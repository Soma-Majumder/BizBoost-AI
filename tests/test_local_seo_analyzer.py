from analyzers.local_seo import analyze
from crawler.models import CrawlStatus, Link, SiteData
from findings import Category, Status
from tests.factories import make_page, make_site

BAKERY_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Bakery",
    "name": "Example Bakery",
    "address": {"@type": "PostalAddress", "addressLocality": "Brooklyn"},
}


def local_page(**overrides):
    base = dict(
        has_map_embed=True,
        structured_data=(BAKERY_SCHEMA,),
        external_links=(Link("https://www.yelp.com/biz/example-bakery", "Yelp"),),
    )
    base.update(overrides)
    return make_page(**base)


def by_id(findings, check_id):
    matches = [f for f in findings if f.check_id == check_id]
    assert matches, f"no finding for {check_id}"
    return matches[0]


def has(findings, check_id):
    return any(f.check_id == check_id for f in findings)


def test_healthy_local_business_passes_everything():
    results = analyze(make_site(local_page()))
    assert results and all(f.status is Status.PASS for f in results)
    assert all(f.category is Category.LOCAL_SEO for f in results)
    assert all(f.evidence for f in results)


def test_missing_phone_and_address_fail():
    results = analyze(make_site(local_page(phones=(), addresses=())))
    assert by_id(results, "local.phone").status is Status.FAIL
    assert by_id(results, "local.address").status is Status.FAIL
    assert not has(results, "local.phone_consistency")


def test_phone_only_on_another_page_warns():
    home = local_page(phones=())
    contact = local_page(url="https://example.com/contact-us/")
    item = by_id(analyze(make_site(home, contact)), "local.phone")
    assert item.status is Status.WARN and "contact-us" in item.evidence


def test_different_phone_formats_of_same_number_are_consistent():
    home = local_page(phones=("(718) 555-0100",))
    other = local_page(url="https://example.com/contact-us/", phones=("+1 718-555-0100",))
    assert by_id(analyze(make_site(home, other)), "local.phone_consistency").status is Status.PASS


def test_different_phone_numbers_warn():
    home = local_page(phones=("(718) 555-0100",))
    other = local_page(url="https://example.com/contact-us/", phones=("(212) 555-0199",))
    item = by_id(analyze(make_site(home, other)), "local.phone_consistency")
    assert item.status is Status.WARN and "212" in item.evidence


def test_no_structured_data_fails_and_organization_only_warns():
    assert by_id(analyze(make_site(local_page(structured_data=()))), "local.schema_markup").status \
        is Status.FAIL
    org = local_page(structured_data=({"@type": "Organization"},))
    assert by_id(analyze(make_site(org)), "local.schema_markup").status is Status.WARN


def test_schema_inside_graph_and_type_lists_is_found():
    graph = {"@graph": [{"@type": "WebSite"}, {"@type": ["Thing", "Restaurant"]}]}
    page = local_page(structured_data=(graph,))
    assert by_id(analyze(make_site(page)), "local.schema_markup").status is Status.PASS


def test_missing_map_and_listings_warn():
    page = local_page(has_map_embed=False, external_links=())
    results = analyze(make_site(page))
    assert by_id(results, "local.map").status is Status.WARN
    assert by_id(results, "local.directory_listings").status is Status.WARN


def test_city_missing_from_title_warns_only_when_city_is_known():
    page = local_page(title="Example Bakery | Fresh Bread", meta_description="Fresh bread daily.")
    item = by_id(analyze(make_site(page)), "local.city_in_title")
    assert item.status is Status.WARN and "Brooklyn" in item.evidence
    assert not has(analyze(make_site(local_page(structured_data=()))), "local.city_in_title")


def test_not_local_business_returns_single_unavailable_finding():
    results = analyze(make_site(), local_relevant=False)
    assert len(results) == 1
    assert results[0].status is Status.UNAVAILABLE and results[0].evidence


def test_javascript_homepage_with_nothing_found_is_unavailable_not_fail():
    page = make_page(phones=(), addresses=(), social_links=(), likely_js_rendered=True)
    results = analyze(make_site(page))
    for cid in ("local.phone", "local.address", "local.schema_markup", "local.map"):
        assert by_id(results, cid).status is Status.UNAVAILABLE
    assert not any(f.status is Status.FAIL for f in results)


def test_site_with_no_pages_returns_no_findings():
    site = SiteData(start_url="https://example.com/", status=CrawlStatus.BLOCKED)
    assert analyze(site) == []
