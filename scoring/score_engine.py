"""Scoring engine: unavailable checks dropped, weights rescaled to 100.

Rules (PRD A10):
    * Points per measured check: pass 1, warn 0.5, fail 0.
    * ``unavailable`` checks are dropped. They never count as zero.
    * Category score = 100 * sum(weight * points) / sum(weight), measured checks only.
    * Overall score = weighted average of category scores. A category with no measured
      checks is left out and the remaining category weights are rescaled to add to 100.

Usage:
    report = score_findings(findings)
    report.overall               # float 0-100, or None if nothing could be measured
    report.categories["technical_seo"].score
    report.to_dict()             # JSON-ready, for the AI agent and the report
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from findings import Category, Finding, Status

# Initial category weights (first guess, to tune after the 10 test sites).
CATEGORY_WEIGHTS: dict[Category, int] = {
    Category.TECHNICAL_SEO: 25,
    Category.KEYWORD_OPTIMIZATION: 25,
    Category.CONTENT_QUALITY: 20,
    Category.LOCAL_SEO: 20,
    Category.CREDIBILITY_BACKLINKS: 10,
}

STATUS_POINTS: dict[Status, float] = {
    Status.PASS: 1.0,
    Status.WARN: 0.5,
    Status.FAIL: 0.0,
}


@dataclass(frozen=True)
class CategoryScore:
    category: Category
    score: float | None  # 0-100, or None when no check in this category was measured
    weight: int  # configured category weight
    effective_weight: float  # share of the overall score after rescaling (0 if left out)
    measured: int  # findings that counted
    unavailable: int  # findings that were dropped

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "score": self.score,
            "weight": self.weight,
            "effective_weight": self.effective_weight,
            "measured": self.measured,
            "unavailable": self.unavailable,
        }


@dataclass(frozen=True)
class ScoreReport:
    overall: float | None  # 0-100, or None when nothing could be measured
    categories: dict[str, CategoryScore]  # keyed by Category value, all five present

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "categories": {key: cat.to_dict() for key, cat in self.categories.items()},
        }


def category_score(findings: Iterable[Finding]) -> float | None:
    """Score 0-100 for findings of one category, or None if none were measured."""
    earned = 0.0
    total = 0
    for item in findings:
        if not item.is_measured:
            continue
        earned += item.weight * STATUS_POINTS[item.status]
        total += item.weight
    if total == 0:
        return None
    return 100 * earned / total


def score_findings(findings: Iterable[Finding]) -> ScoreReport:
    """Score a full audit. Every category appears in the result, measured or not."""
    items = list(findings)
    raw: dict[Category, float | None] = {}
    measured_count: dict[Category, int] = {}
    unavailable_count: dict[Category, int] = {}

    for cat in CATEGORY_WEIGHTS:
        in_cat = [f for f in items if f.category == cat]
        raw[cat] = category_score(in_cat)
        measured_count[cat] = sum(1 for f in in_cat if f.is_measured)
        unavailable_count[cat] = sum(1 for f in in_cat if f.status == Status.UNAVAILABLE)

    scored = [cat for cat, value in raw.items() if value is not None]
    weight_sum = sum(CATEGORY_WEIGHTS[cat] for cat in scored)

    overall: float | None = None
    if weight_sum:
        overall = sum(raw[cat] * CATEGORY_WEIGHTS[cat] for cat in scored) / weight_sum

    categories = {
        cat.value: CategoryScore(
            category=cat,
            score=raw[cat],
            weight=CATEGORY_WEIGHTS[cat],
            effective_weight=(100 * CATEGORY_WEIGHTS[cat] / weight_sum)
            if raw[cat] is not None
            else 0.0,
            measured=measured_count[cat],
            unavailable=unavailable_count[cat],
        )
        for cat in CATEGORY_WEIGHTS
    }
    return ScoreReport(overall=overall, categories=categories)
