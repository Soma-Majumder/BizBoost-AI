"""Website crawler: robots.txt, homepage, XML sitemap, internal links (max 10 pages).

``crawl(start_url)`` returns a ``SiteData``. It never raises for site problems: a
blocked site gives ``CrawlStatus.BLOCKED`` and an unreachable one ``UNREACHABLE``, each
with a plain-language message. Pages it cannot fetch go in ``not_scanned``, never in
``pages``, so they are never scored as failures.

Safety: every URL, including each redirect hop, goes through ``ensure_safe_url``
before anything connects to it. The crawler identifies itself, follows robots.txt and
waits briefly between requests.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from crawler.models import CrawlStatus, NotScanned, PageData, SiteData
from crawler.parser import parse_page, same_site
from url_validator import USER_AGENT, URLValidationError, ensure_safe_url

MAX_PAGES = 10
MAX_REDIRECTS = 5
MAX_BODY_BYTES = 2_000_000
REQUEST_TIMEOUT = (5, 10)  # (connect, read) seconds
CRAWL_DELAY_SECONDS = 0.2
TIME_BUDGET_SECONDS = 90.0  # leaves room for the rest of the 2-minute audit target
MAX_CHILD_SITEMAPS = 5
MAX_SITEMAP_URLS = 200
BLOCKING_STATUSES = {401, 403, 429}  # the site is refusing automated visitors

_SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".zip", ".mp3", ".mp4",
    ".mov", ".css", ".js", ".xml", ".json", ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt",
    ".pptx", ".gz",
)

NOT_ALLOWED = (
    "This website does not allow scanning. Its settings ask automated visitors to stay "
    "out, so we stopped and did not scan it."
)


class FetchError(Exception):
    """A request failed. ``str(error)`` is a plain-language reason."""


@dataclass(frozen=True)
class FetchResult:
    url: str  # final URL after redirects
    status: int
    content_type: str
    body: bytes
    seconds: float
    requested_url: str | None = None  # set when a redirect changed the URL

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    @property
    def is_html(self) -> bool:
        return "html" in self.content_type.lower() or not self.content_type


Fetcher = Callable[[str], FetchResult]


class HttpFetcher:
    """Fetches one URL, following redirects by hand so every hop is checked first."""

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    def __call__(self, url: str) -> FetchResult:
        start = time.monotonic()
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            try:
                current = ensure_safe_url(current)
            except URLValidationError as error:
                raise FetchError("A link or redirect pointed somewhere we can't safely scan.") from error
            try:
                with self.session.get(
                    current, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT,
                    allow_redirects=False, stream=True,
                ) as response:
                    if response.is_redirect and response.headers.get("location"):
                        current = urljoin(current, response.headers["location"])
                        continue
                    content_type = response.headers.get("content-type", "")
                    body = b""
                    if response.status_code < 400 or "html" in content_type.lower():
                        body = _read_limited(response)
                    return FetchResult(
                        url=current, status=response.status_code, content_type=content_type,
                        body=body, seconds=time.monotonic() - start,
                        requested_url=url if current != url else None,
                    )
            except requests.exceptions.Timeout as error:
                raise FetchError("The page took too long to respond.") from error
            except requests.exceptions.SSLError as error:
                raise FetchError("The page has a security certificate problem.") from error
            except requests.exceptions.RequestException as error:
                raise FetchError("The page could not be reached.") from error
        raise FetchError("The page keeps redirecting and never settles.")


def _read_limited(response: requests.Response) -> bytes:
    chunks, size = [], 0
    for chunk in response.iter_content(chunk_size=65536):
        chunks.append(chunk)
        size += len(chunk)
        if size >= MAX_BODY_BYTES:
            break
    return b"".join(chunks)[:MAX_BODY_BYTES]


def crawl(
    start_url: str,
    fetch: Fetcher | None = None,
    max_pages: int = MAX_PAGES,
    delay: float = CRAWL_DELAY_SECONDS,
    time_budget: float = TIME_BUDGET_SECONDS,
    on_progress: Callable[[int, int], None] | None = None,
) -> SiteData:
    """Scan up to ``max_pages`` pages: homepage, then sitemap pages, then homepage links."""
    fetch = fetch or HttpFetcher()
    started = time.monotonic()
    origin = _origin(start_url)

    robots, robots_found, robots_sitemaps = _read_robots(fetch, origin)

    # --- Homepage -------------------------------------------------------------------
    if not robots.can_fetch(USER_AGENT, start_url):
        return SiteData(
            start_url=start_url, status=CrawlStatus.BLOCKED, message=NOT_ALLOWED,
            not_scanned=(NotScanned(start_url, "Blocked by the site's robots.txt"),),
            robots_txt_found=robots_found,
        )
    try:
        home_result = fetch(start_url)
    except FetchError as error:
        return _failed(start_url, CrawlStatus.UNREACHABLE, str(error), robots_found)
    if home_result.status in BLOCKING_STATUSES:
        return _failed(start_url, CrawlStatus.BLOCKED, NOT_ALLOWED, robots_found,
                       "The site refused our request")
    if home_result.status >= 400 or not home_result.is_html:
        return _failed(
            start_url, CrawlStatus.UNREACHABLE,
            "We couldn't load a web page from this address. Please check it and try again.",
            robots_found,
        )

    homepage = _to_page(home_result)
    site_url = homepage.url  # the final address, used to decide what is on the same site

    # --- Candidate pages: homepage, then sitemap, then homepage links -------------------
    sitemap_url, sitemap_urls = _read_sitemap(fetch, origin, robots_sitemaps, site_url)
    candidates = _unique(
        [url for url in [*sitemap_urls, *(l.url for l in homepage.internal_links)]
         if same_site(url, site_url) and _looks_like_page(url)],
        skip={_key(site_url), _key(start_url)},
    )

    pages: list[PageData] = [homepage]
    not_scanned: list[NotScanned] = []
    total = min(max_pages, 1 + len(candidates))
    _report(on_progress, 1, total)

    for url in candidates:
        if len(pages) + len(not_scanned) >= max_pages:
            break
        if time.monotonic() - started > time_budget:
            not_scanned.append(NotScanned(url, "Skipped to keep the audit fast"))
            continue
        if not robots.can_fetch(USER_AGENT, url):
            not_scanned.append(NotScanned(url, "Blocked by the site's robots.txt"))
            continue
        time.sleep(delay)
        page, reason = _fetch_page(fetch, url, site_url)
        if page:
            pages.append(page)
        else:
            not_scanned.append(NotScanned(url, reason))
        _report(on_progress, len(pages) + len(not_scanned), total)

    return SiteData(
        start_url=start_url, status=CrawlStatus.OK, pages=tuple(pages),
        not_scanned=tuple(not_scanned), robots_txt_found=robots_found,
        sitemap_url=sitemap_url, sitemap_page_count=len(sitemap_urls),
    )


# --------------------------------------------------------------------------------------


def _report(callback, done: int, total: int) -> None:
    if callback:
        callback(done, total)


def _failed(start_url, status, message, robots_found, reason=None) -> SiteData:
    return SiteData(
        start_url=start_url, status=status, message=message, robots_txt_found=robots_found,
        not_scanned=(NotScanned(start_url, reason or message),),
    )


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def _key(url: str) -> str:
    """Identity for duplicate detection: no fragment, no trailing slash, lowercase host."""
    parts = urlsplit(urldefrag(url)[0])
    path = parts.path.rstrip("/") or "/"
    return f"{parts.scheme}://{(parts.hostname or '').lower().removeprefix('www.')}{path}?{parts.query}"


def _unique(urls: list[str], skip: set[str]) -> list[str]:
    seen, result = set(skip), []
    for url in urls:
        url = urldefrag(url)[0]
        if _key(url) not in seen:
            seen.add(_key(url))
            result.append(url)
    return result


def _looks_like_page(url: str) -> bool:
    return not urlsplit(url).path.lower().endswith(_SKIP_EXTENSIONS)


def _to_page(result: FetchResult) -> PageData:
    return parse_page(result.body, result.url, result.status, result.seconds, result.requested_url)


def _fetch_page(fetch: Fetcher, url: str, site_url: str) -> tuple[PageData | None, str]:
    try:
        result = fetch(url)
    except FetchError as error:
        return None, str(error)
    if not same_site(result.url, site_url):
        return None, "Redirected to a different website"
    if result.status in BLOCKING_STATUSES:
        return None, "The site refused our request"
    if not result.is_html:
        return None, "Not a web page"
    return _to_page(result), ""


def _read_robots(fetch: Fetcher, origin: str) -> tuple[RobotFileParser, bool, list[str]]:
    """Return (parser, robots.txt found, sitemap URLs it lists). Failures mean 'allow all'."""
    parser = RobotFileParser()
    try:
        result = fetch(f"{origin}/robots.txt")
    except FetchError:
        parser.parse([])
        return parser, False, []
    if result.status != 200 or "html" in result.content_type.lower():
        parser.parse([])
        return parser, False, []
    lines = result.text.splitlines()
    parser.parse(lines)
    sitemaps = [
        line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("sitemap:")
    ]
    return parser, True, sitemaps


def _read_sitemap(
    fetch: Fetcher, origin: str, listed: list[str], site_url: str
) -> tuple[str | None, list[str]]:
    """Return (sitemap URL used, page URLs on this site). Follows sitemap index files."""
    for sitemap_url in [*listed, f"{origin}/sitemap.xml"]:
        urls = _sitemap_pages(fetch, sitemap_url, depth=0)
        if urls is not None:
            same = _unique([u for u in urls if same_site(u, site_url)], skip=set())
            return sitemap_url, same[:MAX_SITEMAP_URLS]
    return None, []


def _sitemap_pages(fetch: Fetcher, url: str, depth: int) -> list[str] | None:
    """Page URLs in a sitemap or sitemap index. None if there is no readable sitemap."""
    try:
        result = fetch(url)
    except FetchError:
        return None
    if result.status != 200 or "<" not in result.text[:200]:
        return None
    soup = BeautifulSoup(result.body, "lxml-xml")
    if soup.find("sitemapindex"):
        children = [loc.get_text(strip=True) for loc in soup.find_all("loc")][:MAX_CHILD_SITEMAPS]
        urls: list[str] = []
        if depth < 2:
            for child in children:
                found = _sitemap_pages(fetch, child, depth + 1)
                urls += found or []
        return urls
    if soup.find("urlset"):
        return [loc.get_text(strip=True) for loc in soup.find_all("loc")]
    return None
