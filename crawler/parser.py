"""Turn one page's server HTML into a ``PageData``. No network access happens here."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import unquote, urldefrag, urljoin, urlsplit

from bs4 import BeautifulSoup

from crawler.models import Heading, Image, Link, PageData

SOCIAL_HOSTS = (
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", "youtube.com",
    "tiktok.com", "pinterest.com", "yelp.com", "tripadvisor.com",
)
MAP_MARKERS = ("google.com/maps", "maps.google.", "goo.gl/maps", "maps.app.goo.gl", "openstreetmap.org")
JS_ROOT_IDS = {"root", "__next", "app", "___gatsby", "__nuxt"}
JS_SHELL_MAX_WORDS = 50

_PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")
# US street address typed in plain text: "77 Mulberry St, New York 10013". Needs a street
# suffix and a ZIP code, and the street name cannot start with a digit (so a phone number
# right before the address is not swallowed into it).
_STREET_WORD = r"(?:[A-Za-z][\w'.\-]*|\d+(?:st|nd|rd|th))"
_TEXT_ADDRESS_RE = re.compile(
    rf"(?<![\d\-])\d{{1,6}}\s+(?:{_STREET_WORD}\s+){{1,4}}?"
    r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct|"
    r"Highway|Hwy|Parkway|Pkwy|Square|Sq)\b\.?,?"
    r"(?:,?\s+[A-Za-z.'\-]+){0,4}?,?\s+(?:[A-Z]{2},?\s+)?\d{5}(?:-\d{4})?\b",
    re.IGNORECASE,
)
_EMAIL_RE =re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_SPACE_RE = re.compile(r"\s+")


def same_site(url_a: str, url_b: str) -> bool:
    """True when both URLs are on the same host, ignoring a leading ``www.``."""
    return _bare_host(url_a) == _bare_host(url_b)


def _bare_host(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def _clean(text: str | None) -> str:
    return _SPACE_RE.sub(" ", text or "").strip()


def _absolute(base: str, href: str | None) -> str | None:
    if not href:
        return None
    url, _ = urldefrag(urljoin(base, href.strip()))
    return url if urlsplit(url).scheme in ("http", "https") else None


def parse_page(
    body: bytes,
    url: str,
    status_code: int,
    fetch_seconds: float,
    requested_url: str | None = None,
) -> PageData:
    soup = BeautifulSoup(body, "lxml")
    html_tag = soup.find("html")

    title_tag = soup.find("title")
    meta = {
        (m.get("name") or m.get("property") or "").lower(): m.get("content", "")
        for m in soup.find_all("meta")
        if m.get("name") or m.get("property")
    }
    canonical_tag = soup.find("link", rel=lambda r: r and "canonical" in r)

    structured = _json_ld(soup)
    internal, external = _links(soup, url)
    images = _images(soup, url)

    # Visible text excludes code and hidden template content.
    # Data blocks such as JSON-LD are not app code, so they don't suggest a JS-built page.
    scripts = [s for s in soup.find_all("script") if "json" not in (s.get("type") or "").lower()]
    noscript_text = " ".join(n.get_text(" ") for n in soup.find_all("noscript")).lower()
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    text = _clean(soup.get_text(" "))

    tel_links = [
        unquote(a["href"][4:]).strip() for a in soup.find_all("a", href=True)
        if a["href"].lower().startswith("tel:")
    ]
    mail_links = [
        unquote(a["href"][7:]).split("?")[0].strip() for a in soup.find_all("a", href=True)
        if a["href"].lower().startswith("mailto:")
    ]
    all_urls = [l.url for l in internal + external]
    social = _dedupe(
        u for u in all_urls
        if _host_matches(u, SOCIAL_HOSTS) and not re.search(r"/(sharer|share)\b", urlsplit(u).path)
    )

    words = len(text.split())
    return PageData(
        url=url,
        requested_url=requested_url,
        status_code=status_code,
        fetch_seconds=fetch_seconds,
        title=_clean(title_tag.get_text()) or None if title_tag else None,
        meta_description=_clean(meta.get("description")) or None,
        canonical=_absolute(url, canonical_tag.get("href")) if canonical_tag else None,
        meta_robots=_clean(meta.get("robots")) or None,
        lang=(html_tag.get("lang") or "").strip() or None if html_tag else None,
        has_viewport="viewport" in meta,
        open_graph={k: v for k, v in meta.items() if k.startswith("og:") and v},
        headings=tuple(
            Heading(int(h.name[1]), _clean(h.get_text()))
            for h in soup.find_all(re.compile(r"^h[1-6]$"))
            if _clean(h.get_text())
        ),
        text=text,
        images=images,
        internal_links=internal,
        external_links=external,
        structured_data=structured,
        phones=_dedupe_phones([*tel_links, *_PHONE_RE.findall(text)]),
        emails=_dedupe(e.lower() for e in [*mail_links, *_EMAIL_RE.findall(text)] if e),
        addresses=_addresses(soup, structured, text),
        social_links=social,
        has_map_embed=_has_map(soup, all_urls),
        likely_js_rendered=words < JS_SHELL_MAX_WORDS
        and (
            any(soup.find(id=i) is not None for i in JS_ROOT_IDS)
            or len(scripts) >= 3
            or "javascript" in noscript_text
        ),
    )


def _dedupe(items) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for item in items:
        if item and item not in seen:
            seen[item] = None
    return tuple(seen)


def _dedupe_phones(items) -> tuple[str, ...]:
    seen: dict[str, str] = {}
    for item in items:
        digits = re.sub(r"\D", "", item)
        key = digits[1:] if len(digits) == 11 and digits.startswith("1") else digits
        if 10 <= len(key) <= 15:
            seen.setdefault(key, item.strip())
    return tuple(seen.values())


def _host_matches(url: str, domains: tuple[str, ...]) -> bool:
    host = (urlsplit(url).hostname or "").lower().removeprefix("www.")
    return any(host == d or host.endswith("." + d) for d in domains)


def _links(soup: BeautifulSoup, page_url: str) -> tuple[tuple[Link, ...], tuple[Link, ...]]:
    internal: dict[str, Link] = {}
    external: dict[str, Link] = {}
    for a in soup.find_all("a", href=True):
        url = _absolute(page_url, a["href"])
        if not url or url == urldefrag(page_url)[0]:
            continue
        bucket = internal if same_site(url, page_url) else external
        bucket.setdefault(url, Link(url, _clean(a.get_text())))
    return tuple(internal.values()), tuple(external.values())


def _images(soup: BeautifulSoup, page_url: str) -> tuple[Image, ...]:
    images: list[Image] = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if not src or src.startswith("data:"):
            continue
        url = _absolute(page_url, src)
        if url:
            images.append(Image(url, img.get("alt")))
    return tuple(images)


def _json_ld(soup: BeautifulSoup) -> tuple[dict[str, Any], ...]:
    blocks: list[dict[str, Any]] = []
    for tag in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
        try:
            data = json.loads(tag.string or tag.get_text() or "")
        except ValueError:
            continue  # broken JSON-LD is ignored, not a crash
        blocks += [d for d in (data if isinstance(data, list) else [data]) if isinstance(d, dict)]
    return tuple(blocks)


def _format_address(node: dict[str, Any]) -> str | None:
    parts = [node.get(k) for k in ("streetAddress", "addressLocality", "addressRegion", "postalCode")]
    text = ", ".join(str(p).strip() for p in parts if isinstance(p, (str, int)) and str(p).strip())
    return text or None


def _schema_addresses(node: Any) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        address = node.get("address")
        if isinstance(address, str) and address.strip():
            found.append(_clean(address))
        elif isinstance(address, dict) and (text := _format_address(address)):
            found.append(text)
        for value in node.values():
            if isinstance(value, (dict, list)):
                found += _schema_addresses(value)
    elif isinstance(node, list):
        for item in node:
            found += _schema_addresses(item)
    return found


def _addresses(
    soup: BeautifulSoup, structured: tuple[dict[str, Any], ...], text: str
) -> tuple[str, ...]:
    tags = [_clean(a.get_text(", ")) for a in soup.find_all("address")]
    typed = [_clean(m.group(0)) for m in _TEXT_ADDRESS_RE.finditer(text)]
    return _dedupe([*tags, *_schema_addresses(list(structured)), *typed])


def _has_map(soup: BeautifulSoup, link_urls: list[str]) -> bool:
    sources = [f.get("src", "") for f in soup.find_all("iframe")] + link_urls
    return any(marker in src.lower() for src in sources for marker in MAP_MARKERS)
