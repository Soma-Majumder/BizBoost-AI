"""Check that a URL entered by a user is valid, reachable and safe to scan.

Call ``validate_url`` on what the user typed. It returns the normalized URL of the
page to scan (after any redirects) or raises a ``URLValidationError`` whose message
is written for a non-technical user and can be shown as is.

The crawler should call ``ensure_safe_url`` on every URL it fetches, because a page
that passed here can still link or redirect somewhere private.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests

USER_AGENT = "BizBoostAI-Audit/0.1 (+https://github.com/Soma-Majumder/BizBoost-AI)"
REQUEST_TIMEOUT = (5, 10)  # (connect, read) in seconds
MAX_REDIRECTS = 5

_ALLOWED_SCHEMES = {"http": 80, "https": 443}
_PRIVATE_NAME_SUFFIXES = (".localhost", ".local", ".internal", ".intranet", ".lan", ".home.arpa")

# A scheme is letters followed by a colon, unless digits follow ("example.com:8080").
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.\-]*:(?!\d)", re.IGNORECASE)
_WHITESPACE_OR_CONTROL_RE = re.compile(r"[\s\x00-\x1f\x7f]")
_HOST_LABEL_RE = re.compile(r"[a-z0-9]([a-z0-9\-]*[a-z0-9])?")

_NOT_A_WEBSITE = (
    "That doesn't look like a website address. "
    "Please check it and enter something like https://www.example.com."
)
_NOT_PUBLIC = (
    "This address points to a private or local network, so we can't scan it. "
    "Please enter your public website address."
)
_UNSAFE_REDIRECT = (
    "This website redirects to an address we can't safely scan. "
    "Please check the site's redirects or enter its final public address."
)
_CANT_REACH = (
    "We couldn't reach this website. "
    "Please check the address for typos and make sure the site is online, then try again."
)


class URLValidationError(Exception):
    """Base error. ``str(error)`` is a plain-language message for the user."""


class InvalidURLError(URLValidationError):
    """The text is not a usable website address."""


class UnsafeURLError(URLValidationError):
    """The address, or a redirect from it, points somewhere we must not scan."""


class UnreachableURLError(URLValidationError):
    """The address is well formed but no working website answered."""


def normalize_url(raw_url: str) -> str:
    """Return a canonical http(s) URL. Does no DNS lookup or network request."""
    if not isinstance(raw_url, str) or not raw_url.strip():
        raise InvalidURLError("Please enter your website address, like https://www.example.com.")

    text = raw_url.strip()
    if _WHITESPACE_OR_CONTROL_RE.search(text):
        raise InvalidURLError(_NOT_A_WEBSITE)
    if not _SCHEME_RE.match(text):
        text = "https://" + text.lstrip("/")

    try:
        parts = urlsplit(text)
        port = parts.port
    except ValueError as error:
        raise InvalidURLError(_NOT_A_WEBSITE) from error

    scheme = parts.scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise InvalidURLError(
            "Only website addresses starting with http:// or https:// can be scanned."
        )
    if "@" in parts.netloc:
        raise InvalidURLError(
            "Please remove the username or password from the address. "
            "We only scan public pages."
        )

    host = _normalize_host(parts.hostname)
    netloc = f"[{host}]" if ":" in host else host
    if port is not None and port != _ALLOWED_SCHEMES[scheme]:
        netloc += f":{port}"
    return urlunsplit((scheme, netloc, parts.path or "/", parts.query, ""))


def ensure_safe_url(url: str) -> str:
    """Normalize ``url`` and reject it if its host is not public. Makes no HTTP request."""
    normalized = normalize_url(url)
    _ensure_public_host(urlsplit(normalized).hostname)
    return normalized


def validate_url(raw_url: str) -> str:
    """Return the normalized final URL to scan, or raise ``URLValidationError``."""
    url = normalize_url(raw_url)
    try:
        return _follow_redirects(url)
    except UnreachableURLError:
        # We assumed https. Some small-business sites still only serve http.
        if _SCHEME_RE.match(raw_url.strip()):
            raise
        return _follow_redirects("http" + url.removeprefix("https"))


def _normalize_host(hostname: str | None) -> str:
    host = (hostname or "").rstrip(".")
    if not host:
        raise InvalidURLError(_NOT_A_WEBSITE)
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        pass

    # Encoding first also folds look-alike characters, so "①②⑦.⓪.⓪.①" can't
    # slip past the safety checks as something other than 127.0.0.1.
    try:
        ascii_host = host.encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise InvalidURLError(_NOT_A_WEBSITE) from error
    if not all(_HOST_LABEL_RE.fullmatch(label) for label in ascii_host.split(".")):
        raise InvalidURLError(_NOT_A_WEBSITE)
    return ascii_host


def _ensure_public_host(host: str) -> None:
    if host == "localhost" or host.endswith(_PRIVATE_NAME_SUFFIXES):
        raise UnsafeURLError(_NOT_PUBLIC)

    try:
        literal_ip = ipaddress.ip_address(host)
    except ValueError:
        literal_ip = None
    if literal_ip is not None:
        if not _is_public_ip(literal_ip):
            raise UnsafeURLError(_NOT_PUBLIC)
        return

    if "." not in host:
        raise InvalidURLError(_NOT_A_WEBSITE)

    try:
        addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (OSError, UnicodeError) as error:
        raise UnreachableURLError(_CANT_REACH) from error
    # Every address must be public: a host can return one public and one private.
    for *_, sockaddr in addresses:
        if not _is_public_ip(ipaddress.ip_address(sockaddr[0])):
            raise UnsafeURLError(_NOT_PUBLIC)


def _is_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    # is_global alone still accepts multicast addresses.
    return ip.is_global and not ip.is_multicast


def _follow_redirects(start_url: str) -> str:
    """Walk redirects by hand so each hop is checked before anything connects to it."""
    url = ensure_safe_url(start_url)
    for _ in range(MAX_REDIRECTS + 1):
        status, location = _fetch(url)
        if location is None:
            if status in (404, 410) or status >= 500:
                raise UnreachableURLError(_CANT_REACH)
            # Other statuses, such as 403, are left for the crawler, which reports
            # blocked sites as "does not allow scanning".
            return url
        try:
            url = ensure_safe_url(urljoin(url, location))
        except (InvalidURLError, UnsafeURLError, ValueError) as error:
            raise UnsafeURLError(_UNSAFE_REDIRECT) from error
    raise UnreachableURLError(
        "This website keeps redirecting and never settles on a page. "
        "Please check the site's redirects or enter its final address."
    )


def _fetch(url: str) -> tuple[int, str | None]:
    """Return the status and redirect target of ``url``. The body is never downloaded."""
    try:
        with requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
            stream=True,
        ) as response:
            location = response.headers["location"] if response.is_redirect else None
            return response.status_code, location
    except requests.exceptions.Timeout as error:
        raise UnreachableURLError(
            "This website took too long to respond. Please try again in a moment."
        ) from error
    except requests.exceptions.SSLError as error:
        raise UnreachableURLError(
            "We couldn't make a secure connection to this website. "
            "Its security certificate may be missing or expired."
        ) from error
    except requests.exceptions.RequestException as error:
        raise UnreachableURLError(_CANT_REACH) from error
