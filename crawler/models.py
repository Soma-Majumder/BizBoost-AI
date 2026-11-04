"""The page data shape: what the crawler produces and every analyzer reads.

The crawler fills a ``SiteData``. Each analyzer is a function with this signature:

    def analyze(site: SiteData) -> list[Finding]

Reading the fields:
    * ``None`` or an empty tuple means "looked for it in the server HTML and it is
      not there". An analyzer may report that as a fail.
    * If ``PageData.likely_js_rendered`` is True, an absent field may only mean the
      content is built by JavaScript, which the crawler cannot see. Analyzers must
      then return ``unavailable`` for checks that depend on that content, never a fail.
    * Pages that could not be fetched are in ``SiteData.not_scanned``, never in
      ``pages``, and are never scored as failures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlsplit


class CrawlStatus(str, Enum):
    OK = "ok"  # at least the homepage was scanned
    BLOCKED = "blocked"  # robots.txt or a firewall refused the crawler
    UNREACHABLE = "unreachable"  # no page could be fetched


@dataclass(frozen=True)
class Heading:
    level: int  # 1 to 6
    text: str


@dataclass(frozen=True)
class Link:
    url: str  # absolute URL, fragment removed
    text: str  # visible link text, may be empty


@dataclass(frozen=True)
class Image:
    src: str  # absolute URL
    alt: str | None  # None = no alt attribute, "" = empty alt (decorative)


@dataclass(frozen=True)
class PageData:
    url: str  # final URL after redirects
    status_code: int
    fetch_seconds: float
    requested_url: str | None = None  # set only when a redirect changed the URL

    # Head tags
    title: str | None = None
    meta_description: str | None = None
    canonical: str | None = None
    meta_robots: str | None = None  # e.g. "noindex, nofollow"
    lang: str | None = None  # <html lang="...">
    has_viewport: bool = False
    open_graph: dict[str, str] = field(default_factory=dict)  # "og:title" -> value

    # Body
    headings: tuple[Heading, ...] = ()
    text: str = ""  # visible text, scripts and styles removed
    images: tuple[Image, ...] = ()
    internal_links: tuple[Link, ...] = ()
    external_links: tuple[Link, ...] = ()

    # Structured data and contact details
    structured_data: tuple[dict, ...] = ()  # parsed JSON-LD blocks
    phones: tuple[str, ...] = ()  # from tel: links and phone-like text
    emails: tuple[str, ...] = ()
    addresses: tuple[str, ...] = ()  # <address> tags and schema.org addresses
    social_links: tuple[str, ...] = ()  # facebook, instagram, x, linkedin, yelp, etc.
    has_map_embed: bool = False  # Google Maps iframe or link

    # Crawler's own judgment: server HTML looks like an empty shell for a JS app
    likely_js_rendered: bool = False

    @property
    def is_https(self) -> bool:
        return urlsplit(self.url).scheme == "https"

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def h1s(self) -> tuple[Heading, ...]:
        return tuple(h for h in self.headings if h.level == 1)


@dataclass(frozen=True)
class NotScanned:
    url: str
    reason: str  # plain language, shown to the user: "Blocked by robots.txt", "Timed out"


@dataclass(frozen=True)
class SiteData:
    start_url: str  # the validated URL the audit began with
    status: CrawlStatus
    pages: tuple[PageData, ...] = ()  # homepage first, at most 10
    not_scanned: tuple[NotScanned, ...] = ()
    message: str | None = None  # plain-language note when status is not OK

    # Site-level files, used by technical SEO checks
    robots_txt_found: bool = False
    sitemap_url: str | None = None  # the sitemap (or index) the crawler used
    sitemap_page_count: int = 0  # page URLs listed in the sitemap

    @property
    def homepage(self) -> PageData | None:
        return self.pages[0] if self.pages else None

    @property
    def scanned_urls(self) -> tuple[str, ...]:
        return tuple(page.url for page in self.pages)
