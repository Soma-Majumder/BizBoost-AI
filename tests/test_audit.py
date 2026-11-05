"""End-to-end tests: the whole audit, from a typed address to explanations.

The other test files check each piece alone. These check that the pieces work together,
so everything real runs here: the URL validator, crawler, parser, five analyzers, provider
connectors, scoring engine, orchestrator and output validator. Only the network is fake
(DNS, HTTP and the Claude client), so these never touch the internet.
"""

import copy
import json
import socket
from types import SimpleNamespace

import pytest
import requests

from agent.fallback_text import rule_based_output
from agent.output_validator import (
    NOTE_AI_REJECTED,
    NOTE_AI_UNAVAILABLE,
    explain_audit,
    validate_output,
)
from analyzers import local_seo
from crawler.models import CrawlStatus
from findings import Category, Source, Status
from integrations.backlinks import API_URL as BACKLINK_API
from integrations.pagespeed import API_URL as PAGESPEED_API
from integrations.pagespeed import CHECKS as SPEED_CHECKS
from orchestrator import run_audit
from url_validator import InvalidURLError, UnreachableURLError, UnsafeURLError, validate_url

SITE = "https://example.com"
HOME = f"{SITE}/"
PUBLIC_IP = "93.184.216.34"
HTML = "text/html; charset=utf-8"

SENTENCE = (
    "Our family bakery bakes fresh bread and pastries every morning for neighbors across "
    "Brooklyn, using simple ingredients and recipes we are proud to share with you. "
)

def healthy_page(path="/"):
    return HEALTHY_PAGE.replace(f'href="{HOME}"', f'href="{SITE}{path}"')


HEALTHY_PAGE = f"""<!doctype html>
<html lang="en"><head>
  <title>Example Bakery | Fresh Bread in Brooklyn</title>
  <meta name="description" content="Family-run bakery in Brooklyn selling fresh bread, pastries and cakes baked daily. Visit us or order online today.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="canonical" href="{HOME}">
  <script type="application/ld+json">
    {{"@context": "https://schema.org", "@type": "Bakery", "name": "Example Bakery",
      "telephone": "718-555-0100",
      "aggregateRating": {{"@type": "AggregateRating", "ratingValue": 5, "reviewCount": 40}}}}
  </script>
</head><body>
  <h1>Example Bakery</h1>
  <h2>Our bread</h2><p>{SENTENCE * 8}</p>
  <h2>Visit us</h2><p>{SENTENCE * 8}</p>
  <img src="/loaf.jpg" alt="A fresh loaf of bread">
  <a href="/contact">Contact us</a> <a href="/about">About us</a> <a href="/privacy">Privacy policy</a>
  <a href="tel:7185550100">(718) 555-0100</a>
  <address>123 Main St, Brooklyn, NY 11201</address>
  <iframe src="https://www.google.com/maps/embed?pb=1"></iframe>
  <a href="https://www.facebook.com/examplebakery">Facebook</a>
  <a href="https://www.yelp.com/biz/example-bakery">Yelp reviews</a>
</body></html>"""

# Long enough not to look like a JavaScript page, with nothing an SEO audit looks for.
NEGLECTED_PAGE = f"""<html><body><p>{"Welcome here. " * 8}</p>
  <img src="/photo.jpg"><img src="/other.jpg"></body></html>"""

JAVASCRIPT_PAGE = """<html><head><script src="/app.js"></script></head>
  <body><div id="root"></div></body></html>"""


def speed_report(score=0.95, lcp_ms=1200, cls=0.01, tbt_ms=100):
    return {
        "lighthouseResult": {
            "categories": {"performance": {"score": score}},
            "audits": {
                "largest-contentful-paint": {"numericValue": lcp_ms},
                "cumulative-layout-shift": {"numericValue": cls},
                "total-blocking-time": {"numericValue": tbt_ms},
            },
        }
    }


class Response:
    """Stands in for ``requests.Response``."""

    def __init__(self, body="", status=200, content_type=HTML, location=None, data=None):
        self.status_code = status
        self.headers = {"content-type": content_type}
        if location:
            self.headers["location"] = location
        self.is_redirect = bool(location)
        self.body = body.encode("utf-8")
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def iter_content(self, chunk_size=65536):
        yield self.body

    def json(self):
        return self.data


class FakeInternet:
    def __init__(self):
        self.routes = {}  # url -> Response or an exception to raise
        self.dns = {}  # host -> list of IPs. Unlisted hosts are public.
        self.crawled = []  # URLs the crawler requested, in order
        self.requested = []  # every URL anything requested

    def add_page(self, path, body=None, **kwargs):
        self.routes[f"{SITE}{path}"] = Response(healthy_page(path) if body is None else body, **kwargs)

    def add_sitemap(self, *urls):
        locs = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
        self.routes[f"{SITE}/sitemap.xml"] = Response(
            f'<?xml version="1.0"?><urlset>{locs}</urlset>', content_type="application/xml"
        )

    def add_robots(self, text):
        self.routes[f"{SITE}/robots.txt"] = Response(text, content_type="text/plain")

    def _answer(self, url):
        self.requested.append(url)
        result = self.routes.get(url, Response("", status=404))
        if isinstance(result, Exception):
            raise result
        return copy.copy(result)

    def lookup(self, host, port, *args, **kwargs):
        ips = self.dns.get(host, [PUBLIC_IP])
        if not ips:
            raise socket.gaierror("name not found")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0)) for ip in ips]

    def requests_get(self, url, **kwargs):  # the validator and both connectors
        return self._answer(url)

    def session_get(self, url, **kwargs):  # the crawler
        self.crawled.append(url)
        return self._answer(url)


@pytest.fixture(autouse=True)
def internet(monkeypatch):
    fake = FakeInternet()
    monkeypatch.setattr(socket, "getaddrinfo", fake.lookup)
    monkeypatch.setattr(requests, "get", fake.requests_get)
    monkeypatch.setattr(requests.Session, "get", lambda session, url, **kwargs: fake.session_get(url, **kwargs))
    monkeypatch.setattr("crawler.website_crawler.time.sleep", lambda seconds: None)
    for name in ("PAGESPEED_API_KEY", "BACKLINK_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"):
        monkeypatch.delenv(name, raising=False)
    # A complete, healthy site. Tests change the parts they are about.
    fake.add_robots("User-agent: *\nAllow: /")
    fake.add_sitemap(HOME)
    for path in ("/", "/contact", "/about", "/privacy"):
        fake.add_page(path)
    return fake


@pytest.fixture
def with_keys(monkeypatch, internet):
    """Both providers configured and working."""
    monkeypatch.setenv("PAGESPEED_API_KEY", "test-speed-key")
    monkeypatch.setenv("BACKLINK_API_KEY", "test-backlink-key")
    internet.routes[PAGESPEED_API] = Response(data=speed_report())
    internet.routes[BACKLINK_API] = Response(
        data={"referring_domains": 18, "total_links": 40, "backlinks": {"rows": []}}
    )


def audit(address="example.com"):
    return run_audit(validate_url(address))


def findings_for(result, check_id):
    return [item for item in result.findings if item.check_id == check_id]


def status_of(result, check_id):
    """The one status of a check. Fails if the check did not run or is mixed across pages."""
    statuses = {item.status for item in findings_for(result, check_id)}
    assert len(statuses) == 1, f"{check_id}: {statuses or 'did not run'}"
    return statuses.pop()


def test_project_imports():
    import agent, analyzers, crawler, integrations, scoring  # noqa: F401, E401


# --- Validator -------------------------------------------------------------------------


def test_typed_address_goes_all_the_way_to_a_scored_audit():
    result = audit("  EXAMPLE.com ")

    assert result.url == HOME
    assert result.completed
    assert result.site.scanned_urls[0] == HOME
    assert result.scores.overall is not None
    assert {item.category for item in result.findings} == set(Category)


def test_validator_follows_a_redirect_and_the_audit_scans_the_final_site(internet):
    internet.add_page("/", status=301, location="https://www.example.com/")
    internet.routes["https://www.example.com/"] = Response(HEALTHY_PAGE)
    internet.routes["https://www.example.com/robots.txt"] = Response("User-agent: *\nAllow: /", content_type="text/plain")

    result = audit("example.com")

    assert result.url == "https://www.example.com/"
    assert result.site.scanned_urls[0] == "https://www.example.com/"
    assert all("www.example.com" in url for url in result.site.scanned_urls)


@pytest.mark.parametrize(
    "address", ["localhost", "http://localhost:8501", "127.0.0.1", "10.0.0.5", "192.168.1.1", "http://[::1]/"]
)
def test_private_addresses_are_refused_before_anything_connects(internet, address):
    with pytest.raises(UnsafeURLError):
        validate_url(address)
    assert internet.requested == []


def test_public_name_pointing_at_a_private_address_is_refused(internet):
    internet.dns["sneaky.example.com"] = ["10.0.0.5"]
    with pytest.raises(UnsafeURLError):
        validate_url("sneaky.example.com")
    assert internet.requested == []


def test_redirect_to_a_private_address_is_refused_and_never_connected_to(internet):
    internet.add_page("/", status=302, location="http://192.168.1.1/admin")
    with pytest.raises(UnsafeURLError):
        validate_url("https://example.com")
    assert internet.requested == [HOME]


def test_invalid_and_unreachable_addresses_get_their_own_errors(internet):
    with pytest.raises(InvalidURLError):
        validate_url("not a website")
    internet.dns["nowhere.example.com"] = []
    with pytest.raises(UnreachableURLError):
        validate_url("https://nowhere.example.com")


# --- Crawler rules ---------------------------------------------------------------------


def test_robots_txt_blocking_the_site_stops_the_audit_without_scanning(internet):
    internet.add_robots("User-agent: *\nDisallow: /")

    result = audit()

    assert result.site.status is CrawlStatus.BLOCKED
    assert not result.completed
    assert "does not allow scanning" in result.site.message
    assert result.findings == ()
    assert result.scores is None
    assert HOME not in internet.crawled
    assert result.site.not_scanned[0].url == HOME


def test_firewall_refusing_the_crawler_stops_the_audit(internet):
    internet.add_page("/", "", status=403)

    result = audit()

    assert result.site.status is CrawlStatus.BLOCKED
    assert result.scores is None


def test_blocked_site_does_not_use_a_backlink_call(with_keys, internet):
    internet.add_robots("User-agent: *\nDisallow: /")
    audit()
    assert BACKLINK_API not in internet.requested


def test_pages_are_scanned_homepage_then_sitemap_then_homepage_links(internet):
    internet.add_page("/", HEALTHY_PAGE.replace('href="/contact"', 'href="/from-link"'))
    internet.add_sitemap(f"{SITE}/first", f"{SITE}/second")
    for path in ("/first", "/second", "/from-link", "/about", "/privacy"):
        internet.add_page(path)

    scanned = audit().site.scanned_urls

    assert scanned[:3] == (HOME, f"{SITE}/first", f"{SITE}/second")
    assert f"{SITE}/from-link" in scanned[3:]


def test_scan_stops_at_ten_pages(internet):
    urls = [f"{SITE}/page-{n}" for n in range(15)]
    internet.add_sitemap(*urls)
    for n in range(15):
        internet.add_page(f"/page-{n}")

    result = audit()

    assert len(result.site.pages) == 10
    assert result.site.scanned_urls[1:] == tuple(urls[:9])
    assert f"{SITE}/page-9" not in internet.crawled


def test_off_site_duplicate_and_non_page_links_are_not_fetched(internet):
    links = (
        '<a href="/menu">Menu</a> <a href="/menu#lunch">Lunch</a> <a href="/menu/">Again</a> '
        '<a href="https://other.example/">Partner</a> <a href="/menu.pdf">PDF</a>'
    )
    internet.add_page("/", HEALTHY_PAGE.replace("</body>", f"{links}</body>"))
    internet.add_page("/menu")

    audit()

    assert internet.crawled.count(f"{SITE}/menu") == 1
    assert f"{SITE}/menu/" not in internet.crawled
    assert f"{SITE}/menu.pdf" not in internet.crawled
    assert not [url for url in internet.crawled if "other.example" in url]


def test_page_redirecting_to_a_private_address_is_not_scanned_or_connected_to(internet):
    internet.add_sitemap(f"{SITE}/sneaky")
    internet.add_page("/sneaky", status=302, location="http://10.0.0.1/secret")

    result = audit()

    assert result.completed
    assert "http://10.0.0.1/secret" not in internet.requested
    assert [page.url for page in result.site.not_scanned] == [f"{SITE}/sneaky"]


def test_page_that_cannot_be_reached_is_listed_and_not_scored_as_a_failure(internet):
    internet.add_sitemap(f"{SITE}/slow")
    internet.routes[f"{SITE}/slow"] = requests.exceptions.ReadTimeout()

    result = audit()

    assert f"{SITE}/slow" not in result.site.scanned_urls
    assert [page.url for page in result.site.not_scanned] == [f"{SITE}/slow"]
    assert all(item.page != f"{SITE}/slow" for item in result.findings)
    assert status_of(result, "technical.broken_pages") is Status.PASS


def test_page_disallowed_by_robots_txt_is_listed_and_not_fetched(internet):
    internet.add_robots("User-agent: *\nDisallow: /private")
    internet.add_sitemap(f"{SITE}/private/page")
    internet.add_page("/private/page")

    result = audit()

    assert result.completed
    assert f"{SITE}/private/page" not in internet.crawled
    assert "robots" in result.site.not_scanned[0].reason


# --- Each analyzer, on real HTML -------------------------------------------------------

# check -> the status a neglected page should get. A healthy page should pass all of them.
ANALYZER_CHECKS = {
    "keyword.title": Status.FAIL,
    "keyword.meta_description": Status.FAIL,
    "keyword.h1": Status.FAIL,
    "content.word_count": Status.FAIL,
    "content.image_alt": Status.FAIL,
    "local.phone": Status.FAIL,
    "local.address": Status.FAIL,
    "local.map": Status.WARN,
    "technical.viewport": Status.FAIL,
    "technical.canonical": Status.WARN,
    "technical.lang": Status.WARN,
    "credibility.contact_page": Status.FAIL,
    "credibility.about_page": Status.FAIL,
    "credibility.social_profiles": Status.WARN,
    "credibility.reviews": Status.WARN,
}


def test_analyzer_checks_cover_all_five_analyzers():
    assert {check_id.split(".")[0] for check_id in ANALYZER_CHECKS} == {
        "keyword", "content", "local", "technical", "credibility",
    }


@pytest.mark.parametrize("check_id", ANALYZER_CHECKS)
def test_healthy_page_passes_each_analyzer_check(check_id):
    assert status_of(audit(), check_id) is Status.PASS


@pytest.mark.parametrize(("check_id", "expected"), ANALYZER_CHECKS.items())
def test_neglected_page_is_flagged_by_each_analyzer_check(internet, check_id, expected):
    internet.add_page("/", NEGLECTED_PAGE)
    assert status_of(audit(), check_id) is expected


def test_every_finding_carries_evidence_and_a_valid_source():
    for item in audit().findings:
        assert item.evidence.strip()
        assert isinstance(item.source, Source)


@pytest.mark.parametrize(
    "check_id",
    ["keyword.title", "keyword.h1", "content.word_count", "content.image_alt", "technical.viewport",
     "credibility.contact_page"],
)
def test_javascript_page_shows_data_unavailable_rather_than_a_failure(internet, check_id):
    internet.add_page("/", JAVASCRIPT_PAGE)
    assert status_of(audit(), check_id) is Status.UNAVAILABLE


def test_finding_names_the_page_it_was_found_on(internet):
    internet.add_page("/", HEALTHY_PAGE)
    internet.add_sitemap(f"{SITE}/thin")
    internet.add_page("/thin", NEGLECTED_PAGE)

    result = audit()

    by_page = {item.page: item.status for item in findings_for(result, "keyword.title")}
    assert by_page[HOME] is Status.PASS
    assert by_page[f"{SITE}/thin"] is Status.FAIL


# --- Providers and the scoring rescale -------------------------------------------------


# The PRD's numbers (A10), written out here on purpose. Importing them from the scoring
# engine would make these tests agree with any mistake made there.
PRD_POINTS = {Status.PASS: 1.0, Status.WARN: 0.5, Status.FAIL: 0.0}
PRD_WEIGHTS = {
    Category.TECHNICAL_SEO: 25,
    Category.KEYWORD_OPTIMIZATION: 25,
    Category.CONTENT_QUALITY: 20,
    Category.LOCAL_SEO: 20,
    Category.CREDIBILITY_BACKLINKS: 10,
}


def expected_category_score(result, category):
    """The PRD's formula, worked out here independently of the scoring engine."""
    measured = [
        item for item in result.findings
        if item.category is category and item.status is not Status.UNAVAILABLE
    ]
    if not measured:
        return None
    earned = sum(item.weight * PRD_POINTS[item.status] for item in measured)
    return 100 * earned / sum(item.weight for item in measured)


def expected_overall(result):
    scores = {cat: expected_category_score(result, cat) for cat in PRD_WEIGHTS}
    scored = {cat: score for cat, score in scores.items() if score is not None}
    total_weight = sum(PRD_WEIGHTS[cat] for cat in scored)
    return sum(score * PRD_WEIGHTS[cat] for cat, score in scored.items()) / total_weight


def test_all_scores_match_the_prd_formula_on_a_full_audit(with_keys, internet):
    internet.add_page("/", NEGLECTED_PAGE)

    result = audit()

    assert result.scores.overall == pytest.approx(expected_overall(result))
    for category in Category:
        assert result.scores.categories[category.value].score == pytest.approx(
            expected_category_score(result, category)
        )


def test_provider_results_reach_their_categories_and_the_score(with_keys):
    result = audit()

    assert status_of(result, "technical.speed_score") is Status.PASS
    assert status_of(result, "credibility.backlinks") is Status.PASS
    assert {item.source for item in result.findings} == set(Source)
    assert result.scores.categories["technical_seo"].unavailable == 0


def test_only_the_homepage_is_sent_to_pagespeed(with_keys, internet):
    internet.add_sitemap(f"{SITE}/menu")
    internet.add_page("/menu")
    audit()
    assert internet.requested.count(PAGESPEED_API) == 1


def test_missing_keys_are_dropped_from_the_score_and_never_count_as_zero():
    without_keys = audit()

    technical = without_keys.scores.categories["technical_seo"]
    assert technical.unavailable == len(SPEED_CHECKS)
    assert status_of(without_keys, "credibility.backlinks") is Status.UNAVAILABLE
    assert technical.score == pytest.approx(expected_category_score(without_keys, Category.TECHNICAL_SEO))
    assert technical.score == 100  # the healthy page's remaining checks all pass


def test_a_slow_site_scores_lower_than_one_we_could_not_measure(monkeypatch, internet):
    unmeasured = audit().scores.categories["technical_seo"].score

    monkeypatch.setenv("PAGESPEED_API_KEY", "test-speed-key")
    internet.routes[PAGESPEED_API] = Response(
        data=speed_report(score=0.2, lcp_ms=9000, cls=0.9, tbt_ms=3000)
    )
    slow = audit()

    assert status_of(slow, "technical.speed_score") is Status.FAIL
    assert slow.scores.categories["technical_seo"].score < unmeasured


@pytest.mark.parametrize(
    ("failure", "reason"),
    [
        (requests.exceptions.ReadTimeout(), "longer than 30 seconds"),
        (requests.exceptions.ConnectionError(), "could not be reached"),
        (Response(status=429), "rate limit"),
        (Response(status=500), "status 500"),
        (Response(data={"not": "a report"}), "could not test this page"),
    ],
)
def test_pagespeed_failure_keeps_the_audit_going_and_says_why(monkeypatch, internet, failure, reason):
    monkeypatch.setenv("PAGESPEED_API_KEY", "test-speed-key")
    internet.routes[PAGESPEED_API] = failure

    result = audit()

    assert result.completed
    speed = [item for item in result.findings if item.source is Source.PAGESPEED]
    assert len(speed) == len(SPEED_CHECKS)
    assert all(item.status is Status.UNAVAILABLE and reason in item.evidence for item in speed)
    assert result.scores.categories["technical_seo"].score == 100


@pytest.mark.parametrize(
    ("failure", "reason"),
    [
        (requests.exceptions.ReadTimeout(), "took too long"),
        (Response(status=401), "rejected our key"),
        (Response(status=429), "daily limit"),
    ],
)
def test_backlink_failure_shows_unavailable_and_says_why(monkeypatch, internet, failure, reason):
    monkeypatch.setenv("BACKLINK_API_KEY", "test-backlink-key")
    internet.routes[BACKLINK_API] = failure

    result = audit()

    assert result.completed
    assert status_of(result, "credibility.backlinks") is Status.UNAVAILABLE
    assert reason in findings_for(result, "credibility.backlinks")[0].evidence
    assert result.scores.categories["credibility_backlinks"].score == pytest.approx(
        expected_category_score(result, Category.CREDIBILITY_BACKLINKS)
    )


def test_category_with_nothing_measured_is_left_out_and_the_rest_rescale_to_100(monkeypatch, internet):
    def crash(*args, **kwargs):
        raise RuntimeError("analyzer bug")

    internet.add_page("/", NEGLECTED_PAGE)
    monkeypatch.setattr(local_seo, "analyze", crash)

    result = audit()
    local = result.scores.categories["local_seo"]

    assert result.completed
    assert local.score is None
    assert local.effective_weight == 0
    effective = [cat.effective_weight for cat in result.scores.categories.values()]
    assert sum(effective) == pytest.approx(100)
    assert result.scores.categories["technical_seo"].effective_weight == pytest.approx(100 * 25 / 80)
    assert result.scores.overall == pytest.approx(expected_overall(result))


def test_javascript_page_is_not_penalized_for_what_could_not_be_read(internet):
    internet.add_page("/", JAVASCRIPT_PAGE)
    javascript_score = audit().scores.categories["keyword_optimization"]
    internet.add_page("/", NEGLECTED_PAGE)
    neglected_score = audit().scores.categories["keyword_optimization"]

    assert javascript_score.unavailable > 0
    assert javascript_score.score is None or javascript_score.score > neglected_score.score


# --- Output validator on real findings -------------------------------------------------


class FakeClaude:
    """Answers each request with the next item, and records what it was asked."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.messages = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **request):
        self.messages.append(request["messages"][0]["content"])
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        text = SimpleNamespace(type="text", text=json.dumps(answer))
        return SimpleNamespace(stop_reason="end_turn", content=[text])


@pytest.fixture
def neglected_audit(internet):
    """A real audit with problems and unavailable checks, so there is plenty to explain."""
    internet.add_page("/", NEGLECTED_PAGE)
    return audit()


def good_answer(result):
    """A correct answer for these exact findings."""
    return copy.deepcopy(rule_based_output(result.findings))


def with_invented_number(result):
    answer = good_answer(result)
    next(e for e in answer["findings"] if e["action"])["why_it_matters"] = "You will get 40% more visitors."
    return answer


def with_invented_check(result):
    answer = good_answer(result)
    answer["findings"].append(
        {"check_id": "technical.made_up", "explanation": "x", "why_it_matters": "y", "action": "z"}
    )
    return answer


def with_missing_citation(result):
    answer = good_answer(result)
    del answer["top_priorities"][0]["check_id"]
    return answer


def with_comment_on_unavailable(result):
    answer = good_answer(result)
    entry = next(e for e in answer["findings"] if not e["action"])
    entry["action"] = "Speed up your site."
    return answer


BAD_ANSWERS = {
    "invented number": (with_invented_number, "40"),
    "invented check": (with_invented_check, "technical.made_up"),
    "missing citation": (with_missing_citation, "no check_id"),
    "comment on unavailable": (with_comment_on_unavailable, "could not be measured"),
}


def test_good_ai_answer_is_used_as_is(neglected_audit):
    answer = good_answer(neglected_audit)
    client = FakeClaude(answer)

    result = explain_audit(neglected_audit.findings, neglected_audit.scores, client=client)

    assert result.ai_generated is True
    assert result.output == answer
    assert result.note is None
    assert len(client.messages) == 1


def test_claude_receives_the_evidence_and_scores_but_no_page_html(neglected_audit):
    client = FakeClaude(good_answer(neglected_audit))

    explain_audit(neglected_audit.findings, neglected_audit.scores, client=client)

    assert "keyword.title" in client.messages[0]
    assert "overall" in client.messages[0]
    assert "<html" not in client.messages[0].lower()
    assert "<img" not in client.messages[0].lower()


@pytest.mark.parametrize("kind", BAD_ANSWERS)
def test_bad_ai_answer_is_rejected_and_retried_with_the_reason(neglected_audit, kind):
    make_bad, reason = BAD_ANSWERS[kind]
    good = good_answer(neglected_audit)
    client = FakeClaude(make_bad(neglected_audit), good)

    result = explain_audit(neglected_audit.findings, neglected_audit.scores, client=client)

    assert result.ai_generated is True
    assert result.output == good
    assert len(client.messages) == 2
    assert "rejected" not in client.messages[0]
    assert "rejected" in client.messages[1] and reason in client.messages[1]


@pytest.mark.parametrize("kind", BAD_ANSWERS)
def test_bad_ai_answer_twice_falls_back_to_rule_based_text(neglected_audit, kind):
    make_bad, _ = BAD_ANSWERS[kind]
    client = FakeClaude(make_bad(neglected_audit), make_bad(neglected_audit), good_answer(neglected_audit))

    result = explain_audit(neglected_audit.findings, neglected_audit.scores, client=client)

    assert result.ai_generated is False
    assert result.note == NOTE_AI_REJECTED
    assert result.output == rule_based_output(neglected_audit.findings)
    assert len(client.messages) == 2


def test_no_api_key_shows_rule_based_text_with_a_note(neglected_audit):
    result = explain_audit(neglected_audit.findings, neglected_audit.scores)

    assert result.ai_generated is False
    assert result.note == NOTE_AI_UNAVAILABLE
    assert result.output["top_priorities"]


def test_claude_being_down_shows_rule_based_text_without_a_retry(neglected_audit):
    client = FakeClaude(RuntimeError("service down"), good_answer(neglected_audit))

    result = explain_audit(neglected_audit.findings, neglected_audit.scores, client=client)

    assert result.ai_generated is False
    assert result.note == NOTE_AI_UNAVAILABLE
    assert len(client.messages) == 1


@pytest.mark.parametrize("page", [HEALTHY_PAGE, NEGLECTED_PAGE, JAVASCRIPT_PAGE])
def test_rule_based_text_always_passes_the_validator(internet, page):
    internet.add_page("/", page)
    result = audit()
    assert validate_output(rule_based_output(result.findings), result.findings) == []


def test_rule_based_report_has_prioritized_fixes_when_there_are_problems(neglected_audit):
    # The PRD's success metric: every report has at least 3 prioritized recommendations.
    fixes = rule_based_output(neglected_audit.findings)["top_priorities"]
    assert len(fixes) == 3
    assert all(fix["check_id"] and fix["title"] and fix["reason"] for fix in fixes)
    statuses = {item.check_id: item.status for item in neglected_audit.findings}
    assert all(statuses[fix["check_id"]] in (Status.FAIL, Status.WARN) for fix in fixes)
