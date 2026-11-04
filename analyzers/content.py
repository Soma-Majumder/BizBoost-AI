"""Content quality analyzer: amount of text, readability, headings, images, internal links.

Deterministic checks on each page's server HTML, plus a duplicate-content comparison
across pages. A page that looks JavaScript-built and has little visible text gets
``unavailable``, not a fail, because the crawler may not be seeing the real content.
"""

from __future__ import annotations

import re
from collections import defaultdict

from crawler.models import PageData, SiteData
from findings import Category, Finding, Status, finding, unavailable

CATEGORY = Category.CONTENT_QUALITY

THIN_WORDS = 100  # fewer than this is a fail
SHORT_WORDS = 250  # fewer than this is a warn
READABILITY_MIN_WORDS = 100  # too little text to score reading ease
EASY_ENOUGH = 50  # Flesch reading ease: 50+ is plain English for most adults
VERY_HARD = 30
ALT_FAIL_SHARE = 0.5  # fail when more than this share of images lack alt text
SUBHEADING_MIN_WORDS = 300  # longer pages should be broken up with H2+ headings

_SENTENCE_RE = re.compile(r"[.!?]+")
_WORD_RE = re.compile(r"[A-Za-z']+")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")


def analyze(site: SiteData) -> list[Finding]:
    results: list[Finding] = []
    for page in site.pages:
        results += [
            _word_count(page),
            _readability(page),
            _headings(page),
            _image_alt(page),
            _internal_links(page),
        ]
    results.append(_duplicate_content(site))
    return [item for item in results if item is not None]


def _js_unavailable(check_id: str, page: PageData, what: str, weight: int) -> Finding:
    return unavailable(
        check_id, CATEGORY,
        f"The {what} could not be checked because this page is built by JavaScript.",
        weight=weight, page=page.url,
    )


def _word_count(page: PageData) -> Finding:
    cid, words = "content.word_count", page.word_count
    if words < SHORT_WORDS and page.likely_js_rendered:
        return _js_unavailable(cid, page, "amount of text", 3)
    if words < THIN_WORDS:
        return finding(
            cid, CATEGORY, Status.FAIL,
            f"Only {words} words of text. Pages with very little text rarely rank well.",
            weight=3, page=page.url,
        )
    if words < SHORT_WORDS:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"{words} words of text. Aim for at least {SHORT_WORDS} to explain what you offer.",
            weight=3, page=page.url,
        )
    return finding(cid, CATEGORY, Status.PASS, f"{words} words of text.", weight=3, page=page.url)


def _syllables(word: str) -> int:
    return max(1, len(_VOWEL_GROUP_RE.findall(word.lower())))


def _reading_ease(text: str) -> float | None:
    """Flesch reading ease (higher is easier). None if there is too little text."""
    words = _WORD_RE.findall(text)
    sentences = [s for s in _SENTENCE_RE.split(text) if _WORD_RE.search(s)]
    if len(words) < READABILITY_MIN_WORDS or not sentences:
        return None
    syllables = sum(_syllables(w) for w in words)
    return 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))


def _readability(page: PageData) -> Finding | None:
    cid = "content.readability"
    if page.lang and not page.lang.lower().startswith("en"):
        return unavailable(
            cid, CATEGORY,
            f'Reading ease is only measured for English pages (this page is "{page.lang}").',
            weight=2, page=page.url,
        )
    score = _reading_ease(page.text)
    if score is None:
        return None  # word_count already reports pages with too little text
    if score >= EASY_ENOUGH:
        return finding(
            cid, CATEGORY, Status.PASS,
            f"Reading ease score is {score:.0f} out of 100, which is easy to read.",
            weight=2, page=page.url,
        )
    status = Status.FAIL if score < VERY_HARD else Status.WARN
    return finding(
        cid, CATEGORY, status,
        f"Reading ease score is {score:.0f} out of 100 (50 or more is easy to read). "
        "Shorter sentences and simpler words would help.",
        weight=2, page=page.url,
    )


def _headings(page: PageData) -> Finding | None:
    cid = "content.heading_structure"
    if not page.headings:
        return None  # keyword.h1 already reports a missing H1
    levels = [h.level for h in page.headings]
    skips = [(a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]
    if skips:
        a, b = skips[0]
        return finding(
            cid, CATEGORY, Status.WARN,
            f"Headings skip from H{a} to H{b}. Use headings in order so the page outline "
            "makes sense.",
            page=page.url,
        )
    if page.word_count >= SUBHEADING_MIN_WORDS and max(levels) == 1:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"{page.word_count} words with no subheadings (H2 or lower). "
            "Break long pages into sections.",
            page=page.url,
        )
    return finding(cid, CATEGORY, Status.PASS, "Headings are in a sensible order.", page=page.url)


def _image_alt(page: PageData) -> Finding:
    cid = "content.image_alt"
    images = page.images
    if not images:
        if page.likely_js_rendered:
            return _js_unavailable(cid, page, "images", 2)
        return finding(
            cid, CATEGORY, Status.WARN,
            "No images found on this page. Photos help visitors and can appear in image search.",
            weight=2, page=page.url,
        )
    # alt="" is a deliberate choice for decorative images. Only a missing attribute counts.
    missing = [i for i in images if i.alt is None]
    if not missing:
        return finding(
            cid, CATEGORY, Status.PASS, f"All {len(images)} images have alt text.",
            weight=2, page=page.url,
        )
    status = Status.FAIL if len(missing) / len(images) > ALT_FAIL_SHARE else Status.WARN
    return finding(
        cid, CATEGORY, status,
        f"{len(missing)} of {len(images)} images have no alt text, which describes them to "
        "search engines and screen readers.",
        weight=2, page=page.url,
    )


def _internal_links(page: PageData) -> Finding:
    cid = "content.internal_links"
    if page.internal_links:
        return finding(
            cid, CATEGORY, Status.PASS,
            f"{len(page.internal_links)} links to other pages on your site.", page=page.url,
        )
    if page.likely_js_rendered:
        return _js_unavailable(cid, page, "internal links", 1)
    return finding(
        cid, CATEGORY, Status.WARN,
        "No links to other pages on your site. Linking your pages helps visitors and search "
        "engines find them.",
        page=page.url,
    )


def _duplicate_content(site: SiteData) -> Finding | None:
    cid = "content.duplicate_content"
    seen: dict[str, list[str]] = defaultdict(list)
    for page in site.pages:
        if page.word_count >= THIN_WORDS:
            seen[" ".join(page.text.lower().split())].append(page.url)
    if sum(len(urls) for urls in seen.values()) < 2:
        return None  # nothing to compare
    dupes = [urls for urls in seen.values() if len(urls) > 1]
    if not dupes:
        return finding(
            cid, CATEGORY, Status.PASS, "No two scanned pages have identical text.", weight=2
        )
    pages = sorted({url for urls in dupes for url in urls})
    return finding(
        cid, CATEGORY, Status.FAIL,
        f"{len(pages)} pages have identical text: {', '.join(pages)}.", weight=2,
    )
