"""Tests for url_validator. DNS and HTTP are faked, so these never touch the network."""

import socket

import pytest
import requests

import url_validator
from url_validator import (
    InvalidURLError,
    UnreachableURLError,
    UnsafeURLError,
    ensure_safe_url,
    normalize_url,
    validate_url,
)

PUBLIC_IP = "93.184.216.34"


class FakeResponse:
    def __init__(self, status_code=200, location=None):
        self.status_code = status_code
        self.headers = {"location": location} if location else {}
        self.is_redirect = location is not None

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class FakeWeb:
    """Stands in for DNS and HTTP, and records every URL we tried to fetch."""

    def __init__(self):
        self.dns = {}  # host -> list of IPs; unlisted hosts get PUBLIC_IP
        self.routes = {}  # url -> FakeResponse or an exception to raise
        self.fetched = []
        self.last_kwargs = {}

    def getaddrinfo(self, host, port, *args, **kwargs):
        ips = self.dns.get(host, [PUBLIC_IP])
        if not ips:
            raise socket.gaierror("name not found")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0)) for ip in ips]

    def get(self, url, **kwargs):
        self.fetched.append(url)
        self.last_kwargs = kwargs
        result = self.routes.get(url, requests.exceptions.ConnectionError())
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture(autouse=True)
def web(monkeypatch):
    fake = FakeWeb()
    monkeypatch.setattr(url_validator.socket, "getaddrinfo", fake.getaddrinfo)
    monkeypatch.setattr(url_validator.requests, "get", fake.get)
    return fake


# --- Valid URLs and normalization ---


def test_valid_url_is_returned(web):
    web.routes["https://example.com/"] = FakeResponse()
    assert validate_url("https://example.com") == "https://example.com/"


def test_request_handles_redirects_itself_and_identifies_the_crawler(web):
    web.routes["https://example.com/"] = FakeResponse()
    validate_url("https://example.com")
    assert web.last_kwargs["allow_redirects"] is False
    assert "BizBoostAI" in web.last_kwargs["headers"]["User-Agent"]
    assert web.last_kwargs["timeout"]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  https://example.com  ", "https://example.com/"),
        ("HTTPS://EXAMPLE.COM", "https://example.com/"),
        ("https://example.com.", "https://example.com/"),
        ("https://example.com:443/a", "https://example.com/a"),
        ("http://example.com:80/a", "http://example.com/a"),
        ("https://example.com:8443/a", "https://example.com:8443/a"),
        ("https://example.com/a?b=1#section", "https://example.com/a?b=1"),
        ("https://bücher.example", "https://xn--bcher-kva.example/"),
        ("https://[2606:4700::1111]/", "https://[2606:4700::1111]/"),
    ],
)
def test_normalize_url(raw, expected):
    assert normalize_url(raw) == expected


# --- Missing scheme ---


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("example.com", "https://example.com/"),
        ("www.example.com/about", "https://www.example.com/about"),
        ("example.com:8080", "https://example.com:8080/"),
        ("//example.com", "https://example.com/"),
    ],
)
def test_missing_scheme_defaults_to_https(raw, expected):
    assert normalize_url(raw) == expected


def test_missing_scheme_falls_back_to_http_when_https_is_unreachable(web):
    web.routes["http://example.com/"] = FakeResponse()
    assert validate_url("example.com") == "http://example.com/"
    assert web.fetched == ["https://example.com/", "http://example.com/"]


def test_explicit_https_does_not_fall_back_to_http(web):
    web.routes["http://example.com/"] = FakeResponse()
    with pytest.raises(UnreachableURLError):
        validate_url("https://example.com")
    assert web.fetched == ["https://example.com/"]


def test_missing_scheme_does_not_fall_back_when_https_is_unsafe(web):
    web.routes["https://example.com/"] = FakeResponse(302, "http://10.0.0.1/")
    web.routes["http://example.com/"] = FakeResponse()
    with pytest.raises(UnsafeURLError):
        validate_url("example.com")


# --- Invalid input ---


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        None,
        "not a url",
        "https://",
        "http:/example.com",
        "ftp://example.com",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "mailto:owner@example.com",
        "https://user:secret@example.com",
        "http://example.com\\@127.0.0.1/",
        "https://example.com/a\nb",
        "https://exa_mple.com",
        "https://example..com",
        "https://-example.com",
        "https://example.com:99999",
        "https://example",
    ],
)
def test_invalid_input_is_rejected_without_fetching(web, raw):
    with pytest.raises(InvalidURLError):
        validate_url(raw)
    assert web.fetched == []


# --- Localhost and private addresses ---


@pytest.mark.parametrize(
    "raw",
    [
        "localhost",
        "localhost:8501",
        "http://localhost:8501/admin",
        "https://LOCALHOST./",
        "http://app.localhost/",
        "http://printer.local/",
        "http://127.0.0.1/",
        "127.0.0.1:8000",
        "http://127.8.8.8/",
        "http://0.0.0.0/",
        "http://[::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://①②⑦.⓪.⓪.①/",
    ],
)
def test_localhost_is_rejected_without_fetching(web, raw):
    with pytest.raises(UnsafeURLError):
        validate_url(raw)
    assert web.fetched == []


@pytest.mark.parametrize(
    "raw",
    [
        "http://10.0.0.1/",
        "10.1.2.3",
        "http://10.255.255.255/",
        "http://192.168.0.1/",
        "192.168.1.1:8080",
        "http://172.16.0.1/",
        "http://172.31.255.255/",
        "http://169.254.169.254/latest/meta-data/",
        "http://100.64.0.1/",
        "http://224.0.0.1/",
        "http://[fd00::1]/",
        "http://[fe80::1]/",
        "http://[::ffff:10.0.0.1]/",
    ],
)
def test_private_ip_is_rejected_without_fetching(web, raw):
    with pytest.raises(UnsafeURLError):
        validate_url(raw)
    assert web.fetched == []


def test_address_just_outside_private_range_is_allowed(web):
    web.routes["http://172.32.0.1/"] = FakeResponse()
    assert validate_url("http://172.32.0.1/") == "http://172.32.0.1/"


@pytest.mark.parametrize(
    "ips",
    [["10.0.0.5"], ["127.0.0.1"], ["::1"], [PUBLIC_IP, "192.168.1.1"]],
)
def test_public_name_resolving_to_private_ip_is_rejected(web, ips):
    web.dns["sneaky.example.com"] = ips
    with pytest.raises(UnsafeURLError):
        validate_url("https://sneaky.example.com")
    assert web.fetched == []


def test_ensure_safe_url_checks_without_fetching(web):
    assert ensure_safe_url("https://Example.com") == "https://example.com/"
    with pytest.raises(UnsafeURLError):
        ensure_safe_url("http://192.168.1.1/")
    assert web.fetched == []


# --- Redirects ---


def test_public_redirect_returns_final_url(web):
    web.routes["https://example.com/"] = FakeResponse(301, "https://www.example.com/")
    web.routes["https://www.example.com/"] = FakeResponse()
    assert validate_url("https://example.com") == "https://www.example.com/"


def test_relative_redirect_is_followed(web):
    web.routes["https://example.com/"] = FakeResponse(302, "/home?x=1")
    web.routes["https://example.com/home?x=1"] = FakeResponse()
    assert validate_url("https://example.com") == "https://example.com/home?x=1"


@pytest.mark.parametrize(
    "target",
    [
        "http://10.0.0.1/",
        "http://192.168.1.1/admin",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost:8501/",
        "http://[::1]/",
        "file:///etc/passwd",
        "http://[bad/",
    ],
)
def test_unsafe_redirect_is_rejected_and_never_fetched(web, target):
    web.routes["https://example.com/"] = FakeResponse(302, target)
    with pytest.raises(UnsafeURLError, match="redirects"):
        validate_url("https://example.com")
    assert web.fetched == ["https://example.com/"]


def test_redirect_to_name_resolving_to_private_ip_is_rejected(web):
    web.dns["internal.example.com"] = ["10.0.0.5"]
    web.routes["https://example.com/"] = FakeResponse(302, "https://internal.example.com/")
    with pytest.raises(UnsafeURLError):
        validate_url("https://example.com")
    assert web.fetched == ["https://example.com/"]


def test_later_redirect_to_private_ip_is_rejected(web):
    web.routes["https://example.com/"] = FakeResponse(301, "https://www.example.com/")
    web.routes["https://www.example.com/"] = FakeResponse(302, "http://192.168.1.1/")
    with pytest.raises(UnsafeURLError):
        validate_url("https://example.com")
    assert web.fetched == ["https://example.com/", "https://www.example.com/"]


def test_redirect_loop_is_rejected(web):
    web.routes["https://example.com/"] = FakeResponse(302, "https://example.com/")
    with pytest.raises(UnreachableURLError, match="redirecting"):
        validate_url("https://example.com")
    assert len(web.fetched) == url_validator.MAX_REDIRECTS + 1


# --- Unreachable sites ---


def test_unknown_host_is_unreachable(web):
    web.dns["no-such-site.example"] = []
    with pytest.raises(UnreachableURLError):
        validate_url("https://no-such-site.example")
    assert web.fetched == []


@pytest.mark.parametrize(
    ("failure", "message"),
    [
        (requests.exceptions.ConnectionError(), "couldn't reach"),
        (requests.exceptions.ConnectTimeout(), "too long"),
        (requests.exceptions.ReadTimeout(), "too long"),
        (requests.exceptions.SSLError(), "secure connection"),
    ],
)
def test_connection_failures_are_unreachable(web, failure, message):
    web.routes["https://example.com/"] = failure
    with pytest.raises(UnreachableURLError, match=message):
        validate_url("https://example.com")


@pytest.mark.parametrize("status", [404, 410, 500, 503])
def test_missing_or_broken_homepage_is_unreachable(web, status):
    web.routes["https://example.com/"] = FakeResponse(status)
    with pytest.raises(UnreachableURLError):
        validate_url("https://example.com")


@pytest.mark.parametrize("status", [401, 403, 429])
def test_blocked_status_passes_through_to_the_crawler(web, status):
    web.routes["https://example.com/"] = FakeResponse(status)
    assert validate_url("https://example.com") == "https://example.com/"
