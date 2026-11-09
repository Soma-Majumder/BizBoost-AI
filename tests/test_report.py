"""Tests for the report generator. No network, no Streamlit."""

import pytest

from agent.fallback_text import rule_based_output
from agent.output_validator import NOTE_AI_UNAVAILABLE, Explanation
from crawler.models import CrawlStatus, NotScanned, SiteData
from findings import Category, Source, finding, unavailable
from orchestrator import AuditResult
from report import (
    CATEGORY_LABELS,
    build_report,
    check_name,
    score_text,
    to_text,
)
from scoring.score_engine import score_findings
from tests.factories import make_page, make_site
from findings import Status

URL = "https://example.com/"
META = "keyword.meta_description"
TITLE = "keyword.title"
LCP = "technical.lcp"
HTTPS = "technical.https"

FINDINGS = (
    finding(TITLE, Category.KEYWORD_OPTIMIZATION, "warn", "Title is short.", weight=2, page=URL),
    finding(META, Category.KEYWORD_OPTIMIZATION, "fail", "Description is missing.", weight=3, page=URL),
    finding(META, Category.KEYWORD_OPTIMIZATION, "pass", "Description is fine.", weight=3, page=URL + "x"),
    finding(HTTPS, Category.TECHNICAL_SEO, "pass", "Site uses HTTPS."),
    unavailable(LCP, Category.TECHNICAL_SEO, "PageSpeed timed out.", source=Source.PAGESPEED, weight=2),
)

AI_OUTPUT = {
    "findings": [
        {"check_id": TITLE, "explanation": "AI title text.", "why_it_matters": "W1.", "action": "A1."},
        {"check_id": META, "explanation": "AI meta text.", "why_it_matters": "W2.", "action": "A2."},
        {"check_id": LCP, "explanation": "AI could not check.", "why_it_matters": "", "action": ""},
    ],
    "top_priorities": [
        {"check_id": META, "title": "Add a description", "reason": "Reason two."},
        {"check_id": TITLE, "title": "Lengthen your title", "reason": "Reason one."},
    ],
}
AI = Explanation(output=AI_OUTPUT, ai_generated=True)
RULE_BASED = Explanation(output=rule_based_output(FINDINGS), ai_generated=False, note=NOTE_AI_UNAVAILABLE)


def audit(findings=FINDINGS, **site_overrides):
    return AuditResult(
        url=URL,
        site=make_site(make_page(url=URL), make_page(url=URL + "x"), **site_overrides),
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


def category(report, key):
    return next(c for c in report.categories if c.key == key)


def check(report, check_id):
    return next(c for cat in report.categories for c in cat.checks if c.check_id == check_id)


# --- Scores ---


def test_overall_and_all_five_category_scores_are_present():
    report = build_report(audit(), AI)
    scores = score_findings(FINDINGS)
    assert report.overall == scores.overall
    assert {c.key for c in report.categories} == set(CATEGORY_LABELS)
    assert len(report.categories) == 5
    assert category(report, "technical_seo").score == scores.categories["technical_seo"].score


def test_category_with_nothing_measured_has_no_score_rather_than_zero():
    report = build_report(audit(), AI)
    assert category(report, "local_seo").score is None
    assert score_text(None) == "Data unavailable"


@pytest.mark.parametrize(("score", "text"), [(0, "0 / 100"), (61.6, "62 / 100"), (100, "100 / 100")])
def test_score_text(score, text):
    assert score_text(score) == text


# --- Checks and evidence ---


def test_ai_text_is_matched_to_its_check():
    item = check(build_report(audit(), AI), TITLE)
    assert item.explanation == "AI title text."
    assert item.why_it_matters == "W1."
    assert item.action == "A1."


def test_a_check_on_several_pages_is_one_item_with_all_its_evidence_and_pages():
    report = build_report(audit(), AI)
    assert [c.check_id for c in category(report, "keyword_optimization").checks].count(META) == 1
    assert check(report, META).evidence == (
        f"{URL}: Description is missing.",
        f"{URL}x: Description is fine.",
    )


def test_page_is_not_repeated_when_the_evidence_already_names_it():
    found = [finding("a.b", Category.CONTENT_QUALITY, "fail", f"{URL} has no text.", page=URL)]
    assert check(build_report(audit(found), None), "a.b").evidence == (f"{URL} has no text.",)


def test_repeated_evidence_is_shown_once():
    found = [finding("a.b", Category.CONTENT_QUALITY, "fail", "No sitemap.") for _ in range(2)]
    assert check(build_report(audit(found), None), "a.b").evidence == ("No sitemap.",)


def test_worst_status_decides_how_a_check_is_shown():
    assert check(build_report(audit(), AI), META).status is Status.FAIL


def test_unavailable_outranks_passed_on_a_mixed_check():
    found = [
        finding("a.b", Category.CONTENT_QUALITY, "pass", "Fine.", page=URL),
        unavailable("a.b", Category.CONTENT_QUALITY, "Built with JavaScript.", page=URL + "x"),
    ]
    item = check(build_report(audit(found), None), "a.b")
    assert item.status is Status.UNAVAILABLE
    assert item.status_label == "Data unavailable"


def test_problems_are_listed_first_then_by_weight():
    found = [
        finding("a.pass", Category.CONTENT_QUALITY, "pass", "x", weight=9),
        unavailable("a.none", Category.CONTENT_QUALITY, "x", weight=9),
        finding("a.warn", Category.CONTENT_QUALITY, "warn", "x", weight=9),
        finding("a.light", Category.CONTENT_QUALITY, "fail", "x", weight=1),
        finding("a.heavy", Category.CONTENT_QUALITY, "fail", "x", weight=5),
    ]
    checks = category(build_report(audit(found), None), "content_quality").checks
    assert [c.check_id for c in checks] == ["a.heavy", "a.light", "a.warn", "a.none", "a.pass"]


def test_category_sorts_checks_into_groups():
    technical = category(build_report(audit(), AI), "technical_seo")
    assert [c.check_id for c in technical.unavailable] == [LCP]
    assert [c.check_id for c in technical.passed] == [HTTPS]
    assert technical.to_fix == ()


def test_passed_check_has_evidence_but_no_advice():
    item = check(build_report(audit(), AI), HTTPS)
    assert item.evidence == ("Site uses HTTPS.",)
    assert (item.explanation, item.why_it_matters, item.action) == ("", "", "")


def test_unavailable_check_has_a_label_and_no_advice():
    item = check(build_report(audit(), RULE_BASED), LCP)
    assert item.status_label == "Data unavailable"
    assert (item.why_it_matters, item.action) == ("", "")
    assert item.evidence == ("PageSpeed timed out.",)


@pytest.mark.parametrize(
    ("check_id", "name"),
    [
        ("keyword.meta_description", "Meta description"),
        ("keyword.h1", "Main heading"),
        ("technical.cls", "Layout stability"),
        ("technical.lcp", "Main content load time"),
        ("technical.tbt", "Page responsiveness"),
        ("local.analyzer_error", "These checks"),
        ("nodot", "Nodot"),
    ],
)
def test_check_names_are_plain_language(check_id, name):
    assert check_name(check_id) == name


# --- Top fixes ---


def test_top_fixes_keep_their_order_and_include_the_action_and_check():
    fixes = build_report(audit(), AI).top_fixes
    assert [f.check_id for f in fixes] == [META, TITLE]
    assert fixes[0].title == "Add a description"
    assert fixes[0].reason == "Reason two."
    assert fixes[0].action == "A2."
    assert fixes[0].name == "Meta description"


def test_rule_based_report_has_top_fixes_a_note_and_advice():
    report = build_report(audit(), RULE_BASED)
    assert report.ai_generated is False
    assert report.note == NOTE_AI_UNAVAILABLE
    assert report.top_fixes
    assert all(fix.title and fix.reason and fix.action for fix in report.top_fixes)
    assert check(report, META).action


def test_rule_based_report_does_not_repeat_the_evidence_as_an_explanation():
    assert check(build_report(audit(), RULE_BASED), META).explanation == ""


def test_ai_report_has_no_note():
    report = build_report(audit(), AI)
    assert report.ai_generated is True
    assert report.note is None


# --- Pages and stopped audits ---


def test_pages_scanned_and_not_scanned_are_listed():
    report = build_report(audit(not_scanned=(NotScanned(URL + "y", "Timed out"),)), AI)
    assert report.pages_scanned == (URL, URL + "x")
    assert [(p.url, p.reason) for p in report.pages_not_scanned] == [(URL + "y", "Timed out")]


def test_stopped_audit_has_the_message_and_no_scores():
    report = build_report(BLOCKED)
    assert report.completed is False
    assert report.message == "This website does not allow scanning."
    assert report.overall is None
    assert report.categories == ()
    assert report.top_fixes == ()
    assert report.pages_scanned == ()
    assert report.pages_not_scanned[0].reason == "Blocked by the site's robots.txt"


def test_seconds_are_kept():
    assert build_report(audit(), AI, seconds=12.5).seconds == 12.5


# --- Plain-text report ---


def test_text_report_has_everything_a_reader_needs():
    text = to_text(build_report(audit(not_scanned=(NotScanned(URL + "y", "Timed out"),)), AI))
    for expected in [
        URL,
        f"Overall score: {score_text(score_findings(FINDINGS).overall)}",
        "Local SEO: Data unavailable",
        "1. Add a description",
        "2. Lengthen your title",
        "What to do: A2.",
        f"Check: {META}",
        "What we found: AI meta text.",
        "Why it matters: W2.",
        f"Evidence: [Problem] {URL}: Description is missing.",
        f"Evidence: [Passed] {URL}x: Description is fine.",
        "[Data unavailable] Main content load time",
        "[Passed] Secure connection (HTTPS)",
        "PAGES SCANNED: 2",
        f"{URL}y: Timed out",
    ]:
        assert expected in text


def test_text_report_includes_the_rule_based_note():
    assert NOTE_AI_UNAVAILABLE in to_text(build_report(audit(), RULE_BASED))


def test_text_report_for_a_stopped_audit():
    text = to_text(build_report(BLOCKED))
    assert "This website does not allow scanning." in text
    assert "Blocked by the site's robots.txt" in text
    assert "Overall score" not in text
    assert "TOP FIXES" not in text


def test_text_report_marks_nothing_measured_as_unavailable_not_zero():
    text = to_text(build_report(audit(()), Explanation({"findings": [], "top_priorities": []}, True)))
    assert "Overall score: Data unavailable" in text
    assert "0 / 100" not in text


# --- What the redesigned results page needs ---------------------------------------------

from datetime import date

from report import (
    GOOD,
    NEEDS_ATTENTION,
    NEEDS_WORK,
    VERDICTS,
    evidence_summary,
    score_band,
)


@pytest.mark.parametrize(
    ("score", "band"),
    [
        (100, GOOD), (75, GOOD), (74.6, GOOD),  # shown as 75, so it must say Good
        (74.5, NEEDS_WORK),  # Python shows 74.5 as 74, and the label must match
        (74.4, NEEDS_WORK), (60, NEEDS_WORK), (59.5, NEEDS_WORK),
        (59.4, NEEDS_ATTENTION), (0, NEEDS_ATTENTION),
        (None, "Data unavailable"),
    ],
)
def test_score_band_matches_the_number_shown(score, band):
    assert score_band(score) == band


def test_verdict_follows_the_overall_band_and_makes_no_claims():
    report = build_report(audit(), AI)
    assert report.verdict == VERDICTS[report.band]
    for sentence in VERDICTS.values():
        assert "Google" not in sentence and "customers" not in sentence


def test_nothing_measured_gets_its_own_verdict():
    report = build_report(audit(()), Explanation({"findings": [], "top_priorities": []}, True))
    assert report.band == "Data unavailable"
    assert "couldn't measure" in report.verdict


def test_each_evidence_line_says_whether_that_page_has_the_problem():
    lines = check(build_report(audit(), AI), META).evidence_lines
    assert [(line.label, line.text) for line in lines] == [
        ("Problem", f"{URL}: Description is missing."),
        ("Passed", f"{URL}x: Description is fine."),
    ]


def test_unavailable_evidence_line_is_labelled_not_checked():
    line = check(build_report(audit(), AI), LCP).evidence_lines[0]
    assert line.label == "Not checked"


def test_top_fix_evidence_counts_the_pages_with_the_problem():
    pages = [f"{URL}{p}" for p in ("", "menu", "about", "gallery")]
    found = [
        finding(META, Category.KEYWORD_OPTIMIZATION, "fail", "Missing.", page=pages[1]),
        finding(META, Category.KEYWORD_OPTIMIZATION, "fail", "Missing.", page=pages[2]),
        finding(META, Category.KEYWORD_OPTIMIZATION, "warn", "Too short.", page=pages[3]),
        finding(META, Category.KEYWORD_OPTIMIZATION, "pass", "Fine.", page=pages[0]),
        unavailable(META, Category.KEYWORD_OPTIMIZATION, "Built with JavaScript.", page=f"{URL}js"),
    ]
    assert evidence_summary(found) == "Found on 3 of 4 pages we could check: /menu, /about…"


def test_top_fix_evidence_says_pages_when_every_page_was_checked():
    found = [
        finding(META, Category.KEYWORD_OPTIMIZATION, "fail", "Missing.", page=f"{URL}menu"),
        finding(META, Category.KEYWORD_OPTIMIZATION, "pass", "Fine.", page=URL),
    ]
    assert evidence_summary(found) == "Found on 1 of 2 pages: /menu"


def test_top_fix_evidence_without_pages_uses_the_scanner_text_shortened():
    found = [finding("technical.sitemap", Category.TECHNICAL_SEO, "fail", "No XML sitemap was found.")]
    assert evidence_summary(found) == "No XML sitemap was found."
    long = [finding("a.b", Category.TECHNICAL_SEO, "fail", "word " * 40)]
    summary = evidence_summary(long)
    assert len(summary) <= 90 and summary.endswith("…")


def test_top_fix_evidence_on_a_single_page_uses_the_scanner_text():
    found = [finding(META, Category.KEYWORD_OPTIMIZATION, "fail", "Missing.", page=URL)]
    assert evidence_summary(found) == "Missing."


def test_top_fix_evidence_is_empty_when_nothing_failed():
    assert evidence_summary([finding(HTTPS, Category.TECHNICAL_SEO, "pass", "Fine.")]) == ""


def test_top_fixes_carry_their_evidence_summary():
    fixes = build_report(audit(), AI).top_fixes
    assert fixes[0].evidence == "Found on 1 of 2 pages: /"  # one page has it, one passed


def test_speed_check_is_found_or_absent():
    assert build_report(audit(), AI).speed is None
    speed = unavailable("technical.speed_score", Category.TECHNICAL_SEO, "No PageSpeed key is set.",
                        source=Source.PAGESPEED, weight=3)
    report = build_report(audit((*FINDINGS, speed)), AI)
    assert report.speed.status is Status.UNAVAILABLE
    assert report.speed.evidence == ("No PageSpeed key is set.",)


def test_report_records_the_scan_date():
    assert build_report(audit(), AI).scanned_on == date.today()


def test_text_report_includes_bands_verdict_and_top_fix_evidence():
    text = to_text(build_report(audit(), AI))
    report = build_report(audit(), AI)
    assert f"Overall score: {score_text(report.overall)} ({report.band})" in text
    assert report.verdict in text
    assert "   Evidence: Found on 1 of 2 pages: /" in text
