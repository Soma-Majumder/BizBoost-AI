"""Rule-based text, used when AI explanations are rejected or unavailable.

``rule_based_output(findings)`` returns the same shape as the AI agent. The explanation is
always the scanner's own evidence, so nothing here can state a fact the scan did not find.
The wording in ``RULES`` is general advice and deliberately contains no numbers.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from agent.reasoning import TOP_PRIORITY_COUNT
from findings import Category, Finding, Status

# check_id -> (title, why it matters, one action)
RULES: dict[str, tuple[str, str, str]] = {
    # Keywords
    "keyword.title": (
        "Improve your page titles",
        "The title is often the first thing people see about your business in search results.",
        "Give each page a unique title that names your business and what the page offers.",
    ),
    "keyword.meta_description": (
        "Improve your page descriptions",
        "A clear description can convince people to choose your site in search results.",
        "Write a unique description for each page summarizing your business and what the page offers.",
    ),
    "keyword.h1": (
        "Fix your main page headings",
        "The main heading tells visitors and search engines what a page is about.",
        "Give each page one main heading (an H1) that clearly says what the page is about.",
    ),
    "keyword.title_terms_in_content": (
        "Match your titles and page text",
        "Search engines trust a page more when its text covers what its title promises.",
        "Use the important words from each page's title naturally in that page's text.",
    ),
    "keyword.duplicate_titles": (
        "Give pages different titles",
        "Identical titles make it hard for search engines and visitors to tell pages apart.",
        "Rewrite the repeated titles so each one describes its own page.",
    ),
    "keyword.duplicate_meta_descriptions": (
        "Give pages different descriptions",
        "Identical descriptions make pages look the same in search results.",
        "Rewrite the repeated descriptions so each one summarizes its own page.",
    ),
    # Content
    "content.word_count": (
        "Add more useful text",
        "Pages with little text give customers and search engines less reason to trust them.",
        "Add helpful details to short pages, such as your services, prices or common questions.",
    ),
    "content.readability": (
        "Make your text easier to read",
        "Customers leave when text is hard to follow.",
        "Use shorter sentences and everyday words on the pages listed.",
    ),
    "content.heading_structure": (
        "Break up long pages with headings",
        "Headings help visitors scan a page and find what they need.",
        "Add short subheadings that split long text into clear sections.",
    ),
    "content.image_alt": (
        "Describe your images",
        "Image descriptions help search engines and people who use screen readers.",
        "Add a short description (alt text) to each image that says what it shows.",
    ),
    "content.internal_links": (
        "Link your pages together",
        "Links between your pages help visitors and search engines find everything you offer.",
        "Add links from each page to your other related pages.",
    ),
    "content.duplicate_content": (
        "Remove repeated page text",
        "Pages with the same text compete with each other and give visitors nothing new.",
        "Rewrite the repeated pages so each has its own useful text, or combine them.",
    ),
    # Local SEO
    "local.phone": (
        "Show your phone number",
        "Customers need an easy way to call you, and search engines use it to confirm your business.",
        "Add your phone number to your homepage and contact page.",
    ),
    "local.address": (
        "Show your street address",
        "Your address helps local customers find you and helps you appear in local searches.",
        "Add your full street address to your homepage and contact page.",
    ),
    "local.phone_consistency": (
        "Use one phone number everywhere",
        "Different numbers can confuse customers and search engines.",
        "Use the same phone number, written the same way, on every page.",
    ),
    "local.address_consistency": (
        "Use one address everywhere",
        "Different addresses can confuse customers and search engines.",
        "Use the same address, written the same way, on every page.",
    ),
    "local.schema_markup": (
        "Add business details for search engines",
        "Structured business details help search engines show your information correctly.",
        "Ask your website provider to add LocalBusiness structured data to your homepage.",
    ),
    "local.map": (
        "Add a map to your site",
        "A map makes it easier for customers to find and visit you.",
        "Add a Google Maps embed or link to your contact page.",
    ),
    "local.directory_listings": (
        "Link to your local listings",
        "Listings on sites like Yelp help customers find and trust your business.",
        "Add links from your site to your profiles on local listing sites.",
    ),
    "local.city_in_title": (
        "Mention your city in your titles",
        "Naming your city helps you appear when nearby customers search.",
        "Add your city or service area to your homepage title.",
    ),
    # Technical
    "technical.https": (
        "Secure your website with HTTPS",
        "Browsers warn visitors about sites that are not secure, which can drive customers away.",
        "Ask your website provider to turn on HTTPS for every page.",
    ),
    "technical.noindex": (
        "Let search engines list your pages",
        "Pages marked noindex will not appear in search results.",
        "Remove the noindex setting from any page you want customers to find.",
    ),
    "technical.broken_pages": (
        "Fix pages that show errors",
        "Broken pages frustrate visitors and waste the links pointing to them.",
        "Repair the pages listed, or redirect them to a working page.",
    ),
    "technical.sitemap": (
        "Add an XML sitemap",
        "A sitemap helps search engines find all of your pages.",
        "Create a sitemap, which most website builders can do for you, and submit it to Google.",
    ),
    "technical.robots_txt": (
        "Add a robots.txt file",
        "This file tells search engines how to crawl your site.",
        "Ask your website provider to add a basic robots.txt file.",
    ),
    "technical.response_time": (
        "Make your site respond faster",
        "Visitors often leave when a site takes too long to start loading.",
        "Ask your website provider about faster hosting or turning on caching.",
    ),
    "technical.canonical": (
        "Set your preferred page addresses",
        "A canonical tag tells search engines which address to list when a page has several.",
        "Add a canonical tag to each page that points to that page's main address.",
    ),
    "technical.viewport": (
        "Make your pages work on phones",
        "Many customers will visit from a phone, and pages without this tag can display badly.",
        "Add a mobile viewport tag to your pages, or use a mobile-friendly template.",
    ),
    "technical.lang": (
        "Set your page language",
        "Declaring the language helps search engines and screen readers handle your pages correctly.",
        "Add a language setting (the lang attribute) to the html tag of each page.",
    ),
    "technical.speed_score": (
        "Speed up your site on mobile",
        "Slow pages lose visitors, especially on phones.",
        "Compress large images and remove features you don't need from your homepage.",
    ),
    "technical.lcp": (
        "Show your main content sooner",
        "People may leave if the main part of a page takes a long time to appear.",
        "Compress the largest image or banner on your homepage.",
    ),
    "technical.cls": (
        "Stop your pages jumping while loading",
        "Content that moves while loading makes people tap the wrong thing.",
        "Set fixed sizes for images and banners so they keep their space while loading.",
    ),
    "technical.tbt": (
        "Make your pages respond faster to taps",
        "Pages that freeze while loading feel broken to visitors.",
        "Remove scripts and plugins you don't need from your homepage.",
    ),
    # Credibility
    "credibility.contact_page": (
        "Add a contact page",
        "Customers trust a business more when it is easy to reach.",
        "Create a contact page and link to it from your homepage menu.",
    ),
    "credibility.about_page": (
        "Add an about page",
        "An about page shows customers who is behind your business.",
        "Create a short about page with your story and link to it from your menu.",
    ),
    "credibility.social_profiles": (
        "Link to your social profiles",
        "Active social profiles help customers see that your business is real.",
        "Add links to your social media profiles in your site's footer.",
    ),
    "credibility.reviews": (
        "Show customer reviews",
        "Reviews from real customers help new visitors trust you.",
        "Add a few customer reviews to your homepage, or link to your review profiles.",
    ),
    "credibility.privacy_policy": (
        "Add a privacy policy",
        "A privacy policy shows visitors you take their information seriously.",
        "Add a privacy policy page and link to it from your site's footer.",
    ),
    "credibility.backlinks": (
        "Earn more links from other websites",
        "Links from other sites act like recommendations for your business.",
        "Ask local partners, suppliers or associations to link to your website.",
    ),
    "credibility.toxic_backlinks": (
        "Review possibly harmful links",
        "Links from low-quality sites can make your business look less trustworthy.",
        "Ask those sites to remove the links to your website.",
    ),
}

# Used for any check without its own wording, so a new check still gets sensible text.
CATEGORY_RULES: dict[Category, tuple[str, str, str]] = {
    Category.KEYWORD_OPTIMIZATION: (
        "Improve your keywords",
        "Clear words on your pages help customers find you through search.",
        "Review the pages listed and make it clear what each one offers.",
    ),
    Category.CONTENT_QUALITY: (
        "Improve your page content",
        "Helpful content gives customers a reason to choose your business.",
        "Review the pages listed and make their content clearer and more useful.",
    ),
    Category.LOCAL_SEO: (
        "Improve your local details",
        "Clear local details help nearby customers find you.",
        "Review the local information on the pages listed and make sure it is complete.",
    ),
    Category.TECHNICAL_SEO: (
        "Fix a technical issue",
        "Technical issues can stop search engines and customers from using your site.",
        "Share this finding with whoever manages your website and ask them to fix it.",
    ),
    Category.CREDIBILITY_BACKLINKS: (
        "Build more trust",
        "Signs of trust help new customers feel safe choosing your business.",
        "Review this finding and add the missing information to your site.",
    ),
}


def rule_based_output(findings: Iterable[Finding]) -> dict[str, Any]:
    """The AI output shape, written from the evidence and the wording above."""
    groups: dict[str, list[Finding]] = defaultdict(list)
    for item in findings:
        if item.status is not Status.PASS:
            groups[item.check_id].append(item)

    entries = [_entry(check_id, group) for check_id, group in groups.items()]
    fixable = [
        (check_id, group)
        for check_id, group in groups.items()
        if any(item.status is not Status.UNAVAILABLE for item in group)
    ]
    fixable.sort(key=lambda pair: _priority_rank(pair[1]))
    priorities = [
        {
            "check_id": check_id,
            "title": _rule(check_id, group)[0],
            "reason": _rule(check_id, group)[1],
        }
        for check_id, group in fixable[:TOP_PRIORITY_COUNT]
    ]
    return {"findings": entries, "top_priorities": priorities}


def _rule(check_id: str, group: list[Finding]) -> tuple[str, str, str]:
    return RULES.get(check_id) or CATEGORY_RULES[group[0].category]


def _entry(check_id: str, group: list[Finding]) -> dict[str, str]:
    _, why, action = _rule(check_id, group)
    if all(item.status is Status.UNAVAILABLE for item in group):
        why, action = "", ""  # nothing was measured, so there is nothing to advise
    return {
        "check_id": check_id,
        "explanation": _explanation(group),
        "why_it_matters": why,
        "action": action,
    }


def _explanation(group: list[Finding]) -> str:
    """The evidence for this check, one line per page, each repeated line shown once."""
    lines: list[str] = []
    for item in group:
        needs_page = item.page and item.page not in item.evidence
        line = f"{item.page}: {item.evidence}" if needs_page else item.evidence
        if line not in lines:
            lines.append(line)
    return "\n".join(lines)


def _priority_rank(group: list[Finding]) -> tuple[int, int, int]:
    """Highest weight first, then most failed checks, then most pages affected."""
    measured = [item for item in group if item.status is not Status.UNAVAILABLE]
    failed = sum(1 for item in measured if item.status is Status.FAIL)
    return (-max(item.weight for item in measured), -failed, -len(measured))
