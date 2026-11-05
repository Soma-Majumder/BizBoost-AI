"""Google PageSpeed Insights integration (homepage only, 30s timeout).

``fetch_pagespeed_findings(url)`` makes ONE mobile-strategy request for the homepage and
returns Technical SEO findings (source ``pagespeed``). It never raises. On a timeout, a
rate limit, a missing key or any other failure, every speed check comes back
``unavailable`` with a plain reason, so the audit carries on and speed is never scored as
zero or as a failure.

The orchestrator can run this in a thread next to the crawl and pass the result to the
Technical analyzer: ``technical.analyze(site, extra=fetch_pagespeed_findings(url))``.

Checks (thresholds are Google's published Core Web Vitals / Lighthouse bands):
    technical.speed_score   Lighthouse performance score   pass 90+, warn 50-89, fail below 50
    technical.lcp           Largest Contentful Paint       pass <= 2.5 s, warn <= 4 s, fail above
    technical.cls           Cumulative Layout Shift        pass <= 0.1, warn <= 0.25, fail above
    technical.tbt           Total Blocking Time            pass <= 200 ms, warn <= 600 ms, fail above

The API key goes in the ``X-goog-api-key`` header and is never placed in a URL, a log
line or an error message. Only the homepage address is sent.
"""

from __future__ import annotations

import math
import os
from typing import Any

import requests

from findings import Category, Finding, Source, Status, finding, unavailable

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
KEY_ENV_VAR = "PAGESPEED_API_KEY"
STRATEGY = "mobile"
REQUEST_TIMEOUT = (5, 30)  # (connect, read) seconds. The 30s read timeout is the PRD limit.

CATEGORY = Category.TECHNICAL_SEO
SOURCE = Source.PAGESPEED

SPEED_SCORE_ID = "technical.speed_score"
LCP_ID = "technical.lcp"
CLS_ID = "technical.cls"
TBT_ID = "technical.tbt"

# check id -> (weight, what it measures, used in "not checked" messages)
CHECKS: dict[str, tuple[int, str]] = {
    SPEED_SCORE_ID: (3, "mobile speed score"),
    LCP_ID: (2, "main content load time"),
    CLS_ID: (2, "layout stability"),
    TBT_ID: (1, "page responsiveness"),
}

SCORE_PASS_MIN = 90
SCORE_WARN_MIN = 50
LCP_PASS_MAX_S, LCP_WARN_MAX_S = 2.5, 4.0
CLS_PASS_MAX, CLS_WARN_MAX = 0.1, 0.25
TBT_PASS_MAX_MS, TBT_WARN_MAX_MS = 200, 600


def fetch_pagespeed_findings(
    homepage_url: str, api_key: str | None = None, session: Any = None
) -> list[Finding]:
    """Return speed findings for the homepage, or ``unavailable`` for every speed check."""
    key = (api_key if api_key is not None else os.getenv(KEY_ENV_VAR, "")).strip()
    if not key:
        return _all_unavailable("no PageSpeed key is set")
    if not isinstance(homepage_url, str) or not homepage_url.strip():
        return _all_unavailable("the homepage address was unclear")

    try:
        response = (session or requests).get(
            API_URL,
            params={"url": homepage_url, "strategy": STRATEGY, "category": "performance"},
            headers={"X-goog-api-key": key},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        return _all_unavailable("Google PageSpeed took longer than 30 seconds")
    except requests.exceptions.RequestException:
        return _all_unavailable("Google PageSpeed could not be reached")

    status = response.status_code
    if status == 429:
        return _all_unavailable("Google PageSpeed's rate limit was reached")
    if status in (400, 401, 403):
        return _all_unavailable("Google PageSpeed rejected the request or our key")
    if status != 200:
        return _all_unavailable(f"Google PageSpeed returned an error (status {status})")
    try:
        data = response.json()
    except ValueError:
        data = None
    return _findings_from_response(data)


def _all_unavailable(why: str) -> list[Finding]:
    return [
        unavailable(
            check_id, CATEGORY,
            f"The {what} was not checked because {why}.",
            source=SOURCE, weight=weight,
        )
        for check_id, (weight, what) in CHECKS.items()
    ]


def _number(value: Any) -> float | None:
    """A finite number of 0 or more, or None. Booleans and strings are not numbers."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) and value >= 0 else None


def _audit_value(audits: Any, audit_id: str) -> float | None:
    audit = audits.get(audit_id) if isinstance(audits, dict) else None
    return _number(audit.get("numericValue")) if isinstance(audit, dict) else None


def _findings_from_response(data: Any) -> list[Finding]:
    result = data.get("lighthouseResult") if isinstance(data, dict) else None
    if not isinstance(result, dict) or result.get("runtimeError"):
        return _all_unavailable("Google PageSpeed could not test this page")

    audits = result.get("audits")
    categories = result.get("categories")
    perf = categories.get("performance") if isinstance(categories, dict) else None
    raw_score = _number(perf.get("score")) if isinstance(perf, dict) else None

    measured = {
        SPEED_SCORE_ID: _score_finding(raw_score),
        LCP_ID: _lcp_finding(_audit_value(audits, "largest-contentful-paint")),
        CLS_ID: _cls_finding(_audit_value(audits, "cumulative-layout-shift")),
        TBT_ID: _tbt_finding(_audit_value(audits, "total-blocking-time")),
    }
    return [
        item if item is not None else _all_unavailable_one(check_id)
        for check_id, item in measured.items()
    ]


def _all_unavailable_one(check_id: str) -> Finding:
    weight, what = CHECKS[check_id]
    return unavailable(
        check_id, CATEGORY,
        f"The {what} was not checked because Google PageSpeed did not report it.",
        source=SOURCE, weight=weight,
    )


def _make(check_id: str, status: Status, evidence: str) -> Finding:
    return finding(check_id, CATEGORY, status, evidence, source=SOURCE, weight=CHECKS[check_id][0])


def _score_finding(raw: float | None) -> Finding | None:
    if raw is None or raw > 1:
        return None
    score = round(raw * 100)
    if score >= SCORE_PASS_MIN:
        status, note = Status.PASS, "a fast page on mobile"
    elif score >= SCORE_WARN_MIN:
        status, note = Status.WARN, "room to speed up on mobile"
    else:
        status, note = Status.FAIL, "slow on mobile"
    return _make(
        SPEED_SCORE_ID, status,
        f"Google PageSpeed gives the homepage a mobile speed score of {score} out of 100 ({note}).",
    )


def _lcp_finding(milliseconds: float | None) -> Finding | None:
    if milliseconds is None:
        return None
    seconds = milliseconds / 1000
    if seconds <= LCP_PASS_MAX_S:
        status, note = Status.PASS, "good"
    elif seconds <= LCP_WARN_MAX_S:
        status, note = Status.WARN, f"needs improvement, good is {LCP_PASS_MAX_S:g} seconds or less"
    else:
        status, note = Status.FAIL, f"slow, good is {LCP_PASS_MAX_S:g} seconds or less"
    return _make(
        LCP_ID, status,
        f"The main content of the homepage takes {seconds:.1f} seconds to appear on mobile ({note}).",
    )


def _cls_finding(value: float | None) -> Finding | None:
    if value is None:
        return None
    if value <= CLS_PASS_MAX:
        status, note = Status.PASS, "good"
    elif value <= CLS_WARN_MAX:
        status, note = Status.WARN, f"needs improvement, good is {CLS_PASS_MAX:g} or less"
    else:
        status, note = Status.FAIL, f"poor, good is {CLS_PASS_MAX:g} or less"
    return _make(
        CLS_ID, status,
        f"The homepage layout shifts by {value:.2f} while loading on mobile ({note}).",
    )


def _tbt_finding(milliseconds: float | None) -> Finding | None:
    if milliseconds is None:
        return None
    if milliseconds <= TBT_PASS_MAX_MS:
        status, note = Status.PASS, "good"
    elif milliseconds <= TBT_WARN_MAX_MS:
        status, note = Status.WARN, f"needs improvement, good is {TBT_PASS_MAX_MS} ms or less"
    else:
        status, note = Status.FAIL, f"poor, good is {TBT_PASS_MAX_MS} ms or less"
    return _make(
        TBT_ID, status,
        f"The homepage is blocked from responding to taps and clicks for {round(milliseconds)} ms "
        f"while loading on mobile ({note}).",
    )
