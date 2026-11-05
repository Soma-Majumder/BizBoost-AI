"""Audit orchestrator: crawl and PageSpeed in parallel, then analyzers, then scoring.

``run_audit(url)`` takes a URL that already passed ``validate_url`` and returns an
``AuditResult``. It never raises for site or provider problems:

    * A blocked or unreachable site stops the audit. ``result.completed`` is False and
      ``result.site.message`` says why in plain language.
    * PageSpeed or the backlink provider failing, or running out of time, makes only those
      checks ``unavailable``. The rest of the audit finishes.
    * An analyzer crashing makes only that category's checks ``unavailable``.

The crawl runs on the caller's thread so ``on_progress`` can safely update Streamlit,
which only accepts updates from its own thread. PageSpeed and backlinks run in workers.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass

from analyzers import content, credibility, keyword, local_seo, technical
from crawler.models import CrawlStatus, NotScanned, SiteData
from crawler.website_crawler import crawl
from findings import Category, Finding, Source, unavailable
from integrations import backlinks as backlink_provider
from integrations import pagespeed
from integrations.backlinks import fetch_backlink_findings
from integrations.pagespeed import fetch_pagespeed_findings
from scoring.score_engine import ScoreReport, score_findings

logger = logging.getLogger(__name__)

# Stop waiting for PageSpeed and backlinks at this point, leaving a margin inside the
# 2-minute target. The crawl limits its own time.
AUDIT_DEADLINE_SECONDS = 110.0

_CRAWL_CRASHED = "Something went wrong while scanning this website. Please try again."


@dataclass(frozen=True)
class AuditResult:
    url: str
    site: SiteData  # status, message, pages scanned and pages not scanned
    findings: tuple[Finding, ...] = ()
    scores: ScoreReport | None = None  # None when the audit stopped early
    seconds: float = 0.0

    @property
    def completed(self) -> bool:
        return self.site.status is CrawlStatus.OK


def run_audit(
    url: str, on_progress: Callable[[int, int], None] | None = None
) -> AuditResult:
    """Run the audit. ``on_progress(done, total)`` is called as pages are scanned."""
    started = time.monotonic()
    deadline = started + AUDIT_DEADLINE_SECONDS
    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="audit")
    try:
        speed_future = executor.submit(fetch_pagespeed_findings, url)
        site = _crawl_site(url, on_progress)
        if site.status is not CrawlStatus.OK:
            return AuditResult(url=url, site=site, seconds=time.monotonic() - started)

        # Backlinks have a daily limit, so spend a call only once the site can be scanned.
        backlink_future = executor.submit(fetch_backlink_findings, site.homepage.url)
        speed = _collect(speed_future, deadline, _speed_unavailable)
        links = _collect(backlink_future, deadline, _backlinks_unavailable)
    finally:
        # Never wait here: a blocked site should not sit on a slow PageSpeed call.
        executor.shutdown(wait=False, cancel_futures=True)

    findings = _run_analyzers(site, speed, links)
    return AuditResult(
        url=url,
        site=site,
        findings=tuple(findings),
        scores=score_findings(findings),
        seconds=time.monotonic() - started,
    )


def _crawl_site(url: str, on_progress: Callable[[int, int], None] | None) -> SiteData:
    try:
        return crawl(url, on_progress=on_progress)
    except Exception:
        logger.exception("Crawl crashed")
        return SiteData(
            start_url=url,
            status=CrawlStatus.UNREACHABLE,
            message=_CRAWL_CRASHED,
            not_scanned=(NotScanned(url, _CRAWL_CRASHED),),
        )


def _collect(
    future: Future, deadline: float, fallback: Callable[[str], list[Finding]]
) -> list[Finding]:
    """The provider's findings, or the fallback if it fails or runs past the deadline."""
    try:
        return future.result(timeout=max(0.0, deadline - time.monotonic()))
    except FutureTimeoutError:
        return fallback("the audit ran out of time")
    except Exception:
        logger.exception("Provider call crashed")
        return fallback("something went wrong while checking")


def _speed_unavailable(why: str) -> list[Finding]:
    return [
        unavailable(
            check_id, pagespeed.CATEGORY, f"The {what} was not checked because {why}.",
            source=pagespeed.SOURCE, weight=weight,
        )
        for check_id, (weight, what) in pagespeed.CHECKS.items()
    ]


def _backlinks_unavailable(why: str) -> list[Finding]:
    return [
        unavailable(
            backlink_provider.BACKLINKS_ID, backlink_provider.CATEGORY,
            f"Inbound backlinks were not checked because {why}.",
            source=backlink_provider.SOURCE, weight=backlink_provider.BACKLINKS_WEIGHT,
        )
    ]


def _run_analyzers(
    site: SiteData, speed: list[Finding], links: list[Finding]
) -> list[Finding]:
    """Run all five. ``extra`` is kept if an analyzer crashes, since it was measured elsewhere."""
    runs = (
        ("keyword", Category.KEYWORD_OPTIMIZATION, lambda: keyword.analyze(site), []),
        ("content", Category.CONTENT_QUALITY, lambda: content.analyze(site), []),
        ("local", Category.LOCAL_SEO, lambda: local_seo.analyze(site), []),
        ("technical", Category.TECHNICAL_SEO, lambda: technical.analyze(site, extra=speed), speed),
        (
            "credibility",
            Category.CREDIBILITY_BACKLINKS,
            lambda: credibility.analyze(site, backlink_findings=links),
            links,
        ),
    )
    findings: list[Finding] = []
    for name, category, analyze, extra in runs:
        try:
            findings += analyze()
        except Exception:
            logger.exception("%s analyzer crashed", name)
            findings += extra
            findings.append(
                unavailable(
                    f"{name}.analyzer_error", category,
                    "These checks could not be completed because of a problem on our side.",
                    source=Source.CRAWLER,
                )
            )
    return findings
