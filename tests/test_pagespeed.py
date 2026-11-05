import pytest
import requests

from analyzers.technical import analyze as analyze_technical
from findings import Category, Source, Status
from integrations import pagespeed
from integrations.pagespeed import fetch_pagespeed_findings
from scoring.score_engine import score_findings
from tests.factories import make_site

KEY = "AIzaSyTESTKEY1234567890"
IDS = ["technical.speed_score", "technical.lcp", "technical.cls", "technical.tbt"]


class FakeResponse:
    def __init__(self, status=200, payload=None, bad_json=False):
        self.status_code, self._payload, self._bad = status, payload, bad_json

    def json(self):
        if self._bad:
            raise ValueError("not json")
        return self._payload


class FakeSession:
    def __init__(self, outcome):
        self.outcome, self.calls = outcome, []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def payload(score=0.95, lcp_ms=1800, cls=0.02, tbt_ms=80, **result_extra):
    audits = {}
    if lcp_ms is not None:
        audits["largest-contentful-paint"] = {"numericValue": lcp_ms}
    if cls is not None:
        audits["cumulative-layout-shift"] = {"numericValue": cls}
    if tbt_ms is not None:
        audits["total-blocking-time"] = {"numericValue": tbt_ms}
    categories = {"performance": {"score": score}}
    return {"lighthouseResult": {"categories": categories, "audits": audits, **result_extra}}


def run(outcome, url="https://example.com/", key=KEY):
    session = FakeSession(outcome)
    return fetch_pagespeed_findings(url, api_key=key, session=session), session


def by_id(results, check_id):
    return next(f for f in results if f.check_id == check_id)


# --- measured results ----------------------------------------------------------------


def test_fast_site_passes_everything_with_real_numbers():
    results, _ = run(FakeResponse(200, payload()))
    assert [f.check_id for f in results] == IDS
    assert all(f.status is Status.PASS for f in results)
    assert "95 out of 100" in by_id(results, "technical.speed_score").evidence
    assert "1.8 seconds" in by_id(results, "technical.lcp").evidence
    assert "0.02" in by_id(results, "technical.cls").evidence
    assert "80 ms" in by_id(results, "technical.tbt").evidence


def test_findings_follow_the_contract():
    for item in run(FakeResponse(200, payload()))[0]:
        assert item.category is Category.TECHNICAL_SEO
        assert item.source is Source.PAGESPEED
        assert item.page is None and item.weight >= 1


@pytest.mark.parametrize("score, status", [
    (0.90, Status.PASS), (0.89, Status.WARN), (0.50, Status.WARN), (0.49, Status.FAIL), (0.0, Status.FAIL),
])
def test_speed_score_boundaries(score, status):
    assert by_id(run(FakeResponse(200, payload(score=score)))[0], "technical.speed_score").status is status


@pytest.mark.parametrize("ms, status", [
    (2500, Status.PASS), (2501, Status.WARN), (4000, Status.WARN), (4001, Status.FAIL),
])
def test_lcp_boundaries(ms, status):
    assert by_id(run(FakeResponse(200, payload(lcp_ms=ms)))[0], "technical.lcp").status is status


@pytest.mark.parametrize("value, status", [
    (0.1, Status.PASS), (0.11, Status.WARN), (0.25, Status.WARN), (0.26, Status.FAIL),
])
def test_cls_boundaries(value, status):
    assert by_id(run(FakeResponse(200, payload(cls=value)))[0], "technical.cls").status is status


@pytest.mark.parametrize("ms, status", [
    (200, Status.PASS), (201, Status.WARN), (600, Status.WARN), (601, Status.FAIL),
])
def test_tbt_boundaries(ms, status):
    assert by_id(run(FakeResponse(200, payload(tbt_ms=ms)))[0], "technical.tbt").status is status


def test_zero_values_are_measured_not_missing():
    results, _ = run(FakeResponse(200, payload(cls=0, tbt_ms=0)))
    assert by_id(results, "technical.cls").status is Status.PASS
    assert by_id(results, "technical.tbt").status is Status.PASS


# --- unavailable, never zero or fail -------------------------------------------------


@pytest.mark.parametrize("outcome, expected", [
    (requests.exceptions.Timeout(), "longer than 30 seconds"),
    (requests.exceptions.ConnectionError(), "could not be reached"),
    (FakeResponse(429), "rate limit"),
    (FakeResponse(400), "rejected"),
    (FakeResponse(403), "rejected"),
    (FakeResponse(500), "status 500"),
    (FakeResponse(200, bad_json=True), "could not test this page"),
    (FakeResponse(200, ["nope"]), "could not test this page"),
    (FakeResponse(200, {}), "could not test this page"),
    (FakeResponse(200, payload(runtimeError={"code": "FAILED_DOCUMENT_REQUEST"})), "could not test this page"),
])
def test_failures_make_every_speed_check_unavailable_with_a_reason(outcome, expected):
    results, _ = run(outcome)
    assert [f.check_id for f in results] == IDS
    for item in results:
        assert item.status is Status.UNAVAILABLE
        assert expected in item.evidence and item.evidence.endswith(".")


def test_no_key_makes_no_request(monkeypatch):
    monkeypatch.delenv("PAGESPEED_API_KEY", raising=False)
    session = FakeSession(FakeResponse(200, payload()))
    results = fetch_pagespeed_findings("https://example.com/", session=session)
    assert session.calls == []
    assert all(f.status is Status.UNAVAILABLE for f in results)
    assert "no PageSpeed key" in results[0].evidence


def test_key_is_read_from_the_environment(monkeypatch):
    monkeypatch.setenv("PAGESPEED_API_KEY", KEY)
    session = FakeSession(FakeResponse(200, payload()))
    fetch_pagespeed_findings("https://example.com/", session=session)
    assert session.calls[0][1]["headers"] == {"X-goog-api-key": KEY}


def test_blank_homepage_url_makes_no_request():
    results, session = run(FakeResponse(200, payload()), url="  ")
    assert session.calls == [] and all(f.status is Status.UNAVAILABLE for f in results)


@pytest.mark.parametrize("missing", ["lcp_ms", "cls", "tbt_ms"])
def test_a_missing_metric_is_unavailable_and_the_others_still_count(missing):
    results, _ = run(FakeResponse(200, payload(**{missing: None})))
    statuses = [f.status for f in results]
    assert statuses.count(Status.UNAVAILABLE) == 1
    assert statuses.count(Status.PASS) == 3


@pytest.mark.parametrize("bad", [True, "1800", -5, float("nan"), float("inf")])
def test_unreadable_numbers_are_unavailable_not_scored(bad):
    results, _ = run(FakeResponse(200, payload(lcp_ms=bad)))
    assert by_id(results, "technical.lcp").status is Status.UNAVAILABLE


def test_score_outside_zero_to_one_is_unavailable():
    assert by_id(run(FakeResponse(200, payload(score=95)))[0], "technical.speed_score").status is Status.UNAVAILABLE


# --- request shape and secrecy --------------------------------------------------------


def test_one_mobile_request_with_key_only_in_the_header():
    _, session = run(FakeResponse(200, payload()))
    assert len(session.calls) == 1
    url, kwargs = session.calls[0]
    assert url == pagespeed.API_URL and KEY not in url
    assert kwargs["params"] == {"url": "https://example.com/", "strategy": "mobile", "category": "performance"}
    assert KEY not in repr(kwargs["params"])
    assert kwargs["headers"] == {"X-goog-api-key": KEY}
    assert kwargs["timeout"] == pagespeed.REQUEST_TIMEOUT and kwargs["timeout"][1] == 30


def test_key_never_appears_in_findings_even_if_the_error_contains_it():
    error = requests.exceptions.ConnectionError(f"failed: key={KEY}")
    assert KEY not in repr(run(error)[0])
    assert KEY not in repr(run(FakeResponse(200, payload()))[0])


# --- works with the Technical analyzer and scoring ------------------------------------


def test_findings_plug_into_the_technical_analyzer():
    results = analyze_technical(make_site(), extra=run(FakeResponse(200, payload()))[0])
    ids = [f.check_id for f in results]
    assert all(i in ids for i in IDS)
    assert by_id(results, "technical.lcp").source is Source.PAGESPEED


def test_pagespeed_failure_does_not_lower_the_technical_score():
    site = make_site()
    without = score_findings(analyze_technical(site)).categories["technical_seo"].score
    with_failure = score_findings(
        analyze_technical(site, extra=run(requests.exceptions.Timeout())[0])
    ).categories["technical_seo"].score
    assert with_failure == without
