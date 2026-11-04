from analyzers.technical import analyze
from crawler.models import CrawlStatus, SiteData
from findings import Category, Source, Status, finding
from tests.factories import make_page, make_site


def by_id(findings, check_id, page=None):
    matches = [f for f in findings if f.check_id == check_id and (page is None or f.page == page)]
    assert matches, f"no finding for {check_id}"
    return matches[0]


def test_healthy_site_passes_everything():
    results = analyze(make_site())
    assert results and all(f.status is Status.PASS for f in results)
    assert all(f.category is Category.TECHNICAL_SEO for f in results)
    assert all(f.evidence for f in results)


def test_http_page_fails_https_check():
    site = make_site(make_page(url="http://example.com/", canonical="http://example.com/"))
    item = by_id(analyze(site), "technical.https")
    assert item.status is Status.FAIL and "http://example.com/" in item.evidence


def test_noindex_fails():
    site = make_site(make_page(meta_robots="noindex, nofollow"))
    assert by_id(analyze(site), "technical.noindex").status is Status.FAIL


def test_error_status_pages_fail_and_name_the_status():
    site = make_site(make_page(), make_page(url="https://example.com/old/", status_code=404))
    item = by_id(analyze(site), "technical.broken_pages")
    assert item.status is Status.FAIL and "404" in item.evidence


def test_missing_sitemap_fails_and_missing_robots_warns():
    site = make_site(sitemap_url=None, sitemap_page_count=0, robots_txt_found=False)
    results = analyze(site)
    assert by_id(results, "technical.sitemap").status is Status.FAIL
    assert by_id(results, "technical.robots_txt").status is Status.WARN


def test_slow_homepage_warns():
    site = make_site(make_page(fetch_seconds=4.2))
    item = by_id(analyze(site), "technical.response_time")
    assert item.status is Status.WARN and "4.2" in item.evidence


def test_missing_canonical_warns_and_foreign_canonical_warns():
    missing = by_id(analyze(make_site(make_page(canonical=None))), "technical.canonical")
    assert missing.status is Status.WARN
    other = make_page(canonical="https://other.com/")
    assert by_id(analyze(make_site(other)), "technical.canonical").status is Status.WARN


def test_canonical_trailing_slash_and_case_do_not_matter():
    page = make_page(url="https://Example.com/menu", canonical="https://example.com/menu/")
    assert by_id(analyze(make_site(page)), "technical.canonical").status is Status.PASS


def test_missing_viewport_fails_and_missing_lang_warns():
    results = analyze(make_site(make_page(has_viewport=False, lang=None)))
    assert by_id(results, "technical.viewport").status is Status.FAIL
    assert by_id(results, "technical.lang").status is Status.WARN


def test_page_checks_are_per_page():
    site = make_site(make_page(), make_page(url="https://example.com/menu/", has_viewport=False,
                                            canonical="https://example.com/menu/"))
    assert by_id(analyze(site), "technical.viewport", "https://example.com/").status is Status.PASS
    assert by_id(analyze(site), "technical.viewport", "https://example.com/menu/").status \
        is Status.FAIL


def test_javascript_page_missing_tags_is_unavailable_not_fail():
    page = make_page(canonical=None, has_viewport=False, lang=None, likely_js_rendered=True)
    results = analyze(make_site(page))
    for cid in ("technical.canonical", "technical.viewport", "technical.lang"):
        item = by_id(results, cid)
        assert item.status is Status.UNAVAILABLE and "JavaScript" in item.evidence


def test_extra_findings_are_included():
    speed = finding("technical.pagespeed_mobile", "technical_seo", "pass", "Mobile score 91",
                    source=Source.PAGESPEED)
    results = analyze(make_site(), extra=[speed])
    assert by_id(results, "technical.pagespeed_mobile").source is Source.PAGESPEED


def test_no_pages_returns_only_extra():
    site = SiteData(start_url="https://example.com/", status=CrawlStatus.BLOCKED)
    assert analyze(site) == []
    speed = finding("technical.pagespeed_mobile", "technical_seo", "unavailable", "Timed out",
                    source=Source.PAGESPEED)
    assert analyze(site, extra=[speed]) == [speed]
