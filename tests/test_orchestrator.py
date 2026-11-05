"""Tests for the audit orchestrator. The crawl and both providers are faked, so these
never touch the network. The analyzers and scoring engine are the real ones unless a
test says otherwise."""

import threading

import pytest

import orchestrator
from crawler.models import CrawlStatus, NotScanned, SiteData
from findings import Category, Source, Status, finding
from orchestrator import run_audit
from tests.factories import make_page, make_site

URL = "https://example.com/"
WAIT = 5  # seconds. Only reached if a test is about to fail.

SPEED = [
    finding(
        "technical.speed_score", Category.TECHNICAL_SEO, Status.PASS, "Fast on mobile.",
        source=Source.PAGESPEED, weight=3,
    )
]
LINKS = [
    finding(
        "credibility.backlinks", Category.CREDIBILITY_BACKLINKS, Status.PASS, "18 domains.",
        source=Source.BACKLINK_PROVIDER, weight=2,
    )
]
BLOCKED = SiteData(start_url=URL, status=CrawlStatus.BLOCKED, message="Does not allow scanning.")


class Fakes:
    """What the orchestrator calls, with a record of how it was called."""

    def __init__(self):
        self.site = make_site()
        self.speed = lambda url: SPEED
        self.links = lambda url: LINKS
        self.speed_urls = []
        self.link_urls = []
        self.progress_callback = None

    def crawl(self, url, on_progress=None):
        self.progress_callback = on_progress
        if isinstance(self.site, Exception):
            raise self.site
        return self.site

    def fetch_speed(self, url):
        self.speed_urls.append(url)
        return self.speed(url)

    def fetch_links(self, url):
        self.link_urls.append(url)
        return self.links(url)


@pytest.fixture(autouse=True)
def fakes(monkeypatch):
    fake = Fakes()
    monkeypatch.setattr(orchestrator, "crawl", fake.crawl)
    monkeypatch.setattr(orchestrator, "fetch_pagespeed_findings", fake.fetch_speed)
    monkeypatch.setattr(orchestrator, "fetch_backlink_findings", fake.fetch_links)
    return fake


def _by_id(result, check_id):
    return [item for item in result.findings if item.check_id == check_id]


def _crash(*args, **kwargs):
    raise RuntimeError("secret internal detail")


class SlowCall:
    """A provider call that stays busy until released, and records when it finishes."""

    def __init__(self):
        self.release = threading.Event()
        self.finished = threading.Event()

    def __call__(self, url):
        self.release.wait(WAIT)
        self.finished.set()
        return SPEED


# --- A normal audit ---


def test_full_audit_returns_findings_from_all_five_categories_and_scores():
    result = run_audit(URL)

    assert result.completed
    assert result.url == URL
    assert {item.category for item in result.findings} == set(Category)
    assert result.scores.overall is not None
    assert all(cat.score is not None for cat in result.scores.categories.values())
    assert result.seconds >= 0


def test_provider_findings_reach_their_analyzer_categories_and_the_score():
    result = run_audit(URL)

    assert _by_id(result, "technical.speed_score") == SPEED
    assert _by_id(result, "credibility.backlinks") == LINKS
    assert result.scores.categories["technical_seo"].measured >= 1


def test_each_provider_is_called_once_with_the_right_address(fakes):
    fakes.site = make_site(make_page(url="https://www.example.com/"))
    run_audit(URL)
    assert fakes.speed_urls == [URL]
    assert fakes.link_urls == ["https://www.example.com/"]


def test_progress_callback_goes_to_the_crawl_on_the_calling_thread(fakes, monkeypatch):
    threads = []
    original = fakes.crawl

    def crawl(url, on_progress=None):
        threads.append(threading.current_thread())
        return original(url, on_progress=on_progress)

    monkeypatch.setattr(orchestrator, "crawl", crawl)
    callback = lambda done, total: None
    run_audit(URL, on_progress=callback)
    assert fakes.progress_callback is callback
    assert threads == [threading.current_thread()]


# --- Parallel running ---


def test_crawl_and_pagespeed_overlap(fakes, monkeypatch):
    speed_started = threading.Event()
    crawl_started = threading.Event()
    original = fakes.crawl

    def speed(url):
        speed_started.set()
        assert crawl_started.wait(WAIT), "the crawl never started while PageSpeed was running"
        return SPEED

    def crawl(url, on_progress=None):
        crawl_started.set()
        assert speed_started.wait(WAIT), "PageSpeed never started while the crawl was running"
        return original(url, on_progress=on_progress)

    fakes.speed = speed
    monkeypatch.setattr(orchestrator, "crawl", crawl)
    result = run_audit(URL)
    assert _by_id(result, "technical.speed_score") == SPEED


# --- Blocked and unreachable sites ---


@pytest.mark.parametrize("status", [CrawlStatus.BLOCKED, CrawlStatus.UNREACHABLE])
def test_failed_crawl_stops_the_audit_and_keeps_the_message(fakes, status):
    not_scanned = (NotScanned(URL, "The site refused our request"),)
    fakes.site = SiteData(start_url=URL, status=status, message="Why it stopped.", not_scanned=not_scanned)

    result = run_audit(URL)

    assert not result.completed
    assert result.site.message == "Why it stopped."
    assert result.site.not_scanned == not_scanned
    assert result.findings == ()
    assert result.scores is None


def test_blocked_site_does_not_spend_a_backlink_call(fakes):
    fakes.site = BLOCKED
    run_audit(URL)
    assert fakes.link_urls == []


def test_blocked_site_does_not_wait_for_a_slow_pagespeed_call(fakes):
    slow = SlowCall()
    fakes.site = BLOCKED
    fakes.speed = slow
    try:
        result = run_audit(URL)
        assert not slow.finished.is_set()
        assert not result.completed
    finally:
        slow.release.set()


def test_crawl_crash_becomes_a_plain_message(fakes):
    fakes.site = RuntimeError("secret internal detail")

    result = run_audit(URL)

    assert not result.completed
    assert result.site.status is CrawlStatus.UNREACHABLE
    assert "secret" not in result.site.message
    assert result.site.not_scanned[0].url == URL


# --- Partial failures: only the affected checks become unavailable ---


def test_pagespeed_crash_makes_only_speed_checks_unavailable(fakes):
    fakes.speed = _crash

    result = run_audit(URL)

    assert result.completed
    speed = [item for item in result.findings if item.source is Source.PAGESPEED]
    assert len(speed) == len(orchestrator.pagespeed.CHECKS)
    assert all(item.status is Status.UNAVAILABLE for item in speed)
    assert all("secret" not in item.evidence for item in speed)
    assert result.scores.categories["technical_seo"].score is not None


def test_pagespeed_past_the_deadline_is_unavailable(fakes, monkeypatch):
    slow = SlowCall()
    monkeypatch.setattr(orchestrator, "AUDIT_DEADLINE_SECONDS", 0.0)
    fakes.speed = slow
    try:
        result = run_audit(URL)
        assert not slow.finished.is_set()
    finally:
        slow.release.set()

    item = _by_id(result, "technical.speed_score")[0]
    assert item.status is Status.UNAVAILABLE
    assert "ran out of time" in item.evidence
    assert result.completed


def test_backlink_crash_is_unavailable_and_audit_finishes(fakes):
    fakes.links = _crash

    result = run_audit(URL)

    item = _by_id(result, "credibility.backlinks")[0]
    assert item.status is Status.UNAVAILABLE
    assert item.source is Source.BACKLINK_PROVIDER
    assert "secret" not in item.evidence
    assert result.scores.categories["credibility_backlinks"].score is not None


def test_unavailable_speed_is_dropped_from_the_score_not_counted_as_a_failure(fakes):
    fakes.speed = lambda url: [
        finding(
            "technical.speed_score", Category.TECHNICAL_SEO, Status.FAIL, "Slow on mobile.",
            source=Source.PAGESPEED, weight=3,
        )
    ]
    with_failed_speed = run_audit(URL).scores.categories["technical_seo"]

    fakes.speed = _crash
    with_unknown_speed = run_audit(URL).scores.categories["technical_seo"]

    assert with_unknown_speed.unavailable >= len(orchestrator.pagespeed.CHECKS)
    assert with_unknown_speed.score > with_failed_speed.score


@pytest.mark.parametrize(
    ("module", "category", "check_id"),
    [
        (orchestrator.keyword, Category.KEYWORD_OPTIMIZATION, "keyword.analyzer_error"),
        (orchestrator.content, Category.CONTENT_QUALITY, "content.analyzer_error"),
        (orchestrator.local_seo, Category.LOCAL_SEO, "local.analyzer_error"),
        (orchestrator.technical, Category.TECHNICAL_SEO, "technical.analyzer_error"),
        (orchestrator.credibility, Category.CREDIBILITY_BACKLINKS, "credibility.analyzer_error"),
    ],
)
def test_analyzer_crash_affects_only_its_own_category(monkeypatch, module, category, check_id):
    monkeypatch.setattr(module, "analyze", _crash)

    result = run_audit(URL)

    assert result.completed
    item = _by_id(result, check_id)[0]
    assert item.category is category
    assert item.status is Status.UNAVAILABLE
    assert "secret" not in item.evidence
    others = {c for c in Category if c is not category}
    assert others <= {i.category for i in result.findings if i.status is not Status.UNAVAILABLE}


def test_technical_crash_keeps_the_measured_speed_findings(monkeypatch):
    monkeypatch.setattr(orchestrator.technical, "analyze", _crash)
    result = run_audit(URL)
    assert _by_id(result, "technical.speed_score") == SPEED
    assert result.scores.categories["technical_seo"].score == 100


def test_credibility_crash_keeps_the_measured_backlink_findings(monkeypatch):
    monkeypatch.setattr(orchestrator.credibility, "analyze", _crash)
    result = run_audit(URL)
    assert _by_id(result, "credibility.backlinks") == LINKS


def test_nothing_measured_gives_no_overall_score(monkeypatch, fakes):
    for module in (
        orchestrator.keyword, orchestrator.content, orchestrator.local_seo,
        orchestrator.technical, orchestrator.credibility,
    ):
        monkeypatch.setattr(module, "analyze", _crash)
    fakes.speed = _crash
    fakes.links = _crash

    result = run_audit(URL)

    assert result.completed
    assert result.scores.overall is None
