"""Keyword optimization analyzer: titles, meta descriptions, H1s and how they line up.

Deterministic checks only. Each page is checked on its own, then titles and
descriptions are compared across pages.

If a page looks JavaScript-built and a tag is missing, the check is ``unavailable``
instead of a fail, because the crawler may simply not see that tag.
"""

from __future__ import annotations

import re
from collections import defaultdict

from crawler.models import PageData, SiteData
from findings import Category, Finding, Status, finding, unavailable

CATEGORY = Category.KEYWORD_OPTIMIZATION

TITLE_MIN, TITLE_MAX = 20, 65
DESCRIPTION_MIN, DESCRIPTION_MAX = 70, 160
MIN_TITLE_TERMS_IN_CONTENT = 0.5  # share of title words that should appear on the page

_GENERIC_TITLE_START = re.compile(r"^(home|homepage|untitled|welcome|index|new page)\b", re.I)
_WORD_RE = re.compile(r"[a-z0-9']+")
_STOPWORDS = frozenset(
    "a an and are as at be by for from in is it of on or our the to we with your you "
    "home page welcome about us".split()
)


def analyze(site: SiteData) -> list[Finding]:
    results: list[Finding] = []
    for page in site.pages:
        results += [
            _title(page),
            _meta_description(page),
            _h1(page),
            _title_terms_in_content(page),
        ]
    results += [item for item in (_duplicate_titles(site), _duplicate_descriptions(site)) if item]
    return [item for item in results if item is not None]


def _terms(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS and len(w) > 2}


def _missing(check_id: str, page: PageData, what: str, weight: int) -> Finding:
    """A tag is absent from the server HTML: a fail, unless JavaScript may hide it."""
    if page.likely_js_rendered:
        return unavailable(
            check_id,
            CATEGORY,
            f"The {what} could not be checked because this page is built by JavaScript.",
            weight=weight,
            page=page.url,
        )
    return finding(
        check_id, CATEGORY, Status.FAIL, f"{what[0].upper()}{what[1:]} is missing.",
        weight=weight, page=page.url,
    )


def _title(page: PageData) -> Finding:
    cid = "keyword.title"
    if not page.title or not page.title.strip():
        return _missing(cid, page, "title tag", 3)
    title = page.title.strip()
    n = len(title)
    if _GENERIC_TITLE_START.match(title):
        return finding(
            cid, CATEGORY, Status.WARN,
            f'Title "{title}" starts with a generic word. Lead with what the business does.',
            weight=3, page=page.url,
        )
    if n < TITLE_MIN:
        return finding(
            cid, CATEGORY, Status.WARN,
            f'Title "{title}" is only {n} characters. Aim for {TITLE_MIN} to {TITLE_MAX}.',
            weight=3, page=page.url,
        )
    if n > TITLE_MAX:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"Title is {n} characters and may be cut off in search results. "
            f"Aim for {TITLE_MIN} to {TITLE_MAX}.",
            weight=3, page=page.url,
        )
    return finding(
        cid, CATEGORY, Status.PASS, f'Title "{title}" is {n} characters.', weight=3, page=page.url
    )


def _meta_description(page: PageData) -> Finding:
    cid = "keyword.meta_description"
    if not page.meta_description or not page.meta_description.strip():
        return _missing(cid, page, "meta description tag", 3)
    n = len(page.meta_description.strip())
    if n < DESCRIPTION_MIN:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"Meta description is only {n} characters. Aim for {DESCRIPTION_MIN} to "
            f"{DESCRIPTION_MAX}.",
            weight=3, page=page.url,
        )
    if n > DESCRIPTION_MAX:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"Meta description is {n} characters and may be cut off in search results. "
            f"Aim for {DESCRIPTION_MIN} to {DESCRIPTION_MAX}.",
            weight=3, page=page.url,
        )
    return finding(
        cid, CATEGORY, Status.PASS, f"Meta description is {n} characters.",
        weight=3, page=page.url,
    )


def _h1(page: PageData) -> Finding:
    cid = "keyword.h1"
    h1s = page.h1s
    if not h1s:
        return _missing(cid, page, "H1 heading", 3)
    if len(h1s) > 1:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"Page has {len(h1s)} H1 headings. Use one main heading per page.",
            weight=3, page=page.url,
        )
    return finding(
        cid, CATEGORY, Status.PASS, f'H1 heading is "{h1s[0].text.strip()}".',
        weight=3, page=page.url,
    )


def _title_terms_in_content(page: PageData) -> Finding | None:
    """Do the words promised in the title actually appear on the page?"""
    cid = "keyword.title_terms_in_content"
    title_terms = _terms(page.title or "")
    if not title_terms:
        return None  # the title check already reports a missing or empty title
    if page.likely_js_rendered and not page.text.strip():
        return unavailable(
            cid, CATEGORY,
            "Page text could not be read because this page is built by JavaScript.",
            page=page.url,
        )
    body_terms = _terms(page.text) | _terms(" ".join(h.text for h in page.headings))
    found = title_terms & body_terms
    share = len(found) / len(title_terms)
    missing = sorted(title_terms - body_terms)
    if share >= MIN_TITLE_TERMS_IN_CONTENT:
        return finding(
            cid, CATEGORY, Status.PASS,
            f"{len(found)} of {len(title_terms)} title keywords appear in the page content.",
            page=page.url,
        )
    return finding(
        cid, CATEGORY, Status.WARN,
        f"Only {len(found)} of {len(title_terms)} title keywords appear in the page content. "
        f"Not found: {', '.join(missing)}.",
        page=page.url,
    )


def _duplicates(values: dict[str, list[str]]) -> dict[str, list[str]]:
    return {text: urls for text, urls in values.items() if len(urls) > 1}


def _duplicate_titles(site: SiteData) -> Finding | None:
    return _duplicate_check(site, "keyword.duplicate_titles", "title", lambda p: p.title)


def _duplicate_descriptions(site: SiteData) -> Finding | None:
    return _duplicate_check(
        site, "keyword.duplicate_meta_descriptions", "meta description",
        lambda p: p.meta_description,
    )


def _duplicate_check(site: SiteData, cid: str, label: str, getter) -> Finding | None:
    seen: dict[str, list[str]] = defaultdict(list)
    for page in site.pages:
        value = (getter(page) or "").strip()
        if value:
            seen[value.lower()].append(page.url)
    if sum(len(urls) for urls in seen.values()) < 2:
        return None  # nothing to compare
    dupes = _duplicates(seen)
    if not dupes:
        return finding(
            cid, CATEGORY, Status.PASS, f"Every scanned page has a different {label}.", weight=2
        )
    pages = sorted({url for urls in dupes.values() for url in urls})
    return finding(
        cid, CATEGORY, Status.FAIL,
        f"{len(pages)} pages share the same {label}: {', '.join(pages)}.",
        weight=2,
    )
