from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from crawler.models import CrawlStatus, NotScanned, SiteData
from findings import Category, Source, Status, finding, unavailable
from orchestrator import AuditResult
from scoring.score_engine import score_findings
from tests.factories import make_site
from url_validator import InvalidURLError

APP = str(Path(__file__).resolve().parent.parent / "app.py")
URL = "https://example.com/"


def _submit(url, side_effect=None, return_value=None, audit=None):
    with (
        patch("url_validator.validate_url", side_effect=side_effect, return_value=return_value),
        patch("orchestrator.run_audit", return_value=audit) as run_audit,
    ):
        at = AppTest.from_file(APP, default_timeout=30).run()
        at.text_input[0].set_value(url)
        at.button[0].click()
        at = at.run()
    at.run_audit_mock = run_audit
    return at


def _metrics(at):
    return {metric.label: metric.value for metric in at.metric}


def _completed_audit(findings=()):
    return AuditResult(
        url=URL,
        site=make_site(not_scanned=(NotScanned(URL + "menu/", "Timed out"),)),
        findings=tuple(findings),
        scores=score_findings(findings),
    )


def test_landing_page_shows_form_and_no_error():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value.endswith("BizBoost AI")
    assert at.button[0].label == "Start Audit"
    assert not at.error


def test_invalid_url_shows_plain_message_and_does_not_audit():
    at = _submit("not a url", side_effect=InvalidURLError("Bad address."))
    assert at.error[0].value == "Bad address."
    at.run_audit_mock.assert_not_called()


def test_valid_url_starts_audit_with_the_validated_address():
    at = _submit("example.com", return_value=URL, audit=_completed_audit())
    assert not at.exception
    assert not at.error
    assert URL in at.success[0].value
    assert at.run_audit_mock.call_args.args == (URL,)


def test_completed_audit_shows_scores_and_pages():
    findings = [
        unavailable("local.nap", Category.LOCAL_SEO, "Not checked.", source=Source.CRAWLER),
        finding("keyword.title", Category.KEYWORD_OPTIMIZATION, Status.PASS, "Good title."),
    ]
    at = _submit("example.com", return_value=URL, audit=_completed_audit(findings))

    metrics = _metrics(at)
    assert not at.exception
    assert metrics["Overall score"] == "100 / 100"
    assert metrics["Keywords"] == "100 / 100"
    assert metrics["Local SEO"] == "Data unavailable"
    page_text = " ".join(item.value for item in at.markdown)
    assert "Pages scanned: 1" in page_text
    assert "Timed out" in page_text
    assert not at.warning


def test_nothing_measured_shows_data_unavailable_not_zero():
    at = _submit("example.com", return_value=URL, audit=_completed_audit())
    assert not at.exception
    assert _metrics(at)["Overall score"] == "Data unavailable"


def test_blocked_site_shows_the_message_and_no_scores():
    site = SiteData(
        start_url=URL,
        status=CrawlStatus.BLOCKED,
        message="This website does not allow scanning.",
        not_scanned=(NotScanned(URL, "Blocked by the site's robots.txt"),),
    )
    at = _submit("example.com", return_value=URL, audit=AuditResult(url=URL, site=site))

    assert not at.exception
    assert at.warning[0].value == "This website does not allow scanning."
    assert not at.metric
    page_text = " ".join(item.value for item in at.markdown)
    assert "Pages scanned: 0" in page_text
    assert "Blocked by the site's robots.txt" in page_text
