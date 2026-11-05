import pytest

from findings import Category, finding, unavailable
from scoring.score_engine import CATEGORY_WEIGHTS, category_score, score_findings

TECH = Category.TECHNICAL_SEO


def f(check_id, status, category=TECH, weight=1):
    return finding(check_id, category, status, "evidence", weight=weight)


def test_weights_add_up_to_100():
    assert sum(CATEGORY_WEIGHTS.values()) == 100


def test_prd_example_warn_and_fail():
    items = [f("a", "pass", weight=3), f("b", "fail", weight=3), f("c", "warn", weight=3)]
    assert category_score(items) == pytest.approx(50)


def test_unavailable_check_is_dropped_not_zero():
    # PRD A10: unavailable must give 100, not the 67 it would be if counted as a failure.
    items = [f("a", "pass", weight=3), f("b", "pass", weight=3)]
    items.append(unavailable("c", TECH, "JavaScript content", weight=3))
    assert category_score(items) == pytest.approx(100)


def test_unavailable_never_lowers_a_score():
    base = [f("a", "pass", weight=2), f("b", "fail", weight=2)]
    with_unavailable = base + [unavailable("c", TECH, "no key", weight=10)]
    assert category_score(with_unavailable) == category_score(base)


def test_weight_matters():
    items = [f("a", "pass", weight=3), f("b", "fail", weight=1)]
    assert category_score(items) == pytest.approx(75)


def test_all_unavailable_category_has_no_score():
    assert category_score([unavailable("a", TECH, "blocked")]) is None
    assert category_score([]) is None


def test_overall_uses_category_weights():
    items = [
        f("t", "pass", Category.TECHNICAL_SEO),
        f("k", "fail", Category.KEYWORD_OPTIMIZATION),
        f("c", "pass", Category.CONTENT_QUALITY),
        f("l", "pass", Category.LOCAL_SEO),
        f("b", "pass", Category.CREDIBILITY_BACKLINKS),
    ]
    report = score_findings(items)
    assert report.overall == pytest.approx(75)  # keyword (25) scores 0, the other 75 score 100


def test_prd_veganbodhi_worked_example():
    scores = {
        Category.TECHNICAL_SEO: 100,
        Category.KEYWORD_OPTIMIZATION: 69,
        Category.CONTENT_QUALITY: 70,
        Category.LOCAL_SEO: 83,
        Category.CREDIBILITY_BACKLINKS: 95,
    }
    items = []
    for cat, pct in scores.items():
        items.append(f(f"{cat.value}.pass", "pass", cat, weight=pct))
        if pct < 100:  # weight must be 1 or more
            items.append(f(f"{cat.value}.fail", "fail", cat, weight=100 - pct))
    report = score_findings(items)
    for cat, pct in scores.items():
        assert report.categories[cat.value].score == pytest.approx(pct)
    assert report.overall == pytest.approx(82, abs=0.5)


def test_category_with_no_measured_checks_is_left_out_and_weights_rescaled():
    items = [
        f("t", "pass", Category.TECHNICAL_SEO),  # 100, weight 25
        f("k", "fail", Category.KEYWORD_OPTIMIZATION),  # 0, weight 25
        unavailable("l", Category.LOCAL_SEO, "not relevant"),
    ]
    report = score_findings(items)
    assert report.overall == pytest.approx(50)  # (100*25 + 0*25) / 50, not divided by 100
    local = report.categories["local_seo"]
    assert local.score is None
    assert local.effective_weight == 0
    assert report.categories["technical_seo"].effective_weight == pytest.approx(50)
    assert sum(c.effective_weight for c in report.categories.values()) == pytest.approx(100)


def test_unavailable_category_does_not_drag_overall_down():
    only_tech = [f("t", "pass", Category.TECHNICAL_SEO)]
    assert score_findings(only_tech).overall == pytest.approx(100)


def test_nothing_measured_gives_no_overall_score():
    report = score_findings([unavailable("a", TECH, "blocked")])
    assert report.overall is None
    assert all(c.score is None for c in report.categories.values())
    assert score_findings([]).overall is None


def test_all_five_categories_always_present():
    report = score_findings([f("t", "pass")])
    assert set(report.categories) == {c.value for c in Category}


def test_counts_measured_and_unavailable():
    items = [f("a", "pass"), f("b", "warn"), unavailable("c", TECH, "x")]
    tech = score_findings(items).categories["technical_seo"]
    assert (tech.measured, tech.unavailable) == (2, 1)


def test_to_dict_is_json_ready():
    import json

    data = score_findings([f("a", "pass"), unavailable("b", Category.LOCAL_SEO, "x")]).to_dict()
    json.dumps(data)
    assert data["overall"] == 100
    assert data["categories"]["local_seo"]["score"] is None
    assert data["categories"]["technical_seo"]["category"] == "technical_seo"
