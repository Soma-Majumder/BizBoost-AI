"""Output validator: AI text only reaches the user if it is backed by the evidence.

``explain_audit(findings, scores, context)`` is what the app calls. It asks the AI agent,
checks the answer, retries once with the complaints, then falls back to rule-based text.
It never raises, so the audit always has something to show:

    result = explain_audit(findings, scores)
    result.output         # same shape as the AI agent's output
    result.ai_generated   # False when the text is rule-based
    result.note           # a sentence to show the user, or None

``validate_output(output, findings)`` returns a list of problems (empty means it passed):
    * every item must cite the ``check_id`` of a finding it is allowed to write about
    * every fail, warn and unavailable check gets exactly one entry
    * ``unavailable`` checks only say what could not be checked, with no verdict or advice
    * text may not state numbers or claims that are not in that check's evidence

The number and claim checks catch figures, not every possible wrong sentence. Human
review on the 10 test sites (issue #19) covers the rest.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

from agent.fallback_text import rule_based_output
from agent.reasoning import (
    TOP_PRIORITY_COUNT,
    AIUnavailableError,
    BusinessContext,
    explain_findings,
)
from findings import Finding, Status
from scoring.score_engine import ScoreReport

logger = logging.getLogger(__name__)

MAX_FEEDBACK_PROBLEMS = 15
MAX_ID_CHARS = 80

NOTE_AI_UNAVAILABLE = (
    "AI explanations are unavailable right now, so you're seeing standard explanations "
    "instead. Your scores and findings aren't affected."
)
NOTE_AI_REJECTED = (
    "We couldn't verify the AI explanations against your scan results, so you're seeing "
    "standard explanations instead. Your scores and findings aren't affected."
)

# Words that are addresses are dropped before looking for numbers, so "/page-2" is not a
# statistic. Evidence can contain text from the scanned website, so this is matched once
# per word: searching the whole text with it takes far too long on text like "a.a.a.a...".
_ADDRESS_WORD_RE = re.compile(
    r"""[("'\[]*(?:https?://|www\.|/|(?:[a-z0-9-]+\.)+[a-z]{2,}(?![a-z0-9-]))""", re.I
)
MAX_NUMBER_CHARS = 40
# Digits not attached to a letter before them, so "H1" is not a number but "200ms" is.
_NUMBER_RE = re.compile(r"(?<![A-Za-z0-9.,])\d+(?:[.,]\d+)*")
_NUMBER_WORDS = {
    "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12,
}
_NUMBER_WORD_RE = re.compile(rf"\b(?:{'|'.join(_NUMBER_WORDS)})\b", re.I)
_CLAIM_RE = re.compile(
    r"\b(?:hundreds?|thousands?|millions?|billions?|dozens?|twice|double(?!-check)\w*|triple\w*"
    r"|percent\w*|competitors?|rivals?|first page of|page one of|number one|top of google"
    r"|rank\w*|traffic|bounce\w*|penali[sz]\w*|conversions?"
    r"|most (?:people|users|visitors|customers|shoppers))\b",
    re.I,
)
# A check that could not be measured has no result, so it cannot be judged.
_VERDICT_RE = re.compile(
    r"\b(?:good|bad|poor|great|excellent|fine|healthy|weak|strong|slow|fast"
    r"|failed|failing|passed|passing)\b",
    re.I,
)

_FINDING_FIELDS = ("explanation", "why_it_matters", "action")
_PRIORITY_FIELDS = ("title", "reason")


@dataclass(frozen=True)
class Explanation:
    output: dict[str, Any]  # {"findings": [...], "top_priorities": [...]}
    ai_generated: bool
    note: str | None = None  # show this to the user when it is set


def explain_audit(
    findings: Iterable[Finding],
    scores: ScoreReport | dict[str, Any] | None = None,
    context: BusinessContext | None = None,
    client: Any = None,
) -> Explanation:
    """Validated AI text, one retry if it is rejected, otherwise rule-based text."""
    items = list(findings)
    feedback = None
    for _ in range(2):
        try:
            output = explain_findings(items, scores, context, feedback=feedback, client=client)
        except AIUnavailableError as error:
            logger.warning("AI explanations unavailable: %s", error)
            return _fallback(items, NOTE_AI_UNAVAILABLE)
        except Exception:
            logger.exception("AI agent crashed")
            return _fallback(items, NOTE_AI_UNAVAILABLE)

        problems = validate_output(output, items)
        if not problems:
            return Explanation(output=output, ai_generated=True)
        logger.warning("AI output rejected: %s", "; ".join(problems))
        feedback = "\n".join(problems[:MAX_FEEDBACK_PROBLEMS])
    return _fallback(items, NOTE_AI_REJECTED)


def _fallback(findings: list[Finding], note: str) -> Explanation:
    return Explanation(output=rule_based_output(findings), ai_generated=False, note=note)


def validate_output(output: Any, findings: Iterable[Finding]) -> list[str]:
    """Return what is wrong with the AI output. An empty list means it passed."""
    if not isinstance(output, dict):
        return ["The answer must be an object with findings and top_priorities."]
    entries, priorities = output.get("findings"), output.get("top_priorities")
    if not isinstance(entries, list) or not isinstance(priorities, list):
        return ["The answer must have a findings list and a top_priorities list."]

    by_check: dict[str, list[Finding]] = defaultdict(list)
    for item in findings:
        by_check[item.check_id].append(item)
    return _check_entries(entries, by_check) + _check_priorities(priorities, by_check)


def _check_entries(entries: list[Any], by_check: dict[str, list[Finding]]) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        check_id = _cited_id(entry, by_check, problems, "findings")
        if check_id is None:
            continue
        if check_id in seen:
            problems.append(f"{check_id}: write one entry per check_id, not several.")
        seen.add(check_id)

        group = by_check[check_id]
        if not _has_status(group, Status.FAIL, Status.WARN):
            problems += _check_unavailable_entry(entry, check_id, group)
        else:
            for field in _FINDING_FIELDS:
                if not _text(entry, field):
                    problems.append(f"{check_id}: {field} must not be empty.")
        for field in _FINDING_FIELDS:
            problems += _check_claims(_text(entry, field), check_id, group)

    for check_id, group in by_check.items():
        if check_id not in seen and _has_status(group, Status.FAIL, Status.WARN, Status.UNAVAILABLE):
            problems.append(f"{check_id}: this check has no entry. Write one.")
    return problems


def _check_unavailable_entry(entry: dict, check_id: str, group: list[Finding]) -> list[str]:
    problems: list[str] = []
    explanation = _text(entry, "explanation")
    if not explanation:
        problems.append(f"{check_id}: explanation must say what could not be checked and why.")
    if _text(entry, "why_it_matters") or _text(entry, "action"):
        problems.append(
            f"{check_id}: this check could not be measured, so why_it_matters and action must be empty."
        )
    evidence = " ".join(item.evidence for item in group).lower()
    for word in {match.lower() for match in _VERDICT_RE.findall(explanation)}:
        if not re.search(rf"\b{word}\b", evidence):
            problems.append(f'{check_id}: this check could not be measured, so do not call it "{word}".')
    return problems


def _check_priorities(priorities: list[Any], by_check: dict[str, list[Finding]]) -> list[str]:
    problems: list[str] = []
    fixable = [cid for cid, group in by_check.items() if _has_status(group, Status.FAIL, Status.WARN)]
    expected = min(TOP_PRIORITY_COUNT, len(fixable))
    if len(priorities) != expected:
        problems.append(f"top_priorities must list exactly {expected} items, not {len(priorities)}.")

    seen: set[str] = set()
    for priority in priorities:
        check_id = _cited_id(priority, by_check, problems, "top_priorities")
        if check_id is None:
            continue
        if check_id in seen:
            problems.append(f"{check_id}: listed more than once in top_priorities.")
        seen.add(check_id)
        if check_id not in fixable:
            problems.append(f"{check_id}: top_priorities can only use checks that failed or warned.")
        for field in _PRIORITY_FIELDS:
            text = _text(priority, field)
            if not text:
                problems.append(f"{check_id}: {field} must not be empty in top_priorities.")
            problems += _check_claims(text, check_id, by_check[check_id])
    return problems


def _cited_id(
    item: Any, by_check: dict[str, list[Finding]], problems: list[str], where: str
) -> str | None:
    """The check_id this item may write about. Otherwise record a problem and return None."""
    check_id = item.get("check_id") if isinstance(item, dict) else None
    if not isinstance(check_id, str) or not check_id.strip():
        problems.append(f"An item in {where} has no check_id. Every item must cite one.")
        return None
    if check_id not in by_check:
        problems.append(f"{check_id[:MAX_ID_CHARS]}: this check_id does not exist in the audit data.")
        return None
    if not _has_status(by_check[check_id], Status.FAIL, Status.WARN, Status.UNAVAILABLE):
        problems.append(f"{check_id}: this check passed. Do not write about passed checks.")
        return None
    return check_id


def _check_claims(text: str, check_id: str, group: list[Finding]) -> list[str]:
    """Numbers and claims must come from this check's evidence, or count its own findings.

    Counts of the check's own findings are allowed: how many there are, how many failed or
    warned, and how many different pages they cover (a page can appear twice).
    """
    relevant = [item for item in group if item.status is not Status.PASS]
    evidence = " ".join(item.evidence for item in relevant)
    own_counts = {
        len(relevant),
        sum(1 for item in relevant if item.status is Status.FAIL),
        sum(1 for item in relevant if item.status is Status.WARN),
        len({item.page for item in relevant if item.page}),
    }
    allowed = _numbers(evidence) | {Decimal(count) for count in own_counts}
    evidence_lower = evidence.lower()

    problems = [
        f"{check_id}: {str(number)[:MAX_NUMBER_CHARS]} is not in this check's evidence. Remove it."
        for number in sorted(_numbers(text) - allowed)
    ]
    for claim in {match.lower() for match in _CLAIM_RE.findall(text)}:
        if claim not in evidence_lower:
            problems.append(f'{check_id}: "{claim}" is not in this check\'s evidence. Remove it.')
    return problems


def _numbers(text: str) -> set[Decimal]:
    text = " ".join(word for word in text.split() if not _ADDRESS_WORD_RE.match(word))
    numbers = {Decimal(_NUMBER_WORDS[word.lower()]) for word in _NUMBER_WORD_RE.findall(text)}
    for token in _NUMBER_RE.findall(text):
        try:
            numbers.add(Decimal(token.replace(",", "")))
        except InvalidOperation:  # something like a version number, 1.2.3
            continue
    return numbers


def _text(item: dict, field: str) -> str:
    value = item.get(field)
    return value.strip() if isinstance(value, str) else ""


def _has_status(group: list[Finding], *statuses: Status) -> bool:
    return any(item.status in statuses for item in group)
