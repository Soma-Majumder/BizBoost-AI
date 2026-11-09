"""Tests for the output validator, the retry flow and the rule-based fallback.

The AI is faked, so these never touch the network. The analyzers are real where a test
needs realistic findings.
"""

import json
import re
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent import output_validator
from agent.fallback_text import CATEGORY_RULES, RULES, rule_based_output
from agent.output_validator import (
    NOTE_AI_REJECTED,
    NOTE_AI_UNAVAILABLE,
    explain_audit,
    validate_output,
)
from agent.reasoning import AIUnavailableError
from analyzers import content, credibility, keyword, local_seo, technical
from crawler.models import Image
from findings import Category, Source, finding, unavailable
from scoring.score_engine import score_findings
from tests.factories import make_page, make_site

ROOT = Path(__file__).resolve().parent.parent

META = "technical.meta_description"
SPEED = "technical.speed_score"
LCP = "technical.lcp"
HTTPS = "technical.https"

FINDINGS = [
    finding(META, Category.TECHNICAL_SEO, "fail", "Meta description tag is missing.", weight=3,
            page="https://example.com/"),
    finding(SPEED, Category.TECHNICAL_SEO, "warn", "Mobile speed score of 62 out of 100.",
            source=Source.PAGESPEED, weight=3),
    finding(HTTPS, Category.TECHNICAL_SEO, "pass", "Site uses HTTPS.", weight=2),
    unavailable(LCP, Category.TECHNICAL_SEO, "PageSpeed timed out after 30 seconds.",
                source=Source.PAGESPEED),
]


def entry(check_id, explanation="Found.", why="It matters.", action="Fix it."):
    return {"check_id": check_id, "explanation": explanation, "why_it_matters": why, "action": action}


def priority(check_id, title="Fix this", reason="It helps."):
    return {"check_id": check_id, "title": title, "reason": reason}


def good_output():
    return {
        "findings": [
            entry(META, "Your homepage has no description."),
            entry(SPEED, "Your mobile speed score is 62 out of 100."),
            entry(LCP, "Load time could not be checked because PageSpeed timed out after 30 seconds.", "", ""),
        ],
        "top_priorities": [priority(META), priority(SPEED)],
    }


def changed(**overrides):
    return {**good_output(), **overrides}


def with_entry(replacement):
    """Good output, with the entry for ``replacement``'s check_id swapped."""
    output = good_output()
    output["findings"] = [
        replacement if item["check_id"] == replacement["check_id"] else item
        for item in output["findings"]
    ]
    return output


def problems_text(output, findings=FINDINGS):
    return "\n".join(validate_output(output, findings))


# --- Output that should pass ---


def test_good_output_passes():
    assert validate_output(good_output(), FINDINGS) == []


def test_nothing_to_explain_passes():
    passed = [finding(HTTPS, Category.TECHNICAL_SEO, "pass", "Site uses HTTPS.")]
    assert validate_output({"findings": [], "top_priorities": []}, passed) == []


@pytest.mark.parametrize(
    "explanation",
    [
        "Your mobile speed score is 62.",
        "Your speed score of 62 out of 100 is shown at https://example.com/page-2020.",
        "Check www.example.com/2024/ and example.org/99 for this.",
        "See /blog/2023 on your site.",
        "Your H1 and H2 headings are fine, and the score is 62.",
        "See (https://example.com/page-7) or example.org. Your score is 62.",
    ],
)
def test_evidence_numbers_addresses_and_heading_names_are_not_invented_metrics(explanation):
    assert validate_output(with_entry(entry(SPEED, explanation)), FINDINGS) == []


def test_number_format_differences_are_accepted():
    findings = [finding("a.b", Category.CONTENT_QUALITY, "fail", "1200 words, loads in 2.50 seconds.")]
    output = {
        "findings": [entry("a.b", "It has 1,200 words and loads in 2.5 seconds.")],
        "top_priorities": [priority("a.b")],
    }
    assert validate_output(output, findings) == []


def test_counting_the_checks_own_affected_pages_is_allowed():
    findings = [
        finding("a.b", Category.CONTENT_QUALITY, "fail", "Too short.", page=f"https://example.com/{n}")
        for n in "xyz"
    ]
    output = {
        "findings": [entry("a.b", "Three of your pages are too short.")],
        "top_priorities": [priority("a.b", reason="It affects 3 pages.")],
    }
    assert validate_output(output, findings) == []


@pytest.mark.parametrize(
    "action",
    [
        "Double-check the description after you publish it.",
        "Give each page one clear description.",
        "Start with your first page and work through the rest.",
    ],
)
def test_ordinary_phrases_are_not_treated_as_claims(action):
    assert validate_output(with_entry(entry(META, action=action)), FINDINGS) == []


# --- check_id citations ---


@pytest.mark.parametrize("bad_id", [None, "", "   ", 5])
def test_entry_without_a_check_id_is_rejected(bad_id):
    output = good_output()
    output["findings"].append({**entry(META), "check_id": bad_id})
    assert "has no check_id" in problems_text(output)


def test_entry_missing_the_check_id_field_is_rejected():
    output = good_output()
    output["findings"].append({"explanation": "x", "why_it_matters": "y", "action": "z"})
    assert "has no check_id" in problems_text(output)


def test_non_object_entry_is_rejected():
    output = good_output()
    output["findings"].append("just some text")
    assert "has no check_id" in problems_text(output)


def test_invented_check_id_is_rejected():
    output = good_output()
    output["findings"].append(entry("technical.made_up"))
    assert "technical.made_up: this check_id does not exist" in problems_text(output)


def test_invented_check_id_in_priorities_is_rejected():
    output = changed(top_priorities=[priority(META), priority("technical.made_up")])
    assert "technical.made_up: this check_id does not exist" in problems_text(output)


def test_writing_about_a_passed_check_is_rejected():
    output = good_output()
    output["findings"].append(entry(HTTPS))
    assert f"{HTTPS}: this check passed" in problems_text(output)


def test_check_that_passed_on_one_page_and_failed_on_another_is_allowed():
    findings = [
        finding("a.b", Category.CONTENT_QUALITY, "pass", "Good.", page="https://example.com/"),
        finding("a.b", Category.CONTENT_QUALITY, "fail", "Bad.", page="https://example.com/x"),
    ]
    output = {"findings": [entry("a.b")], "top_priorities": [priority("a.b")]}
    assert validate_output(output, findings) == []


def test_missing_entry_is_rejected():
    output = good_output()
    output["findings"] = [item for item in output["findings"] if item["check_id"] != META]
    assert f"{META}: this check has no entry" in problems_text(output)


def test_duplicate_entry_is_rejected():
    output = good_output()
    output["findings"].append(entry(META))
    assert f"{META}: write one entry" in problems_text(output)


@pytest.mark.parametrize("field", ["explanation", "why_it_matters", "action"])
def test_empty_text_on_a_failed_check_is_rejected(field):
    bad = {**entry(META), field: "   "}
    assert f"{META}: {field} must not be empty" in problems_text(with_entry(bad))


@pytest.mark.parametrize("output", [None, [], "text", {}, {"findings": []}, {"findings": {}, "top_priorities": []}])
def test_wrong_shape_is_rejected(output):
    assert validate_output(output, FINDINGS)


# --- Top priorities ---


def test_too_few_priorities_is_rejected():
    assert "exactly 2 items, not 1" in problems_text(changed(top_priorities=[priority(META)]))


def test_too_many_priorities_is_rejected():
    many = [finding(f"a.c{n}", Category.CONTENT_QUALITY, "fail", "Bad.") for n in "abcd"]
    output = {
        "findings": [entry(f"a.c{n}") for n in "abcd"],
        "top_priorities": [priority(f"a.c{n}") for n in "abcd"],
    }
    assert "exactly 3 items, not 4" in problems_text(output, many)


def test_priority_on_an_unavailable_check_is_rejected():
    output = changed(top_priorities=[priority(META), priority(LCP)])
    assert f"{LCP}: top_priorities can only use checks that failed or warned" in problems_text(output)


def test_priority_on_a_passed_check_is_rejected():
    output = changed(top_priorities=[priority(META), priority(HTTPS)])
    assert f"{HTTPS}: this check passed" in problems_text(output)


def test_repeated_priority_is_rejected():
    output = changed(top_priorities=[priority(META), priority(META)])
    assert f"{META}: listed more than once" in problems_text(output)


def test_empty_priority_title_is_rejected():
    output = changed(top_priorities=[priority(META, title=""), priority(SPEED)])
    assert f"{META}: title must not be empty" in problems_text(output)


def test_invented_number_in_a_priority_is_rejected():
    output = changed(top_priorities=[priority(META, reason="It could add 500 visitors."), priority(SPEED)])
    assert "500 is not in this check's evidence" in problems_text(output)


# --- Invented metrics ---


@pytest.mark.parametrize(
    ("text", "complaint"),
    [
        ("You could gain 40% more visitors.", "40 is not"),
        ("This adds 200ms of delay.", "200 is not"),
        ("Keep it under 160 characters.", "160 is not"),
        ("It costs you $1,500 a month.", "1500 is not"),
        ("You are losing seven customers a week.", "7 is not"),
        ("You are losing thousands of visitors.", '"thousands" is not'),
        ("This could bring twice the visitors.", '"twice" is not'),
        ("This could double your sales.", '"double" is not'),
        ("Your competitors already do this.", '"competitors" is not'),
        ("Reach the first page of Google.", '"first page of" is not'),
        ("Get to page one of the results.", '"page one of" is not'),
        ("Sales could grow by ten percent.", '"percent" is not'),
    ],
)
@pytest.mark.parametrize("field", ["explanation", "why_it_matters", "action"])
def test_invented_numbers_and_claims_are_rejected(field, text, complaint):
    bad = {**entry(META), field: text}
    assert complaint in problems_text(with_entry(bad))


@pytest.mark.parametrize(
    "hostile",
    ["a." * 10000, "a.1." * 5000, "1," * 10000, "1." * 10000, "x" * 20000, "/" * 20000, "- " * 10000],
)
def test_hostile_text_from_a_website_cannot_stall_the_validator(hostile):
    # Evidence can contain text from the scanned site. Slow matching would freeze the audit.
    findings = [finding("a.b", Category.CONTENT_QUALITY, "fail", hostile)]
    output = {
        "findings": [entry("a.b", hostile, hostile, hostile)],
        "top_priorities": [priority("a.b", hostile, hostile)],
    }
    started = time.perf_counter()
    validate_output(output, findings)
    assert time.perf_counter() - started < 1.0


def test_problem_messages_stay_short_for_huge_numbers():
    text = validate_output(with_entry(entry(META, "1" * 5000)), FINDINGS)
    assert all(len(problem) < 200 for problem in text)


def test_a_number_from_another_checks_evidence_is_rejected():
    # 62 is real, but it belongs to the speed check, not the meta description check.
    assert "62 is not" in problems_text(with_entry(entry(META, "Your score is 62.")))


def test_a_claim_is_allowed_when_it_is_in_the_evidence():
    findings = [finding("a.b", Category.CONTENT_QUALITY, "warn", "Your competitors link here.")]
    output = {
        "findings": [entry("a.b", "Your competitors link to this page.")],
        "top_priorities": [priority("a.b")],
    }
    assert validate_output(output, findings) == []


@pytest.mark.parametrize(
    "text, complaint",
    [
        ("Pages like this rarely rank well in search results.", '"rank'),
        ("Slow pages hurt your traffic.", '"traffic" is not'),
        ("Most people will not wait that long.", '"most people" is not'),
        ("Most visitors leave slow pages.", '"most visitors" is not'),
        ("Google may penalize this.", '"penali'),
        ("It raises your bounce rate.", '"bounce" is not'),
        ("It lowers conversions.", '"conversions" is not'),
    ],
)
def test_ranking_traffic_and_visitor_behavior_claims_need_evidence(text, complaint):
    assert complaint in problems_text(with_entry({**entry(META), "why_it_matters": text}))


def test_a_ranking_claim_is_allowed_when_the_scanner_evidence_says_it():
    # The word count rule's own wording mentions rankings, so repeating it is supported.
    findings = [finding("a.b", Category.CONTENT_QUALITY, "fail",
                        "Only 53 words of text. Pages with very little text rarely rank well.")]
    output = {
        "findings": [entry("a.b", "Only 53 words.", "Pages with very little text rarely rank well.")],
        "top_priorities": [priority("a.b")],
    }
    assert validate_output(output, findings) == []


def pages_findings(*statuses_and_pages):
    return [finding("a.b", Category.KEYWORD_OPTIMIZATION, status, "Meta description tag is missing.",
                    page=page) for status, page in statuses_and_pages]


def count_output(text):
    return {"findings": [entry("a.b", text)], "top_priorities": [priority("a.b")]}


def test_counts_of_the_checks_own_findings_are_allowed():
    findings = pages_findings(("fail", "https://e.com/a"), ("fail", "https://e.com/b"),
                              ("warn", "https://e.com/c"), ("warn", "https://e.com/c"))
    # 4 entries, 2 failed, 2 warned, 3 different pages (a page can appear twice).
    for text in ("4 pages are affected.", "2 pages fail.", "2 pages warn.", "3 different pages."):
        assert validate_output(count_output(text), findings) == [], text
    assert "5 is not" in "\n".join(validate_output(count_output("5 pages are affected."), findings))


def mixed_readability_findings():
    """Like spicymoonnyc.com, plus pages that passed, so every way of counting differs:
    15 pages in all, 11 not passed, 3 with a problem (2 failed, 1 warned), 8 that could
    not be measured, 4 passed and 7 actually measured. Every count differs, so each one
    is tested on its own."""
    unmeasurable = "Reading ease could not be measured because this page is mostly lists."
    return [
        finding("a.b", Category.CONTENT_QUALITY, "fail", "Reading ease score is 17 out of 100.", page="https://e.com/beer"),
        finding("a.b", Category.CONTENT_QUALITY, "fail", "Reading ease score is 21 out of 100.", page="https://e.com/wine"),
        finding("a.b", Category.CONTENT_QUALITY, "warn", "Reading ease score is 32 out of 100.", page="https://e.com/events"),
        *[unavailable("a.b", Category.CONTENT_QUALITY, unmeasurable, page=f"https://e.com/menu{n}") for n in range(8)],
        *[finding("a.b", Category.CONTENT_QUALITY, "pass", "Easy to read.", page=f"https://e.com/ok{n}") for n in range(4)],
    ]


@pytest.mark.parametrize(
    "text",
    [
        "3 pages are hard to read.",                              # with a problem (failed + warned)
        "8 pages could not be measured because they are menus.",  # could not be checked
        "3 of the 15 pages are hard to read.",                    # with a problem, of all pages
        "2 pages are very hard to read and 1 needs attention.",   # failed, warned
        "We measured 7 pages.",                                   # actually measured
        "4 pages are already easy to read.",                      # passed
        "11 pages were not easy to read or could not be checked.",  # not passed
    ],
)
def test_true_counts_on_a_check_with_mixed_statuses_are_allowed(text):
    assert validate_output(count_output(text), mixed_readability_findings()) == []


@pytest.mark.parametrize("wrong", ["5 pages are hard to read.", "9 pages could not be measured.", "12 pages."])
def test_wrong_counts_on_a_check_with_mixed_statuses_are_still_rejected(wrong):
    problems = validate_output(count_output(wrong), mixed_readability_findings())
    assert any("is not in this check's evidence" in problem for problem in problems), wrong


def test_counting_the_pages_that_passed_is_allowed():
    findings = pages_findings(("fail", "https://e.com/a"), ("pass", "https://e.com/b"),
                              ("pass", "https://e.com/c"), ("pass", "https://e.com/d"))
    for text in ("3 pages already have one.", "1 of 4 pages is missing it."):
        assert validate_output(count_output(text), findings) == [], text


@pytest.mark.parametrize("invented", ["Aim for 70 to 160 characters.", "Write at least 100 words."])
def test_invented_guideline_numbers_are_still_rejected(invented):
    findings = pages_findings(("fail", "https://e.com/a"), ("fail", "https://e.com/b"))
    assert validate_output(count_output(invented), findings)


# --- Unavailable checks ---


@pytest.mark.parametrize("field", ["why_it_matters", "action"])
def test_advice_on_an_unavailable_check_is_rejected(field):
    bad = {**entry(LCP, "It could not be checked.", "", ""), field: "Speed matters a lot."}
    assert f"{LCP}: this check could not be measured, so why_it_matters and action must be empty" in problems_text(with_entry(bad))


@pytest.mark.parametrize(
    "explanation", ["Your load time is good.", "This page is probably slow.", "Your site likely passed this check."]
)
def test_verdict_on_an_unavailable_check_is_rejected(explanation):
    bad = entry(LCP, explanation, "", "")
    assert "so do not call it" in problems_text(with_entry(bad))


def test_empty_explanation_on_an_unavailable_check_is_rejected():
    bad = entry(LCP, "", "", "")
    assert f"{LCP}: explanation must say" in problems_text(with_entry(bad))


def test_invented_number_on_an_unavailable_check_is_rejected():
    bad = entry(LCP, "It usually takes 4 seconds, but this could not be checked.", "", "")
    assert "4 is not" in problems_text(with_entry(bad))


def test_verdict_word_from_the_evidence_is_allowed_on_an_unavailable_check():
    findings = [unavailable("a.b", Category.TECHNICAL_SEO, "The provider was too slow to answer.")]
    output = {"findings": [entry("a.b", "The provider was too slow to answer.", "", "")], "top_priorities": []}
    assert validate_output(output, findings) == []


def test_check_that_is_unavailable_on_one_page_and_failed_on_another_can_give_advice():
    findings = [
        unavailable("a.b", Category.TECHNICAL_SEO, "Page was built with JavaScript.", page="https://example.com/"),
        finding("a.b", Category.TECHNICAL_SEO, "fail", "Tag is missing.", page="https://example.com/x"),
    ]
    output = {"findings": [entry("a.b")], "top_priorities": [priority("a.b")]}
    assert validate_output(output, findings) == []


# --- Retry and fallback flow ---


class FakeAI:
    """Replaces explain_findings. Each call uses the next outcome and records the feedback."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.feedback = []

    def __call__(self, findings, scores, context, feedback=None, client=None):
        self.feedback.append(feedback)
        self.received = SimpleNamespace(scores=scores, context=context, client=client)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture
def ai(monkeypatch):
    def install(*outcomes):
        fake = FakeAI(*outcomes)
        monkeypatch.setattr(output_validator, "explain_findings", fake)
        return fake

    return install


BAD_OUTPUT = {"findings": [entry("technical.made_up")], "top_priorities": []}


def test_good_answer_is_used_with_no_retry_and_no_note(ai):
    fake = ai(good_output())
    result = explain_audit(FINDINGS)
    assert result.output == good_output()
    assert result.ai_generated is True
    assert result.note is None
    assert fake.feedback == [None]


def test_scores_context_and_client_reach_the_agent(ai):
    fake = ai(good_output())
    explain_audit(FINDINGS, "scores", "context", client="client")
    assert fake.received == SimpleNamespace(scores="scores", context="context", client="client")


def test_rejected_answer_gets_one_retry_with_the_complaints(ai):
    fake = ai(BAD_OUTPUT, good_output())
    result = explain_audit(FINDINGS)
    assert result.ai_generated is True
    assert result.output == good_output()
    assert fake.feedback[0] is None
    assert "technical.made_up" in fake.feedback[1]


def test_rejected_twice_falls_back_without_a_third_call(ai):
    fake = ai(BAD_OUTPUT, BAD_OUTPUT, good_output())
    result = explain_audit(FINDINGS)
    assert result.ai_generated is False
    assert result.note == NOTE_AI_REJECTED
    assert result.output == rule_based_output(FINDINGS)
    assert len(fake.feedback) == 2


def test_ai_down_falls_back_without_retrying(ai):
    fake = ai(AIUnavailableError("The AI service could not be reached."), good_output())
    result = explain_audit(FINDINGS)
    assert result.ai_generated is False
    assert result.note == NOTE_AI_UNAVAILABLE
    assert result.output == rule_based_output(FINDINGS)
    assert len(fake.feedback) == 1


def test_ai_going_down_during_the_retry_falls_back(ai):
    ai(BAD_OUTPUT, AIUnavailableError("The AI service took too long to answer."))
    result = explain_audit(FINDINGS)
    assert result.ai_generated is False
    assert result.note == NOTE_AI_UNAVAILABLE


def test_unexpected_crash_falls_back_and_never_reaches_the_user(ai):
    ai(RuntimeError("secret internal detail"))
    result = explain_audit(FINDINGS)
    assert result.ai_generated is False
    assert "secret" not in result.note
    assert "secret" not in json.dumps(result.output)


def test_feedback_is_capped(ai):
    fake = ai(
        {"findings": [entry(f"made.up{n}") for n in range(40)], "top_priorities": []},
        good_output(),
    )
    explain_audit(FINDINGS)
    assert len(fake.feedback[1].splitlines()) == output_validator.MAX_FEEDBACK_PROBLEMS


def test_missing_api_key_gives_the_fallback_through_the_real_agent(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = explain_audit(FINDINGS, score_findings(FINDINGS))
    assert result.ai_generated is False
    assert result.note == NOTE_AI_UNAVAILABLE


def test_real_agent_response_goes_through_retry_and_validation():
    def response(payload):
        text = json.dumps(payload)
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])

    answers = [response(BAD_OUTPUT), response(good_output())]
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return answers.pop(0)

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    result = explain_audit(FINDINGS, client=client, scores=score_findings(FINDINGS))

    assert result.ai_generated is True
    assert result.output == good_output()
    assert "Your previous answer was rejected" not in calls[0]["messages"][0]["content"]
    assert "technical.made_up" in calls[1]["messages"][0]["content"]


# --- Rule-based text ---


def _analyzer_check_ids():
    """Every check ID the analyzers and integrations can emit, read from their source."""
    pattern = re.compile(r'"((?:keyword|content|local|technical|credibility)\.[a-z0-9_]+)"')
    ids = set()
    for folder in ("analyzers", "integrations"):
        for path in (ROOT / folder).glob("*.py"):
            ids |= set(pattern.findall(path.read_text(encoding="utf-8")))
    return ids


def test_finding_check_ids_works():
    # Guards the next test: it would pass by accident if this found nothing.
    assert {"keyword.h1", "technical.https", "credibility.backlinks"} <= _analyzer_check_ids()


def test_every_check_has_its_own_rule_based_wording():
    # local.not_applicable is only ever unavailable, so it never shows any advice.
    assert _analyzer_check_ids() - set(RULES) - {"local.not_applicable"} == set()


@pytest.mark.parametrize("check_id", sorted(RULES))
def test_rule_wording_has_no_numbers_or_claims(check_id):
    for text in RULES[check_id]:
        assert text.strip()
        assert not output_validator._numbers(text), text
        assert not output_validator._CLAIM_RE.search(text), text


@pytest.mark.parametrize("category", list(Category))
def test_every_category_has_generic_wording(category):
    title, why, action = CATEGORY_RULES[category]
    assert title and why and action
    assert not output_validator._numbers(f"{title} {why} {action}")


def _all_findings(site):
    speed = [
        finding("technical.speed_score", Category.TECHNICAL_SEO, "fail", "Score of 31 out of 100.",
                source=Source.PAGESPEED, weight=3),
        unavailable("technical.lcp", Category.TECHNICAL_SEO, "PageSpeed could not report this.",
                    source=Source.PAGESPEED, weight=2),
    ]
    return [
        *keyword.analyze(site),
        *content.analyze(site),
        *local_seo.analyze(site),
        *technical.analyze(site, extra=speed),
        *credibility.analyze(site),
    ]


SITES = {
    "healthy": make_site(),
    "many problems": make_site(
        make_page(
            url="https://example.com/2024/", title=None, meta_description=None, canonical=None, lang=None,
            has_viewport=False, headings=(), text="Short.", phones=(), addresses=(), social_links=(),
            images=(Image("https://example.com/a.jpg", None),), internal_links=(),
        ),
        make_page(url="https://example.com/x", status_code=404, title="Home", meta_description="Too short"),
        make_page(url="http://example.com/y", title="Home", meta_description="Too short", phones=("555-0199",)),
        robots_txt_found=False, sitemap_url=None, sitemap_page_count=0,
    ),
    "built with javascript": make_site(
        make_page(title=None, meta_description=None, headings=(), text="", likely_js_rendered=True,
                  phones=(), addresses=(), social_links=(), images=(), internal_links=(), external_links=(),
                  canonical=None, lang=None, has_viewport=False)
    ),
}


@pytest.mark.parametrize("name", SITES)
def test_fallback_for_real_analyzer_findings_passes_the_validator(name):
    findings = _all_findings(SITES[name])
    assert validate_output(rule_based_output(findings), findings) == []


def test_fallback_covers_nothing_when_everything_passed():
    passed = [finding(HTTPS, Category.TECHNICAL_SEO, "pass", "Site uses HTTPS.")]
    assert rule_based_output(passed) == {"findings": [], "top_priorities": []}


def test_fallback_explanation_is_the_evidence_with_its_page():
    item = next(x for x in rule_based_output(FINDINGS)["findings"] if x["check_id"] == META)
    assert item["explanation"] == "https://example.com/: Meta description tag is missing."


def test_fallback_does_not_repeat_a_page_already_in_the_evidence():
    found = [finding("a.b", Category.CONTENT_QUALITY, "fail", "https://example.com/ has no text.",
                     page="https://example.com/")]
    assert rule_based_output(found)["findings"][0]["explanation"] == "https://example.com/ has no text."


def test_fallback_merges_pages_into_one_entry_per_check():
    pages = ["https://example.com/", "https://example.com/x"]
    found = [finding("a.b", Category.CONTENT_QUALITY, "fail", "Too short.", page=p) for p in pages]
    entries = rule_based_output(found)["findings"]
    assert len(entries) == 1
    assert all(page in entries[0]["explanation"] for page in pages)


def test_fallback_gives_no_advice_on_unavailable_checks():
    item = next(x for x in rule_based_output(FINDINGS)["findings"] if x["check_id"] == LCP)
    assert item["why_it_matters"] == "" and item["action"] == ""
    assert item["explanation"] == "PageSpeed timed out after 30 seconds."


def test_fallback_never_prioritizes_unavailable_or_passed_checks():
    ids = [item["check_id"] for item in rule_based_output(FINDINGS)["top_priorities"]]
    assert LCP not in ids and HTTPS not in ids


def test_fallback_uses_category_wording_for_an_unknown_check():
    found = [finding("technical.brand_new", Category.TECHNICAL_SEO, "fail", "Something is off.")]
    item = rule_based_output(found)["findings"][0]
    assert (item["why_it_matters"], item["action"]) == CATEGORY_RULES[Category.TECHNICAL_SEO][1:]


def test_fallback_ranks_by_weight_then_failures_then_pages_and_keeps_three():
    def make(check_id, status, weight, pages=1):
        return [
            finding(check_id, Category.CONTENT_QUALITY, status, "x", weight=weight, page=f"https://example.com/{n}")
            for n in range(pages)
        ]

    found = [
        *make("a.light", "fail", 1),
        *make("a.warned", "warn", 3),
        *make("a.failed", "fail", 3),
        *make("a.failed_more", "fail", 3, pages=2),
        *make("a.mid", "fail", 2),
    ]
    ids = [item["check_id"] for item in rule_based_output(found)["top_priorities"]]
    assert ids == ["a.failed_more", "a.failed", "a.warned"]


def test_fallback_ranking_ignores_the_weight_of_unavailable_findings():
    found = [
        unavailable("a.mixed", Category.CONTENT_QUALITY, "Not checked.", weight=9, page="https://example.com/"),
        finding("a.mixed", Category.CONTENT_QUALITY, "warn", "x", weight=1, page="https://example.com/x"),
        finding("a.other", Category.CONTENT_QUALITY, "fail", "y", weight=2),
    ]
    ids = [item["check_id"] for item in rule_based_output(found)["top_priorities"]]
    assert ids == ["a.other", "a.mixed"]
