"""Technical SEO analyzer: HTTPS, indexing, canonicals, sitemap, mobile tag, page errors.

Deterministic checks on the crawl. PageSpeed findings come from
``integrations/pagespeed.py`` (issue #11) and are passed in through ``extra`` so they
join this category without this module calling any API.

If a page looks JavaScript-built and a tag is missing, the check is ``unavailable``
instead of a fail, because the crawler may simply not see that tag.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from crawler.models import PageData, SiteData
from findings import Category, Finding, Status, finding, unavailable

CATEGORY = Category.TECHNICAL_SEO
SLOW_RESPONSE_SECONDS = 3.0


def analyze(site: SiteData, extra: list[Finding] | None = None) -> list[Finding]:
    """Return technical findings. ``extra`` adds findings from other sources (PageSpeed)."""
    results: list[Finding] = list(extra or [])
    if not site.pages:
        return results  # nothing was scanned, so there is nothing to check

    results += [_https(site), _noindex(site), _broken_pages(site), _sitemap(site),
                _robots_txt(site), _response_time(site)]
    for page in site.pages:
        results += [_canonical(page), _viewport(page), _lang(page)]
    return results


def _js_unavailable(check_id: str, page: PageData, what: str, weight: int) -> Finding:
    return unavailable(
        check_id, CATEGORY,
        f"The {what} could not be checked because this page is built by JavaScript.",
        weight=weight, page=page.url,
    )


def _https(site: SiteData) -> Finding:
    cid = "technical.https"
    insecure = [p.url for p in site.pages if not p.is_https]
    if insecure:
        return finding(
            cid, CATEGORY, Status.FAIL,
            f"{len(insecure)} scanned page(s) load over http, not https: {', '.join(insecure)}.",
            weight=3,
        )
    return finding(cid, CATEGORY, Status.PASS, "All scanned pages load over https.", weight=3)


def _noindex(site: SiteData) -> Finding:
    cid = "technical.noindex"
    blocked = [p.url for p in site.pages if "noindex" in (p.meta_robots or "").lower()]
    if blocked:
        return finding(
            cid, CATEGORY, Status.FAIL,
            f"{len(blocked)} page(s) tell search engines not to list them (noindex): "
            f"{', '.join(blocked)}.",
            weight=3,
        )
    return finding(
        cid, CATEGORY, Status.PASS, "No scanned page blocks search engines with noindex.", weight=3
    )


def _broken_pages(site: SiteData) -> Finding:
    cid = "technical.broken_pages"
    broken = [(p.url, p.status_code) for p in site.pages if p.status_code >= 400]
    if broken:
        listed = ", ".join(f"{url} (status {code})" for url, code in broken)
        return finding(
            cid, CATEGORY, Status.FAIL,
            f"{len(broken)} scanned page(s) returned an error: {listed}.", weight=3,
        )
    return finding(
        cid, CATEGORY, Status.PASS, f"All {len(site.pages)} scanned pages loaded without errors.",
        weight=3,
    )


def _sitemap(site: SiteData) -> Finding:
    cid = "technical.sitemap"
    if site.sitemap_url:
        return finding(
            cid, CATEGORY, Status.PASS,
            f"XML sitemap found at {site.sitemap_url} listing {site.sitemap_page_count} page(s).",
            weight=2,
        )
    return finding(
        cid, CATEGORY, Status.FAIL,
        "No XML sitemap was found, so search engines have no list of your pages.", weight=2,
    )


def _robots_txt(site: SiteData) -> Finding:
    cid = "technical.robots_txt"
    if site.robots_txt_found:
        return finding(cid, CATEGORY, Status.PASS, "A robots.txt file was found.")
    return finding(
        cid, CATEGORY, Status.WARN,
        "No robots.txt file was found. It tells search engines what they may visit.",
    )


def _response_time(site: SiteData) -> Finding:
    cid = "technical.response_time"
    home = site.homepage
    seconds = home.fetch_seconds
    if seconds > SLOW_RESPONSE_SECONDS:
        return finding(
            cid, CATEGORY, Status.WARN,
            f"The homepage took {seconds:.1f} seconds to respond. "
            f"Under {SLOW_RESPONSE_SECONDS:.0f} seconds is better.",
            page=home.url,
        )
    return finding(
        cid, CATEGORY, Status.PASS, f"The homepage responded in {seconds:.1f} seconds.",
        page=home.url,
    )


def _canonical(page: PageData) -> Finding:
    cid = "technical.canonical"
    if not page.canonical:
        if page.likely_js_rendered:
            return _js_unavailable(cid, page, "canonical tag", 2)
        return finding(
            cid, CATEGORY, Status.WARN,
            "No canonical tag. It tells search engines which address is the main one.",
            weight=2, page=page.url,
        )
    if _normalize(page.canonical) != _normalize(page.url):
        return finding(
            cid, CATEGORY, Status.WARN,
            f"Canonical tag points to a different address: {page.canonical}. "
            "Search engines may ignore this page.",
            weight=2, page=page.url,
        )
    return finding(
        cid, CATEGORY, Status.PASS, "Canonical tag points to this page.", weight=2, page=page.url
    )


def _viewport(page: PageData) -> Finding:
    cid = "technical.viewport"
    if page.has_viewport:
        return finding(
            cid, CATEGORY, Status.PASS, "Mobile viewport tag found.", weight=2, page=page.url
        )
    if page.likely_js_rendered:
        return _js_unavailable(cid, page, "mobile viewport tag", 2)
    return finding(
        cid, CATEGORY, Status.FAIL,
        "No mobile viewport tag, so the page may display poorly on phones.",
        weight=2, page=page.url,
    )


def _lang(page: PageData) -> Finding:
    cid = "technical.lang"
    if page.lang:
        return finding(cid, CATEGORY, Status.PASS, f'Page language is set to "{page.lang}".',
                       page=page.url)
    if page.likely_js_rendered:
        return _js_unavailable(cid, page, "page language", 1)
    return finding(
        cid, CATEGORY, Status.WARN,
        "No language set on the page (the lang attribute on the html tag).", page=page.url,
    )


def _normalize(url: str) -> str:
    parts = urlsplit(url.strip())
    return f"{parts.scheme}://{parts.netloc.lower()}{parts.path.rstrip('/') or '/'}?{parts.query}"
