"""Optional backlink provider: the free Crawly API (https://www.getcrawly.com/api).

``fetch_backlink_findings(url)`` makes ONE request for the site's domain and returns
findings for the Credibility and Backlinks category. It never raises. Without a key, or
when the provider fails, it returns ``unavailable`` findings with a plain reason:
backlinks we could not measure are never reported as zero, and they never fail a site.

Rules (initial, to tune on the test sites):
    10 or more referring domains   pass
    1 to 9                         warn
    none found                     warn (the open index may be incomplete)
    any toxic link                 warn

Only the domain is sent. The API key goes in the Authorization header and is never
placed in a URL, a log line or an error message.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlsplit

import requests

from findings import Category, Finding, Source, Status, finding, unavailable

API_URL = "https://www.getcrawly.com/api/v1/backlinks"
KEY_ENV_VAR = "BACKLINK_API_KEY"
REQUEST_TIMEOUT = (5, 10)  # (connect, read) seconds
PASS_MIN_DOMAINS = 10
MAX_EXAMPLES = 3

CATEGORY = Category.CREDIBILITY_BACKLINKS
SOURCE = Source.BACKLINK_PROVIDER
BACKLINKS_ID = "credibility.backlinks"
TOXIC_ID = "credibility.toxic_backlinks"
BACKLINKS_WEIGHT = 2

# Provider text can end up in the AI's input, so only plain domain names are kept.
_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)[a-z0-9]([a-z0-9\-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]*[a-z0-9])?)+$")


def domain_from_url(url: str) -> str | None:
    """``https://www.example.com/page`` becomes ``example.com``."""
    host = (urlsplit(url if "//" in url else f"//{url}").hostname or "").lower()
    host = host.removeprefix("www.")
    return host or None


def fetch_backlink_findings(
    site_url: str, api_key: str | None = None, session: Any = None
) -> list[Finding]:
    """Return backlink findings for the site, or one ``unavailable`` finding."""
    key = (api_key if api_key is not None else os.getenv(KEY_ENV_VAR, "")).strip()
    if not key:
        return [_unavailable("No backlink provider key is set, so inbound backlinks were not checked.")]
    domain = domain_from_url(site_url)
    if not domain:
        return [_unavailable("Inbound backlinks were not checked because the website domain was unclear.")]

    try:
        response = (session or requests).get(
            API_URL,
            params={"domain": domain},
            headers={"Authorization": f"Bearer {key}"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        return [_unavailable("Inbound backlinks were not checked because the backlink provider took too long.")]
    except requests.exceptions.RequestException:
        return [_unavailable("Inbound backlinks were not checked because the backlink provider could not be reached.")]

    status = response.status_code
    if status == 401:
        return [_unavailable("Inbound backlinks were not checked because the backlink provider rejected our key.")]
    if status == 429:
        return [_unavailable("Inbound backlinks were not checked because the backlink provider's daily limit was reached.")]
    if status != 200:
        return [_unavailable(f"Inbound backlinks were not checked because the backlink provider returned an error (status {status}).")]
    try:
        data = response.json()
    except ValueError:
        data = None
    return _findings_from_response(data)


def _unavailable(reason: str) -> Finding:
    return unavailable(BACKLINKS_ID, CATEGORY, reason, source=SOURCE, weight=BACKLINKS_WEIGHT)


def _count(value: Any) -> int | None:
    """A whole number of 0 or more, or None. Booleans and floats are not counts."""
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _findings_from_response(data: Any) -> list[Finding]:
    if not isinstance(data, dict) or (domains := _count(data.get("referring_domains"))) is None:
        return [_unavailable("Inbound backlinks were not checked because the backlink provider's answer could not be read.")]

    backlinks = data.get("backlinks")
    rows = [r for r in (backlinks.get("rows") if isinstance(backlinks, dict) else None) or [] if isinstance(r, dict)]
    results = [_referring_domains_finding(domains, data.get("total_links"), rows)]
    if rows:
        results.append(_toxic_finding(rows, domains))
    return results


def _examples(rows: list[dict[str, Any]]) -> list[str]:
    names = [r.get("source_domain") for r in rows]
    return [n for n in names if isinstance(n, str) and _DOMAIN_RE.match(n)][:MAX_EXAMPLES]


def _referring_domains_finding(domains: int, total_links: Any, rows: list[dict[str, Any]]) -> Finding:
    if domains == 0:
        return finding(
            BACKLINKS_ID, CATEGORY, Status.WARN,
            "No inbound backlinks were found in Crawly's open web index. That index may be "
            "incomplete, so this does not prove your site has none.",
            source=SOURCE, weight=BACKLINKS_WEIGHT,
        )
    links = _count(total_links)
    detail = f"{domains} referring domain{'s' if domains != 1 else ''}"
    if links is not None and links != domains:
        detail += f" ({links} links)"
    examples = _examples(rows)
    suffix = f", for example {', '.join(examples)}" if examples else ""
    if domains >= PASS_MIN_DOMAINS:
        return finding(
            BACKLINKS_ID, CATEGORY, Status.PASS,
            f"{detail} found in Crawly's open web index{suffix}.",
            source=SOURCE, weight=BACKLINKS_WEIGHT,
        )
    return finding(
        BACKLINKS_ID, CATEGORY, Status.WARN,
        f"Only {detail} found in Crawly's open web index{suffix}. {PASS_MIN_DOMAINS} or more "
        "is a healthier sign of trust. The index may be incomplete.",
        source=SOURCE, weight=BACKLINKS_WEIGHT,
    )


def _toxic_finding(rows: list[dict[str, Any]], domains: int) -> Finding:
    toxic = [r for r in rows if r.get("is_toxic") is True]
    scope = f"the {len(rows)} links listed" if len(rows) < domains else "the links listed"
    if toxic:
        return finding(
            TOXIC_ID, CATEGORY, Status.WARN,
            f"{len(toxic)} of {scope} may be harmful (marked toxic by the provider). "
            "Consider asking those sites to remove the links.",
            source=SOURCE,
        )
    return finding(
        TOXIC_ID, CATEGORY, Status.PASS,
        f"None of {scope} were marked toxic by the provider.", source=SOURCE,
    )
