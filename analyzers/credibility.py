"""Credibility and backlinks analyzer: trust signals on the site, plus optional backlinks.

On-site checks are deterministic: contact and about pages, social profiles, reviews,
privacy policy. Inbound backlinks need a paid data provider, so they are optional:
without provider findings (passed in through ``backlink_findings``) the analyzer
reports one ``unavailable`` finding. It never reports zero backlinks it did not measure.

If the homepage looks JavaScript-built and a signal is missing, the check is
``unavailable`` instead of a fail, because the crawler may not see that content.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from analyzers._schema import node_types, schema_nodes
from crawler.models import SiteData
from findings import Category, Finding, Source, Status, finding, unavailable

CATEGORY = Category.CREDIBILITY_BACKLINKS

SOCIAL_HOSTS = ("facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
                "youtube.com", "tiktok.com", "pinterest.com")
REVIEW_HOSTS = ("yelp.com", "tripadvisor.com", "trustpilot.com", "g.page", "maps.google.com")
REVIEW_SCHEMA_TYPES = frozenset({"Review", "AggregateRating"})

_CONTACT_RE = re.compile(r"contact|get[- ]in[- ]touch|reach[- ]us", re.I)
_ABOUT_RE = re.compile(r"\babout|our[- ]story|who[- ]we[- ]are|meet[- ]the", re.I)
_PRIVACY_RE = re.compile(r"privacy|terms|cookie[- ]policy", re.I)
_REVIEW_TEXT_RE = re.compile(
    r"testimonial|customer reviews?|what (our )?(customers|clients|guests) say|"
    r"\d(\.\d)? ?(out of 5|stars?)|★",
    re.I,
)

NO_PROVIDER = (
    "Inbound backlinks were not checked because no backlink data provider is connected."
)


def analyze(site: SiteData, backlink_findings: list[Finding] | None = None) -> list[Finding]:
    """Return credibility findings. ``backlink_findings`` comes from the optional provider."""
    if not site.pages:
        return []
    results = [
        _page_exists(site, "credibility.contact_page", "contact page", _CONTACT_RE, 2),
        _page_exists(site, "credibility.about_page", "about page", _ABOUT_RE, 2),
        _social(site),
        _reviews(site),
        _privacy(site),
    ]
    results += backlink_findings if backlink_findings else [
        unavailable("credibility.backlinks", CATEGORY, NO_PROVIDER,
                    source=Source.BACKLINK_PROVIDER, weight=2)
    ]
    return results


def _site_links(site: SiteData) -> list[tuple[str, str]]:
    """(url, visible text) for every scanned page and every internal link."""
    pairs = [(p.url, "") for p in site.pages]
    pairs += [(l.url, l.text) for p in site.pages for l in p.internal_links]
    return pairs


def _host(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def _on(host: str, domains: tuple[str, ...]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def _js_unavailable(check_id: str, what: str, weight: int, page: str) -> Finding:
    return unavailable(
        check_id, CATEGORY,
        f"The {what} could not be checked because this page is built by JavaScript.",
        weight=weight, page=page,
    )


def _page_exists(site, check_id, label, pattern, weight) -> Finding:
    for url, text in _site_links(site):
        if pattern.search(urlsplit(url).path) or pattern.search(text):
            return finding(
                check_id, CATEGORY, Status.PASS, f"A {label} was found: {url}.", weight=weight
            )
    home = site.homepage
    if home.likely_js_rendered:
        return _js_unavailable(check_id, label, weight, home.url)
    if check_id == "credibility.contact_page" and (
        any(p.emails or p.phones for p in site.pages)
    ):
        return finding(
            check_id, CATEGORY, Status.WARN,
            "No contact page found, though contact details appear elsewhere. "
            "A dedicated contact page builds trust.",
            weight=weight,
        )
    return finding(
        check_id, CATEGORY, Status.FAIL,
        f"No {label} found among the scanned pages. Visitors look for one to trust a business.",
        weight=weight,
    )


def _social(site: SiteData) -> Finding:
    cid = "credibility.social_profiles"
    urls = {u for p in site.pages for u in (*p.social_links, *(l.url for l in p.external_links))}
    networks = sorted({_host(u) for u in urls if _on(_host(u), SOCIAL_HOSTS)})
    if networks:
        return finding(
            cid, CATEGORY, Status.PASS, f"Links to social profiles found: {', '.join(networks)}."
        )
    if site.homepage.likely_js_rendered:
        return _js_unavailable(cid, "social links", 1, site.homepage.url)
    return finding(
        cid, CATEGORY, Status.WARN,
        "No links to social media profiles found. Active profiles show customers you are real.",
    )


def _reviews(site: SiteData) -> Finding:
    cid = "credibility.reviews"
    for page in site.pages:
        for node in schema_nodes(page):
            if node_types(node) & REVIEW_SCHEMA_TYPES:
                return finding(
                    cid, CATEGORY, Status.PASS,
                    "Review or rating structured data found.", weight=2, page=page.url,
                )
        match = _REVIEW_TEXT_RE.search(page.text)
        if match:
            return finding(
                cid, CATEGORY, Status.PASS,
                f'Review or testimonial content found on {page.url} (text: "{match.group(0)}").',
                weight=2, page=page.url,
            )
    for page in site.pages:
        for link in page.external_links:
            if _on(_host(link.url), REVIEW_HOSTS):
                return finding(
                    cid, CATEGORY, Status.PASS,
                    f"A link to a review site was found: {link.url}.", weight=2, page=page.url,
                )
    if site.homepage.likely_js_rendered:
        return _js_unavailable(cid, "reviews", 2, site.homepage.url)
    return finding(
        cid, CATEGORY, Status.WARN,
        "No customer reviews or testimonials found. Showing them builds trust.", weight=2,
    )


def _privacy(site: SiteData) -> Finding:
    cid = "credibility.privacy_policy"
    for url, text in _site_links(site):
        if _PRIVACY_RE.search(urlsplit(url).path) or _PRIVACY_RE.search(text):
            return finding(cid, CATEGORY, Status.PASS, f"A privacy or terms page was found: {url}.")
    if site.homepage.likely_js_rendered:
        return _js_unavailable(cid, "privacy policy", 1, site.homepage.url)
    return finding(
        cid, CATEGORY, Status.WARN,
        "No privacy policy or terms page found. It signals a trustworthy, professional site.",
    )
