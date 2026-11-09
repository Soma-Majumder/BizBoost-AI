import html
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
SPEED = "technical.speed_score"

FINDINGS = (
    finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.FAIL, "Title is missing.", weight=3, page=URL),
    finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.PASS, "Title is 40 characters.", weight=3, page=URL + "about"),
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
        site=make_site(make_page(url=URL, title="Example Bakery"), make_page(url=URL + "about"),
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

    def open(self):
        return self._run(lambda: AppTest.from_file(APP, default_timeout=30).run())

    def submit(self, url="example.com"):
        if self.at is None:
            self.open()

        def action():
            self.at.text_input[0].set_value(url)
            self.at.button[0].click()
            return self.at.run()

        return self._run(action)

    def rerun(self):
        return self._run(lambda: self.at.run())

    def click(self, label):
        button = next(b for b in self.at.button if b.label == label)
        return self._run(lambda: button.click().run())

    @property
    def raw_html(self):
        return " ".join(item.proto.body for item in self.at.get("html"))

    @property
    def text(self):
        """Everything on the page as a reader sees it: tags removed, escapes undone."""
        markdown = " ".join(item.value for item in [*self.at.markdown, *self.at.caption])
        page_html = html.unescape(re.sub(r"<[^>]+>", " ", self.raw_html))
        return " ".join(f"{markdown} {page_html}".split())

    @property
    def expander_labels(self):
        return [item.label for item in self.at.expander]

    @property
    def showing_results(self):
        return "SEO Health Report" in self.text


# --- Landing ---------------------------------------------------------------------------


def test_landing_page_shows_the_promise_and_the_form():
    app = App().open()
    assert not app.at.exception
    assert "BizBoost AI" in app.text
    assert "in under 2 minutes." in app.text
    assert "Public data only" in app.text
    assert [b.label for b in app.at.button] == ["Start Audit →"]
    assert not app.at.error
    assert not app.showing_results


def test_header_logo_links_home_and_about_faq_are_text_style_menus():
    app = App().open()
    assert '<a class="bb bb-brand" href="./"' in app.raw_html
    assert 'aria-label="BizBoost AI home"' in app.raw_html
    popovers = [p.proto.popover for p in app.at.get("popover")]
    assert [p.label for p in popovers] == ["About", "FAQ"]
    assert all(p.type == "tertiary" for p in popovers)  # text style, not bordered buttons


def test_browser_tab_uses_the_logo_as_its_icon():
    from PIL import Image

    from app import FAVICON

    icon = Image.open(FAVICON)
    assert icon.size == (256, 256)
    assert icon.mode == "RGBA" and icon.getpixel((0, 0))[3] == 0  # see-through corners


def test_headline_keeps_the_dash_with_back():
    assert "website back&nbsp;— <em>" in App().open().raw_html


def test_address_box_and_button_share_one_row_with_no_gap():
    # Their matching height and joined corners are CSS, checked in a browser. This
    # guards the layout they rely on: one row, no gap, inside the keyed container.
    from streamlit.proto.GapSize_pb2 import GapSize

    from app import CSS

    app = App().open()
    assert ".st-key-bb-address" in CSS and ".st-key-bb-header" in CSS
    rows = [
        block for block in app.at.get("flex_container")
        if [child.type for child in block.children.values()] == ["column", "column"]
    ]
    assert len(rows) == 1
    assert rows[0].proto.flex_container.gap_config.gap_size == GapSize.NONE


def test_landing_page_shows_the_street_drawing_and_results_do_not():
    from app import STREET_IMAGE

    assert STREET_IMAGE.exists()
    assert len(App().open().at.get("image")) == 1
    assert len(App().submit().at.get("image")) == 0


def test_invalid_url_shows_plain_message_and_does_not_audit():
    app = App(validate_error=InvalidURLError("Bad address.")).submit("not a url")
    assert app.at.error[0].value == "Bad address."
    app.run_audit_mock.assert_not_called()
    assert not app.showing_results
    assert app.at.text_input[0].value == "not a url"  # still there to correct


def test_valid_url_runs_the_audit_and_explains_it():
    app = App().submit()
    assert not app.at.exception
    assert not app.at.error
    assert app.run_audit_mock.call_args.args == (URL,)
    findings, scores, context = app.explain_mock.call_args.args
    assert findings == FINDINGS
    assert scores == _audit().scores
    assert context.name == "Example Bakery"
    assert "example.com — SEO Health Report" in app.text
    assert "2 pages scanned" in app.text


def test_scanning_steps_show_done_active_and_waiting():
    from app import steps_html

    rendered = steps_html(1)
    states = re.findall(r'class="bb-step ?(\w*)"', rendered)
    assert states == ["done", "active", "", ""]
    assert "Checking the website is safe to scan" in rendered
    assert "Writing your plain-English report" in rendered


# --- Results ---------------------------------------------------------------------------


def test_score_ring_verdict_and_all_five_category_cards():
    app = App().submit()
    assert 'alt="Overall score 75 / 100"' in app.raw_html
    assert "Your site is in good shape" in app.text  # 75 is in the Good range
    for label in ("Technical SEO", "Keyword Optimization", "Content Quality", "Local SEO",
                  "Credibility and Backlinks"):
        assert label in app.text
    assert "Technical SEO 100 Good" in app.text
    assert "Keyword Optimization 50 Needs attention" in app.text  # 50 is below 60


def test_unavailable_category_card_explains_itself():
    app = App().submit()
    assert "Data unavailable" in app.text
    assert "doesn't count against your score" in app.text


def test_nothing_measured_shows_data_unavailable_not_zero():
    app = App(audit=_audit(()), explanation=NOTHING_TO_EXPLAIN).submit()
    assert not app.at.exception
    assert 'alt="Overall score Data unavailable"' in app.raw_html
    assert "couldn't measure enough" in app.text
    assert "0 / 100" not in app.text


def test_top_fixes_show_why_what_evidence_and_check():
    app = App().submit()
    assert "Your top 1 fix" in app.text
    assert "Add a title" in app.text
    assert "Why it matters: It is the first thing people see." in app.text
    assert "What to do: ✅ Write a title." in app.text
    assert "From the check: Title" in app.text
    assert "Evidence Found on 1 of 2 pages: /" in app.text


def test_no_fixes_needed_is_said_plainly():
    passed = [finding("technical.https", Category.TECHNICAL_SEO, Status.PASS, "Site uses HTTPS.")]
    app = App(audit=_audit(passed), explanation=NOTHING_TO_EXPLAIN).submit()
    assert "We found nothing to fix" in app.text


def test_categories_expand_with_score_status_word_and_counts():
    labels = App().submit().expander_labels
    assert "🟢 Technical SEO (Score: 100) — :green[Good] · 0 to fix" in labels
    assert "🔴 Keyword Optimization (Score: 50) — :red[Needs attention] · 1 to fix" in labels
    assert "⚪ Local SEO — Data unavailable" in labels


def test_each_evidence_line_says_which_page_has_the_problem():
    app = App().submit()
    assert f"Problem {URL}: Title is missing." in app.text
    assert f"Passed {URL}about: Title is 40 characters." in app.text


def test_finding_shows_explanation_why_solution_and_check():
    app = App().submit()
    assert "Problem Title" in app.text
    assert "🔍 Your page has no title." in app.text
    assert "💡 People see it first." in app.text
    assert "🛠️ Solution: ✅ Write a title." in app.text
    assert f"Check: {TITLE}" in app.text


def test_unavailable_and_passed_checks_are_labelled():
    app = App().submit()
    assert "Data unavailable Phone" in app.text
    assert "Not checked Phone could not be read." in app.text
    assert "Passed Secure connection (HTTPS)" in app.text


def test_pages_scanned_and_not_scanned_are_listed():
    app = App().submit()
    assert "Pages scanned: 2" in app.expander_labels
    assert "Pages not scanned: 1" in app.expander_labels
    assert f"{URL}menu/: Timed out" in app.text


def test_homepage_speed_shows_data_unavailable_with_the_reason():
    speed = unavailable(SPEED, Category.TECHNICAL_SEO, "No PageSpeed key is set.", source=Source.PAGESPEED, weight=3)
    app = App(audit=_audit((*FINDINGS, speed))).submit()
    assert "Homepage speed Data unavailable · No PageSpeed key is set." in app.text


def test_homepage_speed_shows_the_measured_result():
    speed = finding(SPEED, Category.TECHNICAL_SEO, Status.WARN, "Mobile speed score of 58 out of 100.",
                    source=Source.PAGESPEED, weight=3)
    app = App(audit=_audit((*FINDINGS, speed))).submit()
    assert "Homepage speed Mobile speed score of 58 out of 100." in app.text


def test_no_note_when_the_ai_text_passed():
    assert not App().submit().at.info


def test_rule_based_report_shows_the_note_and_top_fixes():
    from agent.fallback_text import rule_based_output

    fallback = Explanation(rule_based_output(FINDINGS), ai_generated=False, note=NOTE_AI_UNAVAILABLE)
    app = App(explanation=fallback).submit()
    assert app.at.info[0].value == NOTE_AI_UNAVAILABLE
    assert "Improve your page titles" in app.text
    assert 'alt="Overall score 75 / 100"' in app.raw_html


def test_blocked_site_shows_the_message_and_no_scores_or_ai_call():
    app = App(audit=BLOCKED).submit()
    assert not app.at.exception
    assert "We stopped the audit. This website does not allow scanning." in app.text
    assert "Overall score" not in app.raw_html
    assert "Pages scanned: 0" in app.expander_labels
    assert "Blocked by the site's robots.txt" in app.text
    app.explain_mock.assert_not_called()


# --- Clicks, which rerun the whole script ----------------------------------------------


def test_results_stay_on_screen_after_a_rerun_without_auditing_again():
    app = App().submit()
    app.rerun()
    assert 'alt="Overall score 75 / 100"' in app.raw_html
    app.run_audit_mock.assert_not_called()
    app.explain_mock.assert_not_called()


def test_run_a_new_audit_returns_to_the_landing_page_with_the_address_kept():
    app = App().submit("bakery.example").click("Run a new audit")
    assert not app.at.exception
    assert not app.showing_results
    assert [b.label for b in app.at.button] == ["Start Audit →"]
    # The test runner keeps typed values by itself, so check what the app remembers.
    assert app.at.session_state["last_address"] == "bakery.example"
    assert app.at.text_input[0].value == "bakery.example"


def test_a_failed_new_audit_does_not_bring_old_results_back():
    app = App().submit().click("Run a new audit")
    app.validate_error = InvalidURLError("Bad address.")
    app.submit("not a url")
    assert app.at.error[0].value == "Bad address."
    assert not app.showing_results
    app.rerun()
    assert not app.showing_results


def test_a_new_audit_replaces_the_old_results():
    app = App().submit().click("Run a new audit")
    app.audit = _audit([finding("technical.https", Category.TECHNICAL_SEO, Status.PASS, "Site uses HTTPS.")])
    app.explanation = NOTHING_TO_EXPLAIN
    app.submit("other.com")
    assert 'alt="Overall score 100 / 100"' in app.raw_html
    assert "Your page has no title." not in app.text


def test_download_button_offers_the_plain_text_report():
    buttons = App().submit().at.get("download_button")
    assert len(buttons) == 1
    assert buttons[0].proto.label == "Download report"


# --- Text from the scanned website -----------------------------------------------------

HOSTILE = (
    '[Click to fix](https://evil.example) <img src=x onerror=alert(1)> <a href="https://evil.example">x</a> '
    '<b>bold</b> " onmouseover="alert(2)'
)


def test_website_text_cannot_add_html_links_or_images():
    found = [finding(TITLE, Category.KEYWORD_OPTIMIZATION, Status.FAIL, HOSTILE, page=URL)]
    explanation = Explanation(
        output={
            "findings": [{"check_id": TITLE, "explanation": HOSTILE, "why_it_matters": HOSTILE, "action": HOSTILE}],
            "top_priorities": [{"check_id": TITLE, "title": HOSTILE, "reason": HOSTILE}],
        },
        ai_generated=True,
    )
    hostile_audit = AuditResult(
        url=URL,
        site=make_site(make_page(url=URL), not_scanned=(NotScanned(URL + "x", HOSTILE),)),
        findings=tuple(found),
        scores=score_findings(found),
    )
    app = App(audit=hostile_audit, explanation=explanation).submit()

    assert not app.at.exception
    assert "<img src=x" in app.text  # the reader still sees the words
    raw = app.raw_html
    for active in ("<img src=x", "<a href", "<b>bold", 'onmouseover="alert'):
        assert active not in raw, active
    assert "&lt;img src=x" in raw


def test_blocked_message_from_a_website_is_escaped_too():
    site = SiteData(start_url=URL, status=CrawlStatus.BLOCKED, message=HOSTILE)
    app = App(audit=AuditResult(url=URL, site=site)).submit()
    assert "<img src=x" not in app.raw_html
    assert "&lt;img src=x" in app.raw_html


def test_emoji_is_added_only_when_the_text_has_none():
    from app import _with_emoji

    assert _with_emoji("Write a title.", "✅") == "✅ Write a title."
    assert _with_emoji("🛠️ Ask your web person.", "✅") == "🛠️ Ask your web person."
