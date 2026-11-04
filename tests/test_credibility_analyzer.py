from analyzers.credibility import NO_PROVIDER, analyze
from crawler.models import CrawlStatus, Link, SiteData
from findings import Category, Source, Status, finding
from tests.factories import make_page, make_site


def trusted_page(**overrides):
    base = dict(
        internal_links=(
            Link("https://example.com/contact-us/", "Contact"),
            Link("https://example.com/about/", "About"),
            Link("https://example.com/privacy-policy/", "Privacy"),
        ),
        text="Fresh bread baked daily. " * 60 + " What our customers say: wonderful!",
    )
    base.update(overrides)
    return make_page(**base)


def by_id(findings, check_id):
    matches = [f for f in findings if f.check_id == check_id]
    assert matches, f"no finding for {check_id}"
    return matches[0]


def test_trusted_site_passes_everything_except_unavailable_backlinks():
    results = analyze(make_site(trusted_page()))
    assert all(f.category is Category.CREDIBILITY_BACKLINKS for f in results)
    assert all(f.evidence for f in results)
    for f in results:
        expected = Status.UNAVAILABLE if f.check_id == "credibility.backlinks" else Status.PASS
        assert f.status is expected, f.check_id


def test_backlinks_unavailable_without_provider_never_zero():
    item = by_id(analyze(make_site(trusted_page())), "credibility.backlinks")
    assert item.status is Status.UNAVAILABLE
    assert item.evidence == NO_PROVIDER
    assert item.source is Source.BACKLINK_PROVIDER


def test_provider_findings_replace_the_unavailable_placeholder():
    provider = finding("credibility.backlinks", "credibility_backlinks", "pass",
                       "42 inbound links from 12 sites", source="backlink_provider", weight=2)
    results = analyze(make_site(trusted_page()), backlink_findings=[provider])
    backlinks = [f for f in results if f.check_id == "credibility.backlinks"]
    assert backlinks == [provider]


def test_missing_contact_about_privacy_reviews_and_social():
    page = make_page(internal_links=(), social_links=(), external_links=(),
                     phones=(), emails=(), text="Fresh bread. " * 60)
    results = analyze(make_site(page))
    assert by_id(results, "credibility.contact_page").status is Status.FAIL
    assert by_id(results, "credibility.about_page").status is Status.FAIL
    assert by_id(results, "credibility.social_profiles").status is Status.WARN
    assert by_id(results, "credibility.reviews").status is Status.WARN
    assert by_id(results, "credibility.privacy_policy").status is Status.WARN


def test_contact_details_without_contact_page_warns_not_fails():
    page = make_page(internal_links=(), phones=("(718) 555-0100",))
    assert by_id(analyze(make_site(page)), "credibility.contact_page").status is Status.WARN


def test_contact_page_found_by_url_of_scanned_page():
    home = make_page(internal_links=())
    contact = make_page(url="https://example.com/contact-us/", internal_links=())
    assert by_id(analyze(make_site(home, contact)), "credibility.contact_page").status \
        is Status.PASS


def test_review_schema_and_review_site_links_count():
    schema = make_page(structured_data=({"@type": "LocalBusiness",
                                         "aggregateRating": {}}, {"@type": "AggregateRating"}),
                       text="Fresh bread. " * 60)
    assert by_id(analyze(make_site(schema)), "credibility.reviews").status is Status.PASS
    yelp = make_page(external_links=(Link("https://www.yelp.com/biz/x", "Yelp"),),
                     text="Fresh bread. " * 60)
    assert by_id(analyze(make_site(yelp)), "credibility.reviews").status is Status.PASS


def test_social_profiles_ignore_non_social_hosts():
    page = make_page(social_links=("https://www.yelp.com/biz/x",), external_links=())
    assert by_id(analyze(make_site(page)), "credibility.social_profiles").status is Status.WARN
    page = make_page(social_links=("https://www.instagram.com/x",), external_links=())
    assert by_id(analyze(make_site(page)), "credibility.social_profiles").status is Status.PASS


def test_javascript_homepage_with_nothing_found_is_unavailable_not_fail():
    page = make_page(internal_links=(), social_links=(), external_links=(), phones=(),
                     emails=(), text="", likely_js_rendered=True)
    results = analyze(make_site(page))
    for cid in ("credibility.contact_page", "credibility.about_page", "credibility.reviews",
                "credibility.social_profiles", "credibility.privacy_policy"):
        item = by_id(results, cid)
        assert item.status is Status.UNAVAILABLE and "JavaScript" in item.evidence
    assert not any(f.status is Status.FAIL for f in results)


def test_site_with_no_pages_returns_no_findings():
    site = SiteData(start_url="https://example.com/", status=CrawlStatus.BLOCKED)
    assert analyze(site) == []
