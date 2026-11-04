from crawler.parser import parse_page, same_site

URL = "https://example.com/"

FULL_PAGE = b"""<!doctype html>
<html lang="en"><head>
<title>  Example Bakery |  Brooklyn </title>
<meta name="description" content="Fresh bread daily.">
<meta name="viewport" content="width=device-width">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Example Bakery">
<link rel="canonical" href="/">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Bakery","name":"Example",
 "address":{"@type":"PostalAddress","streetAddress":"123 Main St","addressLocality":"Brooklyn",
            "addressRegion":"NY","postalCode":"11201"}}
</script>
<script type="application/ld+json">{ this is not json </script>
<style>.x{color:red}</style>
</head><body>
<h1>Example Bakery</h1><h2>Our   Bread</h2><h3></h3>
<p>Call us at (718) 555-0100 or email Hello@Example.com. Fresh bread baked daily.</p>
<address>123 Main St<br>Brooklyn, NY</address>
<a href="tel:+1-718-555-0100">Call</a>
<a href="mailto:hello@example.com?subject=Hi">Email</a>
<a href="/menu/#top">Menu</a><a href="/menu/">Menu again</a><a href="#top">Top</a>
<a href="https://www.example.com/about">About</a>
<a href="https://other.com/page">Other</a>
<a href="https://www.facebook.com/examplebakery">Facebook</a>
<a href="https://www.facebook.com/sharer/sharer.php?u=x">Share</a>
<a href="javascript:void(0)">JS</a><a href="mailto:x@y.com">Mail</a>
<img src="/loaf.jpg" alt="A loaf"><img src="/deco.jpg" alt=""><img src="/noalt.jpg">
<img src="data:image/gif;base64,AAAA"><img data-src="/lazy.jpg" alt="Lazy">
<iframe src="https://www.google.com/maps/embed?pb=1"></iframe>
<script>var secret = "should not appear in text";</script>
</body></html>"""


def parse(body=FULL_PAGE, **kw):
    return parse_page(body, kw.get("url", URL), 200, 0.4)


def test_head_tags_are_extracted_and_cleaned():
    page = parse()
    assert page.title == "Example Bakery | Brooklyn"
    assert page.meta_description == "Fresh bread daily."
    assert page.canonical == "https://example.com/"
    assert page.meta_robots == "index, follow"
    assert page.lang == "en"
    assert page.has_viewport
    assert page.open_graph == {"og:title": "Example Bakery"}
    assert page.status_code == 200 and page.fetch_seconds == 0.4


def test_missing_head_tags_are_none_or_false():
    page = parse(b"<html><body><p>Hi</p></body></html>")
    assert page.title is None and page.meta_description is None and page.canonical is None
    assert page.lang is None and not page.has_viewport and page.meta_robots is None


def test_headings_skip_empty_ones_and_normalize_space():
    assert [(h.level, h.text) for h in parse().headings] == [(1, "Example Bakery"), (2, "Our Bread")]


def test_text_excludes_scripts_and_styles():
    page = parse()
    assert "should not appear" not in page.text and "color:red" not in page.text
    assert "Fresh bread baked daily" in page.text


def test_links_split_internal_external_and_deduplicated():
    page = parse()
    internal = [l.url for l in page.internal_links]
    assert internal == ["https://example.com/menu/", "https://www.example.com/about"]
    assert [l.url for l in page.external_links][0] == "https://other.com/page"
    assert not any(u.startswith(("javascript", "mailto", "tel")) for u in internal)


def test_social_links_found_and_share_buttons_ignored():
    assert parse().social_links == ("https://www.facebook.com/examplebakery",)


def test_images_keep_alt_distinction_and_skip_data_uris():
    images = {i.src.rsplit("/", 1)[-1]: i.alt for i in parse().images}
    assert images == {"loaf.jpg": "A loaf", "deco.jpg": "", "noalt.jpg": None, "lazy.jpg": "Lazy"}


def test_phones_and_emails_are_deduplicated_across_tel_links_and_text():
    page = parse()
    assert page.phones == ("+1-718-555-0100",)
    assert page.emails == ("hello@example.com", "x@y.com")


def test_addresses_from_address_tag_and_schema():
    page = parse()
    assert "123 Main St, Brooklyn, NY" in page.addresses[0]
    assert "123 Main St, Brooklyn, NY, 11201" in page.addresses


def test_json_ld_parsed_and_broken_block_ignored():
    page = parse()
    assert len(page.structured_data) == 1 and page.structured_data[0]["@type"] == "Bakery"


def test_map_embed_detected():
    assert parse().has_map_embed
    assert not parse(b"<html><body><p>x</p></body></html>").has_map_embed


def test_js_shell_is_flagged_but_content_page_is_not():
    shell = b'<html><body><div id="root"></div><script src="a.js"></script></body></html>'
    assert parse(shell).likely_js_rendered
    assert not parse().likely_js_rendered
    wordy = b'<html><body><div id="root">' + b"word " * 80 + b"</div></body></html>"
    assert not parse(wordy).likely_js_rendered


def test_same_site_ignores_www_and_case():
    assert same_site("https://www.Example.com/a", "http://example.com/b")
    assert not same_site("https://example.com", "https://example.org")


def test_requested_url_is_passed_through():
    page = parse_page(b"<html></html>", URL, 200, 0.1, requested_url="http://example.com/")
    assert page.requested_url == "http://example.com/"


def test_garbage_input_does_not_crash():
    assert parse(b"").text == ""
    assert parse(b"\xff\xfe not html at all <<<").status_code == 200


def test_plain_text_address_is_found_and_not_confused_with_a_nearby_phone():
    body = (b"<html><body><footer>Sunday 11:00 AM - 9:45 PM 212-233-2921 "
            b"77 Mulberry St, New York 10013 Follow us</footer></body></html>")
    page = parse(body)
    assert page.addresses == ("77 Mulberry St, New York 10013",)
    assert page.phones == ("212-233-2921",)


def test_plain_text_address_variants():
    cases = {
        "Visit 1600 Pennsylvania Avenue NW, Washington, DC 20500 today": "1600 Pennsylvania Avenue NW, Washington, DC 20500",
        "Find us at 350 5th Ave, New York, NY 10118.": "350 5th Ave, New York, NY 10118",
    }
    for text, expected in cases.items():
        assert expected in parse(f"<html><body><p>{text}</p></body></html>".encode()).addresses


def test_text_without_a_street_and_zip_is_not_an_address():
    page = parse(b"<html><body><p>We sold 500 loaves in 2024 on Main Street last week.</p></body></html>")
    assert page.addresses == ()
