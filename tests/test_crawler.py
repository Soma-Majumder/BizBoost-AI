import pytest
import requests

from crawler.models import CrawlStatus
from crawler.website_crawler import FetchError, FetchResult, HttpFetcher, crawl

BASE = "https://example.com"


def page_html(title, links=(), words=120):
    anchors = "".join(f'<a href="{href}">{href}</a>' for href in links)
    return (
        f"<html lang='en'><head><title>{title}</title></head>"
        f"<body><h1>{title}</h1><p>{'word ' * words}</p>{anchors}</body></html>"
    ).encode()


class FakeWeb:
    """A pretend website. Maps URL -> (status, content_type, body) or an exception."""

    def __init__(self, routes):
        self.routes = routes
        self.requested: list[str] = []

    def __call__(self, url):
        self.requested.append(url)
        route = self.routes.get(url)
        if route is None:
            return FetchResult(url, 404, "text/html", b"", 0.1)
        if isinstance(route, Exception):
            raise route
        status, content_type, body = route
        if isinstance(body, str):
            body = body.encode()
        return FetchResult(url, status, content_type, body, 0.1)


def html(body):
    return (200, "text/html; charset=utf-8", body)


def sitemap(*urls):
    locs = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return (200, "application/xml",
            f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>')


def run(routes, **kw):
    web = FakeWeb(routes)
    kw.setdefault("delay", 0)
    return crawl(f"{BASE}/", fetch=web, **kw), web


def test_homepage_then_sitemap_then_links_in_that_order():
    site, _ = run({
        f"{BASE}/robots.txt": (200, "text/plain", f"Sitemap: {BASE}/sitemap.xml\n"),
        f"{BASE}/sitemap.xml": sitemap(f"{BASE}/", f"{BASE}/menu/", f"{BASE}/about/"),
        f"{BASE}/": html(page_html("Home", links=["/contact/", "/menu/"])),
        f"{BASE}/menu/": html(page_html("Menu")),
        f"{BASE}/about/": html(page_html("About")),
        f"{BASE}/contact/": html(page_html("Contact")),
    })
    assert site.status is CrawlStatus.OK
    assert site.scanned_urls == (f"{BASE}/", f"{BASE}/menu/", f"{BASE}/about/", f"{BASE}/contact/")
    assert site.robots_txt_found and site.sitemap_url == f"{BASE}/sitemap.xml"
    assert site.sitemap_page_count == 3


def test_sitemap_index_is_followed():
    site, _ = run({
        f"{BASE}/robots.txt": (404, "text/html", ""),
        f"{BASE}/sitemap.xml": (200, "application/xml",
            f'<sitemapindex><sitemap><loc>{BASE}/page-sitemap.xml</loc></sitemap></sitemapindex>'),
        f"{BASE}/page-sitemap.xml": sitemap(f"{BASE}/", f"{BASE}/menu/"),
        f"{BASE}/": html(page_html("Home")),
        f"{BASE}/menu/": html(page_html("Menu")),
    })
    assert site.scanned_urls == (f"{BASE}/", f"{BASE}/menu/")
    assert site.sitemap_page_count == 2 and not site.robots_txt_found


def test_robots_sitemap_line_wins_and_missing_sitemap_is_reported():
    site, _ = run({f"{BASE}/": html(page_html("Home"))})
    assert site.status is CrawlStatus.OK
    assert site.sitemap_url is None and site.sitemap_page_count == 0 and not site.robots_txt_found


def test_max_pages_is_respected_and_duplicates_skipped():
    links = [f"/p{i}/" for i in range(30)] + ["/p1/", "/p1/#frag", f"{BASE}/p2"]
    routes = {f"{BASE}/": html(page_html("Home", links=links))}
    routes.update({f"{BASE}/p{i}/": html(page_html(f"P{i}")) for i in range(30)})
    site, _ = run(routes)
    assert len(site.pages) == 10
    assert len(set(site.scanned_urls)) == 10


def test_off_site_and_non_page_links_are_not_crawled():
    site, web = run({
        f"{BASE}/": html(page_html("Home", links=["https://other.com/x", "/menu.pdf", "/img.png",
                                                  "/real/"])),
        f"{BASE}/real/": html(page_html("Real")),
    })
    assert site.scanned_urls == (f"{BASE}/", f"{BASE}/real/")
    assert not any("other.com" in u or u.endswith((".pdf", ".png")) for u in web.requested)


def test_robots_disallow_everything_blocks_the_scan_without_touching_the_site():
    site, web = run({f"{BASE}/robots.txt": (200, "text/plain", "User-agent: *\nDisallow: /\n"),
                     f"{BASE}/": html(page_html("Home"))})
    assert site.status is CrawlStatus.BLOCKED
    assert "does not allow scanning" in site.message
    assert site.pages == () and site.not_scanned
    assert f"{BASE}/" not in web.requested


def test_robots_disallowed_subpage_is_listed_as_not_scanned():
    site, web = run({
        f"{BASE}/robots.txt": (200, "text/plain", "User-agent: *\nDisallow: /private/\n"),
        f"{BASE}/": html(page_html("Home", links=["/private/", "/ok/"])),
        f"{BASE}/ok/": html(page_html("OK")),
    })
    assert site.scanned_urls == (f"{BASE}/", f"{BASE}/ok/")
    assert [(n.url, n.reason) for n in site.not_scanned] == [
        (f"{BASE}/private/", "Blocked by the site's robots.txt")]
    assert f"{BASE}/private/" not in web.requested


@pytest.mark.parametrize("status", [401, 403, 429])
def test_firewall_refusal_on_homepage_is_blocked(status):
    site, _ = run({f"{BASE}/": (status, "text/html", "denied")})
    assert site.status is CrawlStatus.BLOCKED and "does not allow scanning" in site.message


@pytest.mark.parametrize("route", [(404, "text/html", ""), (503, "text/html", ""),
                                   (200, "application/pdf", b"%PDF"), FetchError("Too slow.")])
def test_unreachable_homepage(route):
    site, _ = run({f"{BASE}/": route})
    assert site.status is CrawlStatus.UNREACHABLE and site.message and site.pages == ()


def test_failed_subpages_go_to_not_scanned_but_error_pages_are_still_pages():
    site, _ = run({
        f"{BASE}/": html(page_html("Home", links=["/slow/", "/gone/", "/denied/", "/file/"])),
        f"{BASE}/slow/": FetchError("The page took too long to respond."),
        f"{BASE}/gone/": (404, "text/html", page_html("Gone")),
        f"{BASE}/denied/": (403, "text/html", "no"),
        f"{BASE}/file/": (200, "application/pdf", b"%PDF"),
    })
    assert site.status is CrawlStatus.OK
    assert {p.url: p.status_code for p in site.pages} == {f"{BASE}/": 200, f"{BASE}/gone/": 404}
    reasons = {n.url: n.reason for n in site.not_scanned}
    assert reasons[f"{BASE}/slow/"] == "The page took too long to respond."
    assert reasons[f"{BASE}/denied/"] == "The site refused our request"
    assert reasons[f"{BASE}/file/"] == "Not a web page"


def test_redirect_to_another_website_is_not_scanned():
    class Redirecting(FakeWeb):
        def __call__(self, url):
            if url.endswith("/away/"):
                return FetchResult("https://evil.com/", 200, "text/html", page_html("Evil"), 0.1,
                                   requested_url=url)
            return super().__call__(url)

    web = Redirecting({f"{BASE}/": html(page_html("Home", links=["/away/"]))})
    site = crawl(f"{BASE}/", fetch=web, delay=0)
    assert site.scanned_urls == (f"{BASE}/",)
    assert site.not_scanned[0].reason == "Redirected to a different website"


def test_time_budget_skips_remaining_pages_with_a_reason():
    routes = {f"{BASE}/": html(page_html("Home", links=["/a/", "/b/"]))}
    site, _ = run(routes, time_budget=-1)
    assert site.scanned_urls == (f"{BASE}/",)
    assert {n.reason for n in site.not_scanned} == {"Skipped to keep the audit fast"}


def test_progress_callback_reports_counts():
    calls = []
    run({f"{BASE}/": html(page_html("Home", links=["/a/"])), f"{BASE}/a/": html(page_html("A"))},
        on_progress=lambda done, total: calls.append((done, total)))
    assert calls == [(1, 2), (2, 2)]


def test_every_url_the_crawler_fetches_is_on_the_same_site():
    site, web = run({f"{BASE}/": html(page_html("Home", links=["/a/", "https://other.com/z"])),
                     f"{BASE}/a/": html(page_html("A"))})
    assert all(u.startswith(BASE) for u in web.requested)


# --- HttpFetcher: safety checks, no real network ---------------------------------------


class FakeResponse:
    def __init__(self, status=200, headers=None, body=b"<html></html>"):
        self.status_code, self.headers, self._body = status, headers or {}, body
        self.is_redirect = status in (301, 302, 303, 307, 308)

    def iter_content(self, chunk_size):
        yield self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = responses, []

    def get(self, url, **kwargs):
        self.calls.append(url)
        item = self.responses[url]
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture(autouse=True)
def public_dns(monkeypatch):
    """Treat every hostname as resolving to a public address."""
    monkeypatch.setattr("url_validator.socket.getaddrinfo",
                        lambda host, *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))])


def test_fetcher_follows_redirect_and_records_requested_url():
    session = FakeSession({
        "http://example.com/": FakeResponse(301, {"location": "https://example.com/"}),
        "https://example.com/": FakeResponse(200, {"content-type": "text/html"}),
    })
    result = HttpFetcher(session)("http://example.com/")
    assert result.url == "https://example.com/" and result.requested_url == "http://example.com/"
    assert result.status == 200 and result.is_html


def test_fetcher_refuses_redirect_to_private_address_without_connecting():
    session = FakeSession({"https://example.com/": FakeResponse(302, {"location": "http://127.0.0.1/admin"})})
    with pytest.raises(FetchError, match="safely"):
        HttpFetcher(session)("https://example.com/")
    assert session.calls == ["https://example.com/"]


def test_fetcher_gives_up_on_redirect_loops():
    session = FakeSession({"https://example.com/": FakeResponse(302, {"location": "https://example.com/"})})
    with pytest.raises(FetchError, match="redirecting"):
        HttpFetcher(session)("https://example.com/")


@pytest.mark.parametrize("error, message", [
    (requests.exceptions.Timeout(), "too long"),
    (requests.exceptions.SSLError(), "certificate"),
    (requests.exceptions.ConnectionError(), "could not be reached"),
])
def test_fetcher_turns_network_errors_into_plain_messages(error, message):
    with pytest.raises(FetchError, match=message):
        HttpFetcher(FakeSession({"https://example.com/": error}))("https://example.com/")


def test_fetcher_caps_body_size_and_identifies_the_crawler():
    from crawler.website_crawler import MAX_BODY_BYTES

    session = FakeSession({"https://example.com/": FakeResponse(200, {"content-type": "text/html"},
                                                                b"x" * (MAX_BODY_BYTES + 5000))})
    result = HttpFetcher(session)("https://example.com/")
    assert len(result.body) == MAX_BODY_BYTES
