import pytest

from analyzers.keyword import analyze
from crawler.models import Heading
from findings import Category, Status
from tests.factories import make_page, make_site


def by_id(findings, check_id, page=None):
    matches = [f for f in findings if f.check_id == check_id and (page is None or f.page == page)]
    assert matches, f"no finding for {check_id}"
    return matches[0]


def test_healthy_page_passes_everything():
    results = analyze(make_site())
    assert results and all(f.status is Status.PASS for f in results)
    assert all(f.category is Category.KEYWORD_OPTIMIZATION for f in results)
    assert all(f.evidence for f in results)


def test_missing_title_meta_and_h1_fail_with_page_url():
    page = make_page(title=None, meta_description=None, headings=())
    results = analyze(make_site(page))
    for cid in ("keyword.title", "keyword.meta_description", "keyword.h1"):
        item = by_id(results, cid)
        assert item.status is Status.FAIL
        assert item.page == page.url
        assert item.weight == 3


def test_blank_title_counts_as_missing():
    assert by_id(analyze(make_site(make_page(title="   "))), "keyword.title").status is Status.FAIL


def test_generic_title_warns():
    # Mirrors veganbodhi.com: "Home - Bodhi Kosher Vegetarian Restaurant"
    page = make_page(title="Home - Bodhi Kosher Vegetarian Restaurant")
    item = by_id(analyze(make_site(page)), "keyword.title")
    assert item.status is Status.WARN
    assert "generic" in item.evidence


@pytest.mark.parametrize("title", ["Bakery", "A" * 66])
def test_title_length_out_of_range_warns(title):
    assert by_id(analyze(make_site(make_page(title=title))), "keyword.title").status is Status.WARN


@pytest.mark.parametrize("desc", ["Too short.", "x" * 161])
def test_description_length_out_of_range_warns(desc):
    item = by_id(analyze(make_site(make_page(meta_description=desc))), "keyword.meta_description")
    assert item.status is Status.WARN


def test_multiple_h1_warns():
    page = make_page(headings=(Heading(1, "One"), Heading(1, "Two")))
    item = by_id(analyze(make_site(page)), "keyword.h1")
    assert item.status is Status.WARN
    assert "2 H1" in item.evidence


def test_title_terms_missing_from_content_warns():
    page = make_page(
        title="Brooklyn Plumbing Repair Experts",
        text="We bake bread and pastries every morning. " * 20,
        headings=(Heading(1, "Welcome"),),
    )
    item = by_id(analyze(make_site(page)), "keyword.title_terms_in_content")
    assert item.status is Status.WARN
    assert "plumbing" in item.evidence


def test_duplicate_titles_and_descriptions_fail_across_pages():
    a = make_page(url="https://example.com/")
    b = make_page(url="https://example.com/menu/")
    results = analyze(make_site(a, b))
    titles = by_id(results, "keyword.duplicate_titles")
    descriptions = by_id(results, "keyword.duplicate_meta_descriptions")
    assert titles.status is Status.FAIL and titles.page is None
    assert "https://example.com/menu/" in titles.evidence
    assert descriptions.status is Status.FAIL


def test_distinct_titles_pass_duplicate_check():
    a = make_page(url="https://example.com/")
    b = make_page(
        url="https://example.com/menu/",
        title="Menu | Example Bakery Brooklyn",
        meta_description="See our full menu of breads, pastries and cakes baked fresh every day.",
    )
    assert by_id(analyze(make_site(a, b)), "keyword.duplicate_titles").status is Status.PASS


def test_single_page_skips_duplicate_checks():
    ids = {f.check_id for f in analyze(make_site())}
    assert "keyword.duplicate_titles" not in ids


def test_javascript_page_with_missing_tags_is_unavailable_not_fail():
    page = make_page(
        title=None, meta_description=None, headings=(), text="", likely_js_rendered=True
    )
    results = analyze(make_site(page))
    for cid in ("keyword.title", "keyword.meta_description", "keyword.h1"):
        item = by_id(results, cid)
        assert item.status is Status.UNAVAILABLE
        assert "JavaScript" in item.evidence
    assert not any(f.status is Status.FAIL for f in results)


def test_empty_site_returns_no_findings():
    from crawler.models import CrawlStatus, SiteData

    site = SiteData(start_url="https://example.com/", status=CrawlStatus.BLOCKED)
    assert analyze(site) == []
