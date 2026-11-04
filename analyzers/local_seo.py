"""Local SEO analyzer: phone and address (NAP), local business markup, map, listings.

Deterministic checks on the crawl. Businesses that do not depend on local search can
pass ``local_relevant=False``: the analyzer then returns one ``unavailable`` finding,
so the category shows "Data unavailable" instead of failing the site (PRD open
question on Local SEO relevance).

If the homepage looks JavaScript-built and a detail is missing, the check is
``unavailable`` instead of a fail, because the crawler may not see that content.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from analyzers._schema import node_types, schema_nodes
from crawler.models import PageData, SiteData
from findings import Category, Finding, Status, finding, unavailable

CATEGORY = Category.LOCAL_SEO

LOCAL_BUSINESS_TYPES = frozenset(
    "LocalBusiness Restaurant FoodEstablishment CafeOrCoffeeShop Bakery BarOrPub FastFoodRestaurant "
    "Store Hotel LodgingBusiness HealthAndBeautyBusiness HairSalon BeautySalon DaySpa Dentist "
    "Physician MedicalBusiness MedicalClinic AutoRepair AutomotiveBusiness LegalService Attorney "
    "RealEstateAgent Plumber Electrician HVACBusiness RoofingContractor HomeAndConstructionBusiness "
    "FinancialService AccountingService ProfessionalService SportsActivityLocation GymOrFitnessCenter "
    "ChildCare Florist GroceryStore ClothingStore HardwareStore PetStore".split()
)
LISTING_HOSTS = ("yelp.com", "tripadvisor.com", "foursquare.com", "yellowpages.com",
                 "maps.google.com", "g.page", "business.google.com")


def analyze(site: SiteData, local_relevant: bool = True) -> list[Finding]:
    if not local_relevant:
        return [
            unavailable(
                "local.not_applicable", CATEGORY,
                "Local SEO was skipped because this business does not rely on local search.",
            )
        ]
    home = site.homepage
    if home is None:
        return []
    results = [
        _contact_detail(site, "local.phone", "phone number", lambda p: p.phones, 3),
        _contact_detail(site, "local.address", "street address", lambda p: p.addresses, 3),
        _consistency(site, "local.phone_consistency", "phone number", lambda p: p.phones,
                     _normalize_phone),
        _consistency(site, "local.address_consistency", "address", lambda p: p.addresses,
                     _normalize_text),
        _local_schema(site),
        _map(site),
        _listings(site),
        _city_in_content(site),
    ]
    return [item for item in results if item is not None]


def _contact_detail(site, check_id, label, getter, weight) -> Finding:
    home = site.homepage
    if getter(home):
        return finding(
            check_id, CATEGORY, Status.PASS,
            f"{label.capitalize()} found on the homepage: {getter(home)[0]}.",
            weight=weight, page=home.url,
        )
    elsewhere = next((p for p in site.pages[1:] if getter(p)), None)
    if elsewhere:
        return finding(
            check_id, CATEGORY, Status.WARN,
            f"{label.capitalize()} found on {elsewhere.url} but not on the homepage. "
            "Show it where visitors land.",
            weight=weight, page=home.url,
        )
    if home.likely_js_rendered:
        return unavailable(
            check_id, CATEGORY,
            f"The {label} could not be checked because this page is built by JavaScript.",
            weight=weight, page=home.url,
        )
    return finding(
        check_id, CATEGORY, Status.FAIL,
        f"No {label} found on the scanned pages. Customers and search engines look for it.",
        weight=weight,
    )


def _consistency(site, check_id, label, getter, normalize) -> Finding | None:
    variants: dict[str, str] = {}
    for page in site.pages:
        for value in getter(page):
            variants.setdefault(normalize(value), value)
    if not variants:
        return None  # the detail itself is already reported as missing
    if len(variants) == 1:
        return finding(
            check_id, CATEGORY, Status.PASS,
            f"The {label} is the same on every page where it appears.",
        )
    return finding(
        check_id, CATEGORY, Status.WARN,
        f"{len(variants)} different {label}s appear on the site: {'; '.join(variants.values())}. "
        "Use one consistent version unless you have several locations.",
    )


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits[1:] if len(digits) == 11 and digits.startswith("1") else digits


def _normalize_text(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", value.lower()).split())


def _local_schema(site: SiteData) -> Finding:
    cid = "local.schema_markup"
    home = site.homepage
    found: set[str] = set()
    for page in site.pages:
        for node in schema_nodes(page):
            found |= node_types(node)
    local = found & LOCAL_BUSINESS_TYPES
    if local:
        return finding(
            cid, CATEGORY, Status.PASS,
            f"Local business structured data found ({', '.join(sorted(local))}).", weight=2,
        )
    if home.likely_js_rendered and not found:
        return unavailable(
            cid, CATEGORY,
            "Structured data could not be checked because this page is built by JavaScript.",
            weight=2, page=home.url,
        )
    if "Organization" in found:
        return finding(
            cid, CATEGORY, Status.WARN,
            "Structured data describes an Organization but not a local business. "
            "LocalBusiness markup adds your address, hours and phone for search engines.",
            weight=2,
        )
    return finding(
        cid, CATEGORY, Status.FAIL,
        "No LocalBusiness structured data found. It tells search engines your address, "
        "hours and phone in a form they can read.",
        weight=2,
    )


def _map(site: SiteData) -> Finding:
    cid = "local.map"
    page = next((p for p in site.pages if p.has_map_embed), None)
    if page:
        return finding(cid, CATEGORY, Status.PASS, f"A map was found on {page.url}.", page=page.url)
    if site.homepage.likely_js_rendered:
        return unavailable(
            cid, CATEGORY, "A map could not be checked because this page is built by JavaScript.",
            page=site.homepage.url,
        )
    return finding(
        cid, CATEGORY, Status.WARN, "No map found. A map helps customers locate you."
    )


def _listings(site: SiteData) -> Finding:
    cid = "local.directory_listings"
    links = {url for p in site.pages for url in (*p.social_links, *(l.url for l in p.external_links))}
    hosts = {_host(u) for u in links}
    matched = sorted(h for h in hosts if any(h == d or h.endswith("." + d) for d in LISTING_HOSTS))
    if matched:
        return finding(
            cid, CATEGORY, Status.PASS, f"Links to local listing sites found: {', '.join(matched)}."
        )
    return finding(
        cid, CATEGORY, Status.WARN,
        "No links to local listing sites such as Yelp or Google Maps were found.",
    )


def _host(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def _city_in_content(site: SiteData) -> Finding | None:
    """If the markup names a city, the homepage's key tags should mention it too."""
    cid = "local.city_in_title"
    home = site.homepage
    city = None
    for page in site.pages:
        for node in schema_nodes(page):
            address = node.get("address")
            if isinstance(address, dict) and isinstance(address.get("addressLocality"), str):
                city = address["addressLocality"].strip()
                break
        if city:
            break
    if not city:
        return None  # no city known, so there is nothing to compare
    tags = " ".join([home.title or "", home.meta_description or "", *(h.text for h in home.h1s)])
    if city.lower() in tags.lower():
        return finding(
            cid, CATEGORY, Status.PASS,
            f'Your city, "{city}", appears in the homepage title, description or heading.',
            weight=2, page=home.url,
        )
    return finding(
        cid, CATEGORY, Status.WARN,
        f'Your structured data lists "{city}" but it is not in the homepage title, description '
        "or main heading. Local searchers look for the city name.",
        weight=2, page=home.url,
    )
