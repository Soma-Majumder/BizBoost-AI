import pytest

from crawler.models import CrawlStatus, Heading, NotScanned, SiteData
from tests.factories import make_page, make_site


def test_healthy_sample_page_has_expected_properties():
    page = make_page()
    assert page.is_https
    assert page.word_count > 100
    assert [h.text for h in page.h1s] == ["Example Bakery"]


def test_http_page_is_not_https():
    assert not make_page(url="http://example.com/").is_https


def test_missing_things_are_none_or_empty_by_default():
    page = make_page(title=None, meta_description=None, headings=(), images=())
    assert page.title is None and page.meta_description is None
    assert page.h1s == ()


def test_image_alt_distinguishes_missing_from_empty():
    from crawler.models import Image

    assert Image("a.jpg", None).alt is None
    assert Image("a.jpg", "").alt == ""


def test_homepage_is_first_page_and_scanned_urls_listed():
    site = make_site(make_page(), make_page(url="https://example.com/menu/"))
    assert site.homepage.url == "https://example.com/"
    assert site.scanned_urls == ("https://example.com/", "https://example.com/menu/")


def test_blocked_site_has_no_pages_and_a_message():
    site = SiteData(
        start_url="https://example.com/",
        status=CrawlStatus.BLOCKED,
        not_scanned=(NotScanned("https://example.com/", "Blocked by robots.txt"),),
        message="This website does not allow scanning.",
    )
    assert site.homepage is None
    assert site.scanned_urls == ()


def test_page_data_is_immutable():
    with pytest.raises(Exception):
        make_page().title = "changed"


def test_js_flag_defaults_to_false():
    assert make_page().likely_js_rendered is False
    assert make_page(likely_js_rendered=True).likely_js_rendered is True
