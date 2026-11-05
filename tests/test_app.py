import re
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from agent.output_validator import NOTE_AI_UNAVAILABLE, Explanation
from crawler.models import CrawlStatus, NotScanned, SiteData
from findings import Category, Source, Status, finding, unavailable
from orchestrator import AuditResult
from scoring.score_engine import score_findings
from tests.factories import make_page, make_site
from url_validator import InvalidURLError

APP = str(Path(__file__).resolve().parent.parent / "app.py")
URL = "https://example.com/"
TITLE = "keyword.title"
LOCAL = "local.phone"

FINDINGS = (
    finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.FAIL, "Title is missing.", weight=3, page=URL),
    finding("technical.https", Category.TECHNICAL_SEO, Status.PASS, "Site uses HTTPS."),
    unavailable(LOCAL, Category.LOCAL_SEO, "Phone could not be read.", source=Source.CRAWLER),
)
AI = Explanation(
    output={
        "findings": [
            {"check_id": TITLE, "explanation": "Your page has no title.", "why_it_matters": "People see it first.",
             "action": "Write a title."},
            {"check_id": LOCAL, "explanation": "We could not read your phone.", "why_it_matters": "", "action": ""},
        ],
        "top_priorities": [{"check_id": TITLE, "title": "Add a title", "reason": "It is the first thing people see."}],
    },
    ai_generated=True,
)
NOTHING_TO_EXPLAIN = Explanation(output={"findings": [], "top_priorities": []}, ai_generated=True)


def _audit(findings=FINDINGS):
    return AuditResult(
        url=URL,
        site=make_site(make_page(url=URL, title="Example Bakery"),
                       not_scanned=(NotScanned(URL + "menu/", "Timed out"),)),
        findings=tuple(findings),
        scores=score_findings(findings),
    )


BLOCKED = AuditResult(
    url=URL,
    site=SiteData(
        start_url=URL,
        status=CrawlStatus.BLOCKED,
        message="This website does not allow scanning.",
        not_scanned=(NotScanned(URL, "Blocked by the site's robots.txt"),),
    ),
)


class App:
    """The running app, with the audit and AI faked. Everything else is real."""

    def __init__(self, audit=None, explanation=AI, validate_error=None):
        self.audit = audit if audit is not None else _audit()
        self.explanation = explanation
        self.validate_error = validate_error
        self.at = None
        self.run_audit_mock = None
        self.explain_mock = None

    def _run(self, action):
        with (
            patch("url_validator.validate_url", side_effect=self.validate_error, return_value=URL),
            patch("orchestrator.run_audit", return_value=self.audit) as run_audit,
            patch("agent.output_validator.explain_audit", return_value=self.explanation) as explain,
        ):
            self.at = action()
        self.run_audit_mock, self.explain_mock = run_audit, explain
        return self

    def submit(self, url="example.com"):
        def action():
            at = self.at or AppTest.from_file(APP, default_timeout=30).run()
            at.text_input[0].set_value(url)
            at.button[0].click()
            return at.run()

        return self._run(action)

    def rerun(self):
        return self._run(lambda: self.at.run())

    def click(self, label):
        button = next(b for b in self.at.button if b.label == label)
        return self._run(lambda: button.click().run())

    @property
    def text(self):
        """Everything in Markdown on the page, as a reader sees it (escapes removed)."""
        raw = " ".join(item.value for item in [*self.at.markdown, *self.at.caption, *self.at.subheader])
        return re.sub(r"\\([!-/:-@\[-`{-~])", r"\1", raw).replace("\u200b", "")

    @property
    def metrics(self):
        return {metric.label: metric.value for metric in self.at.metric}

    @property
    def expander_labels(self):
        return [item.label for item in self.at.expander]

    @property
    def score_bars(self):
        return [item.proto.text for item in self.at.get("progress")]


def test_landing_page_shows_form_and_no_error():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value.endswith("BizBoost AI")
    assert at.button[0].label == "Start Audit"
    assert not at.error
    assert not at.metric


def test_invalid_url_shows_plain_message_and_does_not_audit():
    app = App(validate_error=InvalidURLError("Bad address.")).submit("not a url")
    assert app.at.error[0].value == "Bad address."
    app.run_audit_mock.assert_not_called()
    assert not app.at.metric


def test_valid_url_runs_the_audit_and_explains_it():
    app = App().submit()
    assert not app.at.exception
    assert not app.at.error
    assert app.run_audit_mock.call_args.args == (URL,)
    findings, scores, context = app.explain_mock.call_args.args
    assert findings == FINDINGS
    assert scores == _audit().scores
    assert context.name == "Example Bakery"
    assert f"Results for {URL}" in app.text


# --- The dashboard ---


def test_shows_overall_and_all_five_category_scores():
    app = App().submit()
    assert app.metrics["Overall score"] == "50 / 100"
    bars = " ".join(app.score_bars)
    assert "**Technical SEO:** 100 / 100" in bars
    assert "**Keyword Optimization:** 0 / 100" in bars
    assert "**Local SEO:** Data unavailable" in app.text
    assert "**Content Quality:** Data unavailable" in app.text
    assert "**Credibility and Backlinks:** Data unavailable" in app.text


def test_nothing_measured_shows_data_unavailable_not_zero():
    app = App(audit=_audit(()), explanation=NOTHING_TO_EXPLAIN).submit()
    assert not app.at.exception
    assert app.metrics["Overall score"] == "Data unavailable"
    assert "0 / 100" not in app.text


def test_top_fixes_show_the_reason_action_and_check():
    app = App().submit()
    assert "1. Add a title" in app.text
    assert "It is the first thing people see." in app.text
    assert "**What to do:** Write a title." in app.text
    assert f"From the check: Title ({TITLE})" in app.text


def test_no_fixes_needed_is_said_plainly():
    passed = [finding("technical.https", Category.TECHNICAL_SEO, Status.PASS, "Site uses HTTPS.")]
    app = App(audit=_audit(passed), explanation=NOTHING_TO_EXPLAIN).submit()
    assert "nothing to fix" in app.at.success[0].value


def test_findings_expand_by_category_with_score_and_counts():
    labels = App().submit().expander_labels
    assert "Keyword Optimization: 0 / 100 (1 to fix)" in labels
    assert "Technical SEO: 100 / 100 (0 to fix)" in labels
    assert "Local SEO: Data unavailable (0 to fix, 1 unavailable)" in labels


def test_finding_shows_explanation_why_action_and_evidence():
    app = App().submit()
    assert "❌ **Title**: Problem" in app.text
    assert "Your page has no title." in app.text
    assert "**Why it matters:** People see it first." in app.text
    assert f"- {URL}: Title is missing." in app.text
    assert f"Check: {TITLE}" in app.text


def test_unavailable_check_is_labelled_and_passed_check_shows_evidence():
    app = App().submit()
    assert "➖ **Phone**: Data unavailable" in app.text
    assert "- Phone could not be read." in app.text
    assert "✅ **Secure connection (HTTPS)**: Passed" in app.text
    assert "- Site uses HTTPS." in app.text


def test_pages_scanned_and_not_scanned_are_listed():
    app = App().submit()
    assert "Pages scanned: 1" in app.expander_labels
    assert "Pages not scanned: 1" in app.expander_labels
    assert f"- {URL}menu/: Timed out" in app.text


def test_no_note_when_the_ai_text_passed():
    assert not App().submit().at.info


def test_rule_based_report_shows_the_note_and_top_fixes():
    from agent.fallback_text import rule_based_output

    fallback = Explanation(rule_based_output(FINDINGS), ai_generated=False, note=NOTE_AI_UNAVAILABLE)
    app = App(explanation=fallback).submit()
    assert app.at.info[0].value == NOTE_AI_UNAVAILABLE
    assert "1. Improve your page titles" in app.text
    assert app.metrics["Overall score"] == "50 / 100"


def test_blocked_site_shows_the_message_and_no_scores_or_ai_call():
    app = App(audit=BLOCKED).submit()
    assert not app.at.exception
    assert app.at.warning[0].value == "This website does not allow scanning."
    assert not app.at.metric
    assert "Pages scanned: 0" in app.expander_labels
    assert "Blocked by the site's robots.txt" in app.text
    app.explain_mock.assert_not_called()


# --- Clicks, which rerun the whole script ---


def test_results_stay_on_screen_after_a_rerun_without_auditing_again():
    app = App().submit()
    app.rerun()
    assert app.metrics["Overall score"] == "50 / 100"
    app.run_audit_mock.assert_not_called()
    app.explain_mock.assert_not_called()


def test_run_another_audit_clears_the_results():
    app = App().submit().click("Run another audit")
    assert not app.at.exception
    assert not app.at.metric
    assert "Results for" not in app.text
    assert [b.label for b in app.at.button] == ["Start Audit"]


def test_a_failed_new_audit_clears_the_old_results():
    app = App().submit()
    app.validate_error = InvalidURLError("Bad address.")
    app.submit("not a url")
    assert app.at.error[0].value == "Bad address."
    assert not app.at.metric
    app.rerun()  # a later click must not bring the old results back
    assert not app.at.metric


def test_a_new_audit_replaces_the_old_results():
    app = App().submit()
    app.audit = _audit([finding("technical.https", Category.TECHNICAL_SEO, Status.PASS, "Site uses HTTPS.")])
    app.explanation = NOTHING_TO_EXPLAIN
    app.submit("other.com")
    assert app.metrics["Overall score"] == "100 / 100"
    assert "Your page has no title." not in app.text


def test_download_button_offers_the_plain_text_report():
    buttons = App().submit().at.get("download_button")
    assert len(buttons) == 1
    assert buttons[0].proto.label == "Download report"


# --- Text from the scanned website ---


def test_website_text_cannot_add_links_images_or_formatting():
    hostile = (
        "[Click to fix](https://evil.example) ![x](https://evil.example/t.png) "
        "<img src=x> **bold** `code` :red[alert] $x^2$ # Heading"
    )
    found = [finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.FAIL, hostile, page=URL)]
    explanation = Explanation(
        output={
            "findings": [{"check_id": TITLE, "explanation": hostile, "why_it_matters": hostile, "action": hostile}],
            "top_priorities": [{"check_id": TITLE, "title": hostile, "reason": hostile}],
        },
        ai_generated=True,
    )
    app = App(audit=_audit(found), explanation=explanation).submit()

    raw = " ".join(item.value for item in app.at.markdown)
    assert hostile in app.text  # the reader still sees the words
    # Each symbol that would make these active must have a backslash in front of it.
    for active in (r"\[Click", r"!\[x", "<img", r"\*bold", "`code", ":red", r"\$x"):
        assert not re.search(rf"(?<!\\){active}", raw), active


def test_bare_addresses_from_a_website_cannot_become_links():
    # Streamlit links these even when escaped, so each pattern must be broken up.
    hostile = "Go to https://evil.example or WWW.evil.example or mail owner@evil.example"
    found = [finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.FAIL, hostile, page=URL)]
    app = App(audit=_audit(found), explanation=NOTHING_TO_EXPLAIN).submit()

    raw = " ".join(item.value for item in app.at.markdown).replace("\\", "")
    assert hostile in app.text
    assert "https://" not in raw
    assert "www." not in raw.lower()
    assert "owner@" not in raw


def test_new_lines_in_website_text_cannot_start_new_markdown_blocks():
    found = [finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.FAIL, "ok\n\n# Big heading\n- item", page=URL)]
    app = App(audit=_audit(found), explanation=NOTHING_TO_EXPLAIN).submit()
    raw = " ".join(item.value for item in app.at.markdown)
    assert "\n# " not in raw
    assert "ok \\# Big heading \\- item" in raw
