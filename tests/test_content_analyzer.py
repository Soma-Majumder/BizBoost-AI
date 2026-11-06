import pytest

from analyzers.content import _reading_ease, analyze
from crawler.models import CrawlStatus, Heading, Image, SiteData
from findings import Category, Status
from tests.factories import make_page, make_site

HARD_TEXT = (
    "Notwithstanding considerable organizational complexity, institutional "
    "stakeholders systematically operationalize comprehensive methodological "
    "frameworks, necessitating multidimensional interdisciplinary collaboration. "
) * 12


def by_id(findings, check_id, page=None):
    matches = [f for f in findings if f.check_id == check_id and (page is None or f.page == page)]
    assert matches, f"no finding for {check_id}"
    return matches[0]


def has(findings, check_id):
    return any(f.check_id == check_id for f in findings)


def test_healthy_page_passes_everything():
    results = analyze(make_site())
    assert results and all(f.status is Status.PASS for f in results)
    assert all(f.category is Category.CONTENT_QUALITY for f in results)
    assert all(f.evidence for f in results)


@pytest.mark.parametrize(
    "text, status",
    [("word " * 50, Status.FAIL), ("word " * 150, Status.WARN), ("word " * 300, Status.PASS)],
)
def test_word_count_thresholds(text, status):
    assert by_id(analyze(make_site(make_page(text=text))), "content.word_count").status is status


def test_hard_to_read_text_is_flagged():
    item = by_id(analyze(make_site(make_page(text=HARD_TEXT))), "content.readability")
    assert item.status in (Status.WARN, Status.FAIL)
    assert "Reading ease" in item.evidence


def test_menu_style_text_without_sentences_is_unavailable_not_scored():
    menu = "Veggie Burger with fries and salad $12 Tofu Pad Thai with peanuts $14 " * 20
    item = by_id(analyze(make_site(make_page(text=menu))), "content.readability")
    assert item.status is Status.UNAVAILABLE
    assert "mostly lists or short items" in item.evidence


def test_normal_prose_is_still_scored():
    prose = "We cook fresh food every day. Come and eat with us. Our menu is simple and tasty. " * 8
    assert by_id(analyze(make_site(make_page(text=prose))), "content.readability").status is Status.PASS


def test_short_text_skips_readability():
    assert not has(analyze(make_site(make_page(text="Short page."))), "content.readability")
    assert _reading_ease("Short page.") is None


def test_non_english_page_readability_is_unavailable():
    item = by_id(analyze(make_site(make_page(lang="es"))), "content.readability")
    assert item.status is Status.UNAVAILABLE


def test_skipped_heading_level_warns():
    page = make_page(headings=(Heading(1, "Home"), Heading(3, "Deep")))
    assert by_id(analyze(make_site(page)), "content.heading_structure").status is Status.WARN


def test_long_page_without_subheadings_warns():
    page = make_page(headings=(Heading(1, "Home"),), text="word. " * 400)
    item = by_id(analyze(make_site(page)), "content.heading_structure")
    assert item.status is Status.WARN and "subheadings" in item.evidence


def test_no_headings_is_left_to_the_keyword_analyzer():
    assert not has(analyze(make_site(make_page(headings=()))), "content.heading_structure")


def test_image_alt_missing_some_warns_most_fails_empty_alt_is_fine():
    some = (Image("a.jpg", "A"), Image("b.jpg", "B"), Image("c.jpg", None))
    most = (Image("a.jpg", None), Image("b.jpg", None), Image("c.jpg", "C"))
    decorative = (Image("a.jpg", ""), Image("b.jpg", "B"))
    assert by_id(analyze(make_site(make_page(images=some))), "content.image_alt").status \
        is Status.WARN
    assert by_id(analyze(make_site(make_page(images=most))), "content.image_alt").status \
        is Status.FAIL
    assert by_id(analyze(make_site(make_page(images=decorative))), "content.image_alt").status \
        is Status.PASS


def test_no_images_warns():
    assert by_id(analyze(make_site(make_page(images=()))), "content.image_alt").status \
        is Status.WARN


def test_no_internal_links_warns():
    item = by_id(analyze(make_site(make_page(internal_links=()))), "content.internal_links")
    assert item.status is Status.WARN


def test_identical_text_across_pages_fails():
    a = make_page()
    b = make_page(url="https://example.com/menu/")
    item = by_id(analyze(make_site(a, b)), "content.duplicate_content")
    assert item.status is Status.FAIL and item.page is None
    assert "https://example.com/menu/" in item.evidence


def test_different_text_passes_duplicate_check_and_single_page_skips_it():
    a = make_page()
    b = make_page(url="https://example.com/menu/", text="Our menu has pastries and cakes. " * 60)
    assert by_id(analyze(make_site(a, b)), "content.duplicate_content").status is Status.PASS
    assert not has(analyze(make_site()), "content.duplicate_content")


def test_javascript_page_with_little_content_is_unavailable_not_fail():
    page = make_page(text="", images=(), internal_links=(), likely_js_rendered=True)
    results = analyze(make_site(page))
    for cid in ("content.word_count", "content.image_alt", "content.internal_links"):
        item = by_id(results, cid)
        assert item.status is Status.UNAVAILABLE and "JavaScript" in item.evidence
    assert not any(f.status is Status.FAIL for f in results)


def test_site_with_no_pages_returns_no_findings():
    site = SiteData(start_url="https://example.com/", status=CrawlStatus.BLOCKED)
    assert analyze(site) == []
