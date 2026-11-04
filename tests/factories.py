"""Build sample crawl data so analyzers can be written and tested without a crawler."""

from crawler.models import CrawlStatus, Heading, Image, Link, PageData, SiteData


def make_page(**overrides) -> PageData:
    """A healthy sample page. Override any field to create a problem."""
    base = dict(
        url="https://example.com/",
        status_code=200,
        fetch_seconds=0.3,
        title="Example Bakery | Fresh Bread in Brooklyn",
        meta_description=(
            "Family-run bakery in Brooklyn selling fresh bread, pastries and cakes baked daily."
        ),
        canonical="https://example.com/",
        lang="en",
        has_viewport=True,
        headings=(Heading(1, "Example Bakery"), Heading(2, "Our Bread")),
        text="Fresh bread baked daily in Brooklyn. " * 60,
        images=(Image("https://example.com/loaf.jpg", "A fresh loaf of bread"),),
        internal_links=(Link("https://example.com/menu/", "Menu"),),
        external_links=(Link("https://www.facebook.com/examplebakery", "Facebook"),),
        phones=("(718) 555-0100",),
        addresses=("123 Main St, Brooklyn, NY 11201",),
        social_links=("https://www.facebook.com/examplebakery",),
    )
    base.update(overrides)
    return PageData(**base)


def make_site(*pages: PageData, **overrides) -> SiteData:
    """A successful crawl. With no pages given, it contains one healthy homepage."""
    base = dict(
        start_url="https://example.com/",
        status=CrawlStatus.OK,
        pages=pages or (make_page(),),
        robots_txt_found=True,
        sitemap_url="https://example.com/sitemap.xml",
        sitemap_page_count=5,
    )
    base.update(overrides)
    return SiteData(**base)
