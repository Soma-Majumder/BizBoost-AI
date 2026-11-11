"""BizBoost AI: Streamlit interface. The audit runs in ``orchestrator.py``, the report is
built in ``report.py``, and this file only decides how they look.

One page, three screens: landing, scanning, results. Streamlit reruns this script on every
click, so the finished report is kept in the session (memory only, never saved).

Report text can quote the scanned website. Everything from a report goes through ``_h``
before it is placed in HTML, so a hostile page title cannot add links, images or code.
"""

import html
import re
import time
from pathlib import Path
from urllib.parse import quote, urlsplit

import streamlit as st
from dotenv import load_dotenv

from agent.output_validator import explain_audit
from agent.reasoning import BusinessContext
from orchestrator import AuditResult, run_audit
from report import (
    DATA_UNAVAILABLE,
    GOOD,
    NEEDS_ATTENTION,
    NEEDS_WORK,
    Report,
    ReportCategory,
    ReportCheck,
    build_report,
    score_text,
    to_text,
)
from url_validator import URLValidationError, validate_url

load_dotenv()  # API keys from .env, read by the PageSpeed, backlink and AI integrations

ASSETS = Path(__file__).resolve().parent / "assets"
FAVICON = ASSETS / "favicon.png"  # the BizBoost logo, shown in the browser tab
STREET_IMAGE = ASSETS / "main-street.png"

st.set_page_config(
    page_title="BizBoost AI",
    page_icon=str(FAVICON) if FAVICON.exists() else "📈",
    layout="wide",
)

REPORT_KEY = "report"
ADDRESS_KEY = "last_address"

STEPS = (
    "Checking the website is safe to scan",
    "Scanning up to 10 pages and checking homepage speed",
    "Running 5 SEO checks",
    "Writing your plain-English report",
)

# CSS class for each band, used by the score ring, cards and status words.
BAND_CLASS = {GOOD: "good", NEEDS_WORK: "work", NEEDS_ATTENTION: "attention", DATA_UNAVAILABLE: "none"}
BAND_DOT = {GOOD: "🟢", NEEDS_WORK: "🟠", NEEDS_ATTENTION: "🔴", DATA_UNAVAILABLE: "⚪"}
BAND_COLOR = {GOOD: "green", NEEDS_WORK: "orange", NEEDS_ATTENTION: "red"}

# Check status label -> CSS class, and evidence line label -> marker.
STATUS_CLASS = {"Problem": "attention", "Needs attention": "work", "Passed": "good", DATA_UNAVAILABLE: "none"}
LINE_MARKERS = {
    "Problem": ("attention", "!"),
    "Needs attention": ("work", "!"),
    "Passed": ("good", "✓"),
    "Not checked": ("none", "–"),
}

UNAVAILABLE_TIP = "We couldn't access this data, so it doesn't count against your score."

ABOUT_TEXT = """
**BizBoost AI** gives small-business owners a free SEO audit in plain English.

We scan up to 10 public pages of your website, check five areas of SEO, and show what to
fix first. Every finding shows the evidence behind it, and anything we can't check is marked
*Data unavailable* instead of counting against you.

Nothing is saved: your report exists only while it's on your screen.
"""

FAQ_TEXT = """
**Is it free?** Yes. No account and no payment.

**What do you look at?** Only public pages, the way a visitor or search engine sees them.
We never ask for logins or private data.

**What does "Data unavailable" mean?** We couldn't check that item, for example because a
page is built with JavaScript or a speed test didn't respond. It's left out of your score.

**Why did my site refuse the scan?** Some sites ask automated visitors to stay out. We
respect that and stop.

**Do you keep my report?** No. Download it if you want a copy.
"""

# Small line icons. Streamlit's HTML cleaner removes inline <svg>, so each icon is an
# image whose source is the SVG itself. They are fixed shapes, never website text.
BLUE, NAVY, GREEN, GREY = "#1a56db", "#0f2a5c", "#15803d", "#475569"


def _svg_img(body: str, alt: str = "", size: int = 24, view: str = "0 0 24 24") -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">{body}</svg>'
    alt_attr = f' alt="{html.escape(alt, quote=True)}"' if alt else ' alt="" aria-hidden="true"'
    return f'<img src="data:image/svg+xml;utf8,{quote(svg)}"{alt_attr} width="{size}" height="{size}">'


def _line_icon(paths: str, color: str = BLUE, size: int = 24) -> str:
    body = (
        f'<g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths}</g>'
    )
    return _svg_img(body, size=size)


ICONS = {
    "logo": _svg_img(
        f'<rect x="3" y="18" width="5" height="10" rx="1" fill="{BLUE}"/>'
        f'<rect x="11" y="13" width="5" height="15" rx="1" fill="{BLUE}"/>'
        f'<rect x="19" y="8" width="5" height="20" rx="1" fill="{NAVY}"/>'
        f'<path d="M3 14 L12 7 L18 10 L28 3 M23 3 H28 V8" stroke="{BLUE}" stroke-width="2.5" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        size=34, view="0 0 32 32",
    ),
    "keyword_optimization": _line_icon('<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2"/>'),
    "content_quality": _line_icon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="14" y2="17"/>'),
    "local_seo": _line_icon('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'),
    "technical_seo": _line_icon('<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>'),
    "credibility_backlinks": _line_icon('<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>'),
    # Three outlined bars of rising height, standing on one baseline.
    "scores": _line_icon('<rect x="2.5" y="13" width="4.5" height="8"/><rect x="9.75" y="8" width="4.5" height="13"/><rect x="17" y="3" width="4.5" height="18"/>', size=40),
    "evidence": _line_icon('<circle cx="10.5" cy="10.5" r="7"/><line x1="21" y1="21" x2="15.5" y2="15.5"/>', size=40),
    # A light bulb with short rays around the top.
    "fixes": _line_icon(
        '<path d="M9 15.5a5.5 5.5 0 1 1 6 0V17H9z"/><path d="M10 19.5h4"/><path d="M10.75 22h2.5"/>'
        '<path d="M12 1v2"/><path d="M4.5 3.8l1.4 1.4"/><path d="M19.5 3.8l-1.4 1.4"/>'
        '<path d="M2 10.5h2"/><path d="M20 10.5h2"/>',
        size=40,
    ),
    # A solid green shield with a white check.
    "shield": _svg_img(
        f'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill="{GREEN}"/>'
        '<polyline points="8.5 12 11 14.5 15.5 9.5" fill="none" stroke="#fff" stroke-width="2.2" '
        'stroke-linecap="round" stroke-linejoin="round"/>',
        size=22,
    ),
    # A speedometer: the dial, five tick marks and a needle pointing towards fast.
    "gauge": _svg_img(
        f'<g fill="none" stroke="{NAVY}" stroke-linecap="round">'
        '<path d="M3.5 17.5a8.5 8.5 0 1 1 17 0" stroke-width="2.4"/>'
        '<path d="M6.2 13.6l1.4.8M8.4 10.2l.9 1.3M12 8.9v1.6M15.6 10.2l-.9 1.3M17.8 13.6l-1.4.8" stroke-width="1.8"/>'
        '<path d="M12 17.5l3.6-4.6" stroke-width="2.4"/></g>'
        f'<circle cx="12" cy="17.5" r="1.7" fill="{NAVY}"/>',
        size=40,
    ),
    "info": _line_icon('<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="11"/><line x1="12" y1="8" x2="12" y2="8"/>', GREY, 16),
}

RING_COLORS = {"good": "#16a34a", "work": "#f59e0b", "attention": "#dc2626", "none": "#cbd5e1"}

CSS = """
<style>
.block-container { max-width: 1120px; padding-top: 4.5rem; padding-bottom: 3rem; }
[data-testid="stForm"] { border: 0; padding: 0; }

/* Header: one row with a thin line under it. Logo is a plain link back to the start. */
.st-key-bb-header { border-bottom: 1px solid #e2e8f0; padding-bottom: .6rem; margin-bottom: .5rem; }
a.bb-brand, a.bb-brand:hover, a.bb-brand:visited { text-decoration: none; color: #0f2a5c; }
a.bb-brand:focus-visible { outline: 2px solid #1a56db; outline-offset: 4px; border-radius: 6px; }

/* Address bar: the box and button share one height and read as a single bar. */
.st-key-bb-address [data-testid="stTextInputRootElement"] { height: 3.4rem; border-radius: 12px 0 0 12px; }
.st-key-bb-address [data-testid="stTextInput"] input { height: 100%; font-size: 1.05rem; padding-left: 1rem; }
.st-key-bb-address [data-testid="stFormSubmitButton"] button { height: 3.4rem; min-height: 3.4rem; border-radius: 0 12px 12px 0; }
@media (max-width: 640px) {
  /* The columns stack on phones, so each part gets its own rounded corners and a gap. */
  .st-key-bb-address [data-testid="stTextInputRootElement"] { border-radius: 12px; }
  .st-key-bb-address [data-testid="stFormSubmitButton"] button { border-radius: 12px; margin-top: .6rem; }
}

.bb { color: #0f1f3d; font-family: inherit; }
.bb p { margin: 0; }
.bb-good { color: #15803d; } .bb-work { color: #b45309; } .bb-attention { color: #dc2626; } .bb-none { color: #64748b; }

.bb-brand { display: flex; align-items: center; gap: .55rem; font-size: 1.45rem; font-weight: 700; color: #0f2a5c; }
.bb-brand img { width: 34px; height: 34px; }
.bb-brand span { color: #1a56db; }

.bb-hero h1 { font-size: clamp(2rem, 5vw, 3.3rem); line-height: 1.08; font-weight: 800; letter-spacing: -.02em; margin: .5rem 0 1rem; color: #0f1f3d; padding: 0; }
.bb-hero h1 em { font-style: normal; color: #1a56db; text-decoration: underline; text-decoration-thickness: 3px; text-underline-offset: 10px; }
[data-testid="stFormSubmitButton"] button p, .bb-big-button button p { font-size: 1.05rem; font-weight: 600; }
.bb img { display: inline-block; vertical-align: middle; }
.bb-hero .bb-sub { font-size: 1.15rem; color: #334155; margin-bottom: .75rem; }

.bb-trust { display: flex; align-items: center; justify-content: center; text-align: center; gap: .45rem; font-size: .9rem; color: #334155; margin: .25rem 0 1.5rem; }
.bb-trust img { width: 22px; height: 22px; flex: none; }

.bb-features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.bb-feature { border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem; text-align: center; box-shadow: 0 2px 8px rgba(15,42,92,.05); }
.bb-feature img { width: 40px; height: 40px; }
.bb-feature h3 { font-size: 1.05rem; margin: .5rem 0 .25rem; padding: 0; color: #0f1f3d; }
.bb-feature p { font-size: .92rem; color: #475569; }

.bb-scan h2 { font-size: clamp(1.6rem, 4vw, 2.3rem); font-weight: 800; margin: .5rem 0 1.5rem; padding: 0; color: #0f1f3d; }
.bb-scan h2 span { color: #1a56db; }
.bb-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: .5rem; margin-bottom: 1.25rem; }
.bb-step { text-align: center; font-size: .9rem; color: #64748b; position: relative; }
.bb-step::before { content: ""; position: absolute; top: 14px; left: -50%; width: 100%; height: 3px; background: #dbe3f0; z-index: 0; }
.bb-step:first-child::before { display: none; }
.bb-step.done::before, .bb-step.active::before { background: #1a56db; }
.bb-dot { position: relative; z-index: 1; width: 30px; height: 30px; margin: 0 auto .5rem; border-radius: 50%; border: 3px solid #cbd5e1; background: #fff; display: flex; align-items: center; justify-content: center; font-size: .85rem; font-weight: 700; color: #fff; }
.bb-step.done .bb-dot { background: #1a56db; border-color: #1a56db; }
.bb-step.active .bb-dot { border-color: #1a56db; border-top-color: transparent; animation: bb-spin 1s linear infinite; }
.bb-step.done, .bb-step.active { color: #0f1f3d; font-weight: 600; }
.bb-wait { display: flex; align-items: center; gap: 1rem; background: #eef3fd; border-radius: 14px; padding: 1.25rem 1.5rem; margin-top: 1rem; }
.bb-spinner { width: 34px; height: 34px; border-radius: 50%; border: 4px solid #c7d6f5; border-top-color: #1a56db; animation: bb-spin 1s linear infinite; flex: none; }
@keyframes bb-spin { to { transform: rotate(360deg); } }

.bb-report-title h2 { font-size: clamp(1.4rem, 3.5vw, 2rem); font-weight: 800; margin: 0; padding: 0; color: #0f1f3d; }
.bb-report-title p { color: #64748b; margin-top: .2rem; }

.bb-summary { display: flex; align-items: center; gap: 2rem; flex-wrap: wrap; margin: 1rem 0 1.25rem; }
.bb-summary img { flex: none; }
.bb-verdict { font-size: 1.35rem; line-height: 1.35; max-width: 32rem; padding-left: 2rem; border-left: 1px solid #e2e8f0; }

.bb-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .75rem; margin-bottom: 1.5rem; }
.bb-card { border: 1px solid #e2e8f0; border-radius: 14px; padding: 1rem .75rem; text-align: center; box-shadow: 0 2px 8px rgba(15,42,92,.05); }
.bb-card img { width: 26px; height: 26px; color: #1a56db; }
.bb-card .name { font-weight: 600; font-size: .95rem; margin: .35rem 0; min-height: 2.5em; display: flex; align-items: center; justify-content: center; }
.bb-card .score { font-size: 1.9rem; font-weight: 800; line-height: 1.1; }
.bb-card .band { font-size: .85rem; font-weight: 600; margin-top: .25rem; }
.bb-card .band::before { content: "●"; margin-right: .3rem; }
.bb-pill-none { display: inline-flex; align-items: center; gap: .3rem; background: #eef1f5; color: #475569; border-radius: 999px; padding: .2rem .6rem; font-size: .85rem; font-weight: 600; }
.bb-tip { position: relative; display: inline-flex; cursor: help; outline: none; }
.bb-tip img { width: 16px; height: 16px; color: #475569; }
.bb-tip .bb-tiptext { visibility: hidden; opacity: 0; position: absolute; bottom: 125%; right: -10px; width: 210px; background: #0f1f3d; color: #fff; text-align: left; font-size: .8rem; font-weight: 400; line-height: 1.35; border-radius: 8px; padding: .5rem .65rem; z-index: 10; transition: opacity .15s; }
.bb-tip:hover .bb-tiptext, .bb-tip:focus .bb-tiptext { visibility: visible; opacity: 1; }

.bb-fixes { border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 1.5rem; }
.bb-fixes-head { background: #0f2a5c; color: #fff; font-weight: 700; font-size: 1.1rem; padding: .7rem 1rem; }
.bb-fix { display: grid; grid-template-columns: 2rem 1fr 13rem; gap: 1rem; padding: 1rem; border-top: 1px solid #eef1f5; }
.bb-fix:first-of-type { border-top: 0; }
.bb-num { width: 28px; height: 28px; border-radius: 50%; background: #1a56db; color: #fff; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.bb-fix-title { font-weight: 700; margin-bottom: .25rem; }
.bb-fix-body div { font-size: .95rem; margin-top: .15rem; }
.bb-from { color: #64748b; font-size: .82rem !important; margin-top: .35rem !important; }
.bb-tag { display: inline-block; background: #eef3fd; color: #1a56db; font-size: .75rem; font-weight: 700; border-radius: 6px; padding: .1rem .45rem; margin-bottom: .3rem; }
.bb-evidence { font-size: .85rem; color: #334155; overflow-wrap: anywhere; }
.bb-done { background: #ecfdf3; border: 1px solid #bbf7d0; color: #15803d; border-radius: 14px; padding: 1rem; margin-bottom: 1.5rem; }
@media (max-width: 640px) { .bb-fix { grid-template-columns: 2rem 1fr; } .bb-evidence { grid-column: 2; } .bb-verdict { border-left: 0; padding-left: 0; } .bb-steps { grid-template-columns: 1fr 1fr; } .bb-step::before { display: none; } }

.bb-check { padding: .75rem 0; border-top: 1px solid #eef1f5; }
.bb-check:first-child { border-top: 0; }
.bb-check-head { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; font-size: 1rem; }
.bb-status { font-size: .78rem; font-weight: 700; border-radius: 999px; padding: .12rem .55rem; }
.bb-status.attention { background: #fde8e8; color: #b91c1c; } .bb-status.work { background: #fef3c7; color: #92400e; }
.bb-status.good { background: #dcfce7; color: #15803d; } .bb-status.none { background: #eef1f5; color: #475569; }
.bb-check p { margin-top: .35rem; font-size: .95rem; }
.bb-lines { list-style: none; padding: 0; margin: .5rem 0 0; }
.bb-lines li { display: flex; gap: .5rem; align-items: baseline; font-size: .9rem; padding: .15rem 0; overflow-wrap: anywhere; }
.bb-marker { flex: none; width: 1.1rem; height: 1.1rem; border-radius: 50%; color: #fff; font-size: .7rem; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }
.bb-marker.attention { background: #dc2626; } .bb-marker.work { background: #f59e0b; } .bb-marker.good { background: #16a34a; } .bb-marker.none { background: #94a3b8; }
.bb-line-label { flex: none; font-weight: 600; font-size: .8rem; min-width: 6.8rem; }
.bb-solution { margin-top: .6rem; background: #f6f9ff; border-left: 3px solid #1a56db; border-radius: 6px; padding: .5rem .75rem; font-size: .95rem; }
.bb-check-id { color: #64748b; font-size: .8rem; margin-top: .4rem; }

.bb-speed { display: flex; align-items: center; gap: 1rem; background: #f1f5fd; border-radius: 12px; padding: .85rem 1.25rem; }
.bb-speed img { width: 40px; height: 40px; flex: none; }
.bb-speed .t { font-weight: 700; font-size: 1rem; color: #0f1f3d; }
.bb-speed .d { font-size: .9rem; color: #1e293b; }
.bb-speed .d .bb-none { color: #1e293b; }

/* Result actions: an outlined blue "Run a new audit" next to a solid blue download. */
.st-key-new_audit button, .st-key-download_report button { min-height: 3rem; border-radius: 12px; }
.st-key-new_audit button { background: #fff; border: 1.5px solid #1a56db; color: #1a56db; }
.st-key-new_audit button:hover { background: #eef3fd; border-color: #1a56db; color: #1a56db; }
.st-key-new_audit button p, .st-key-download_report button p { font-weight: 700; font-size: 1rem; }
.bb-stopped { background: #fff7ed; border: 1px solid #fed7aa; border-radius: 14px; padding: 1rem 1.25rem; margin: 1rem 0; }
.bb-pages { list-style: none; padding: 0; margin: 0; font-size: .9rem; }
.bb-pages li { padding: .15rem 0; overflow-wrap: anywhere; }
</style>
"""


def _h(text: object) -> str:
    """Untrusted text, safe to put in HTML: tags and quotes become plain characters."""
    return html.escape(" ".join(str(text).split()), quote=True)


def _with_emoji(text: str, default: str) -> str:
    """The AI starts its lines with an emoji. Rule-based text does not, so give it the default."""
    return text if text[:1] and not text[0].isascii() else f"{default} {text}"


def _host(url: str) -> str:
    return (urlsplit(url).hostname or url).removeprefix("www.")


# --- Landing -----------------------------------------------------------------------------


def show_header() -> None:
    # A horizontal container keeps the logo, About and FAQ on one row, even on phones.
    # The key gives it a CSS class, used for the thin line under the header.
    with st.container(key="bb-header", horizontal=True, vertical_alignment="center", gap="small"):
        # The logo links to the start page. A fresh load clears any report on screen.
        st.html(
            f'<a class="bb bb-brand" href="./" target="_self" aria-label="BizBoost AI home">'
            f'{ICONS["logo"]}BizBoost <span>AI</span></a>',
            width="stretch",
        )
        with st.popover("About", type="tertiary"):
            st.markdown(ABOUT_TEXT)
        with st.popover("FAQ", type="tertiary"):
            st.markdown(FAQ_TEXT)


def show_landing():
    """Draw the landing screen. Returns (submitted, address, place for an error message)."""
    st.html(
        # The non-breaking space keeps the dash on the first line, after "back".
        '<div class="bb bb-hero"><h1>Find out what\'s holding your website back&nbsp;— '
        "<em>in under 2&nbsp;minutes.</em></h1>"
        '<p class="bb-sub">Free SEO audit. No account. No SEO knowledge needed.</p></div>'
    )
    with st.form("audit_form"), st.container(key="bb-address"):
        # No gap, so the box and the button form one bar with the same height.
        field, button = st.columns([4, 1], gap=None, vertical_alignment="center")
        raw_url = field.text_input(
            "Your website address",
            value=st.session_state.get(ADDRESS_KEY, ""),  # so a re-scan after a fix is one click
            placeholder="yourbusiness.com",
            label_visibility="collapsed",
        )
        submitted = button.form_submit_button("Start Audit →", type="primary", width="stretch")
    error_slot = st.empty()
    st.html(
        f'<div class="bb bb-trust">{ICONS["shield"]}Public data only · Every finding shows its '
        "evidence · We never guess</div>"
        '<div class="bb bb-features">'
        + _feature("scores", "Scores you can understand", "Get a clear SEO score and easy tips.")
        + _feature("evidence", "Evidence for every finding", "See exactly what we found and where.")
        + _feature("fixes", "Your top 3 fixes", "Simple steps to improve your site.")
        + "</div>"
    )
    if STREET_IMAGE.exists():  # a decoration, so the page still works without it
        # PNG, because Streamlit would otherwise re-save it as a blurrier JPEG.
        st.image(str(STREET_IMAGE), width="stretch", output_format="PNG")
    return submitted, raw_url, error_slot


def _feature(icon: str, title: str, text: str) -> str:
    return f'<div class="bb-feature">{ICONS[icon]}<h3>{title}</h3><p>{text}</p></div>'


# --- Scanning ----------------------------------------------------------------------------


def steps_html(current: int) -> str:
    """Steps before ``current`` are done, ``current`` is in progress, the rest are waiting."""
    items = []
    for number, label in enumerate(STEPS):
        state = "done" if number < current else "active" if number == current else ""
        mark = "✓" if state == "done" else ""
        items.append(f'<div class="bb-step {state}"><div class="bb-dot">{mark}</div>{label}</div>')
    return f'<div class="bb bb-steps">{"".join(items)}</div>'


def run_full_audit(url: str) -> Report:
    """Show the scanning screen while the audit runs, then return the finished report."""
    started = time.monotonic()
    st.html(f'<div class="bb bb-scan"><h2>Auditing <span>{_h(_host(url))}</span></h2></div>')
    steps = st.empty()
    steps.html(steps_html(1))  # the address was checked before this screen appeared
    progress = st.progress(0.0, text="Pages scanned: 0")
    st.html(
        '<div class="bb bb-wait"><div class="bb-spinner"></div><div><b>This usually takes less '
        "than 2 minutes.</b><br>Hang tight while we analyze your website.</div></div>"
    )

    def on_progress(done: int, total: int) -> None:
        progress.progress(min(done / total, 1.0), text=f"Pages scanned: {done} of {total}")

    audit = run_audit(url, on_progress=on_progress)
    explanation = None
    if audit.completed:
        steps.html(steps_html(3))  # the five checks run inside the audit, in a moment
        explanation = explain_audit(audit.findings, audit.scores, _business_context(audit))
    return build_report(audit, explanation, seconds=time.monotonic() - started)


def _business_context(audit: AuditResult) -> BusinessContext:
    return BusinessContext(name=audit.site.homepage.title)


# --- Results -----------------------------------------------------------------------------


def show_results(report: Report) -> None:
    pages = len(report.pages_scanned)
    date_text = f" • {report.scanned_on:%b} {report.scanned_on.day}, {report.scanned_on.year}" if report.scanned_on else ""
    st.html(
        f'<div class="bb bb-report-title"><h2>{_h(_host(report.url))} — SEO Health Report</h2>'
        f'<p>{pages} page{"" if pages == 1 else "s"} scanned{date_text}</p></div>'
    )

    if not report.completed:
        st.html(
            f'<div class="bb bb-stopped"><b>We stopped the audit.</b><br>'
            f'{_h(report.message or "The audit could not be completed.")}</div>'
        )
        show_pages(report)
        show_actions(report)
        return

    if report.note:
        st.info(report.note)
    st.html(summary_html(report) + cards_html(report) + top_fixes_html(report))

    for category in report.categories:
        show_category(category)
    show_pages(report)

    speed, again, download = st.columns([3, 1, 1], vertical_alignment="center")
    speed.html(speed_html(report))
    _action_buttons(report, again, download)
    if report.seconds is not None:
        st.caption(f"Finished in {report.seconds:.0f} seconds.")


def summary_html(report: Report) -> str:
    band = report.band
    css = BAND_CLASS[band]
    radius, width = 52, 12
    circumference = 2 * 3.14159 * radius
    filled = 0 if report.overall is None else circumference * max(0, min(report.overall, 100)) / 100
    number = "—" if report.overall is None else str(round(report.overall))
    caption = "Data unavailable" if report.overall is None else "/ 100"
    font = 'font-family="Source Sans Pro, Segoe UI, Arial, sans-serif" fill="#0f1f3d"'
    body = (
        f'<circle cx="70" cy="70" r="{radius}" fill="none" stroke="#e2e8f0" stroke-width="{width}"/>'
        f'<circle cx="70" cy="70" r="{radius}" fill="none" stroke="{RING_COLORS[css]}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-dasharray="{filled:.1f} {circumference:.1f}" transform="rotate(-90 70 70)"/>'
        f'<text x="70" y="78" text-anchor="middle" font-size="40" font-weight="800" {font}>{number}</text>'
        f'<text x="70" y="100" text-anchor="middle" font-size="14" {font}>{caption}</text>'
    )
    ring = _svg_img(body, alt=f"Overall score {score_text(report.overall)}", size=150, view="0 0 140 140")
    return f'<div class="bb bb-summary">{ring}<p class="bb-verdict">{_h(report.verdict)}</p></div>'


def cards_html(report: Report) -> str:
    cards = []
    for category in report.categories:
        css = BAND_CLASS[category.band]
        if category.score is None:
            value = (
                f'<span class="bb-pill-none">{DATA_UNAVAILABLE}'
                f'<span class="bb-tip" tabindex="0" aria-label="{_h(UNAVAILABLE_TIP)}">{ICONS["info"]}'
                f'<span class="bb-tiptext">{_h(UNAVAILABLE_TIP)}</span></span></span>'
            )
        else:
            value = (
                f'<div class="score bb-{css}">{round(category.score)}</div>'
                f'<div class="band bb-{css}">{category.band}</div>'
            )
        icon = ICONS.get(category.key, ICONS["scores"])
        cards.append(f'<div class="bb-card">{icon}<div class="name">{_h(category.label)}</div>{value}</div>')
    return f'<div class="bb bb-cards">{"".join(cards)}</div>'


def top_fixes_html(report: Report) -> str:
    if not report.top_fixes:
        return '<div class="bb bb-done">✓ We found nothing to fix in the checks we could measure.</div>'
    count = len(report.top_fixes)
    title = "Your top 3 fixes" if count == 3 else f"Your top {count} fix{'' if count == 1 else 'es'}"
    rows = []
    for number, fix in enumerate(report.top_fixes, start=1):
        action = f"<div><b>What to do:</b> {_h(_with_emoji(fix.action, '✅'))}</div>" if fix.action else ""
        evidence = (
            f'<div class="bb-evidence"><span class="bb-tag">Evidence</span><div>{_h(fix.evidence)}</div></div>'
            if fix.evidence else '<div class="bb-evidence"></div>'
        )
        rows.append(
            f'<div class="bb-fix"><div class="bb-num">{number}</div><div class="bb-fix-body">'
            f'<div class="bb-fix-title">{_h(fix.title)}</div>'
            f"<div><b>Why it matters:</b> {_h(fix.reason)}</div>{action}"
            f'<div class="bb-from">From the check: {_h(fix.name)}</div></div>{evidence}</div>'
        )
    return f'<div class="bb bb-fixes"><div class="bb-fixes-head">{title}</div>{"".join(rows)}</div>'


def category_label(category: ReportCategory) -> str:
    """Expander label. Only built from our own fixed text, never from the website."""
    if category.score is None:
        return f"{BAND_DOT[DATA_UNAVAILABLE]} {category.label} — {DATA_UNAVAILABLE}"
    band = category.band
    counts = f"{len(category.to_fix)} to fix"
    if category.unavailable:
        counts += f", {len(category.unavailable)} not checked"
    return (
        f"{BAND_DOT[band]} {category.label} (Score: {round(category.score)}) — "
        f":{BAND_COLOR[band]}[{band}] · {counts}"
    )


def show_category(category: ReportCategory) -> None:
    with st.expander(category_label(category)):
        checks = [check_html(check) for check in (*category.to_fix, *category.unavailable)]
        if category.passed:
            checks.append('<div class="bb-check"><b>Passed</b></div>')
            checks += [check_html(check) for check in category.passed]
        st.html(f'<div class="bb">{"".join(checks) or "<p>No checks in this category.</p>"}</div>')


def check_html(check: ReportCheck) -> str:
    css = STATUS_CLASS[check.status_label]
    parts = [
        f'<div class="bb-check"><div class="bb-check-head"><span class="bb-status {css}">'
        f"{check.status_label}</span><b>{_h(check.name)}</b></div>"
    ]
    if check.explanation:
        parts.append(f"<p>{_h(_with_emoji(check.explanation, '🔍'))}</p>")
    if check.why_it_matters:
        parts.append(f"<p>{_h(_with_emoji(check.why_it_matters, '💡'))}</p>")
    lines = []
    for line in check.evidence_lines:
        marker_css, mark = LINE_MARKERS[line.label]
        lines.append(
            f'<li><span class="bb-marker {marker_css}">{mark}</span>'
            f'<span class="bb-line-label bb-{marker_css}">{line.label}</span><span>{_h(line.text)}</span></li>'
        )
    parts.append(f'<ul class="bb-lines">{"".join(lines)}</ul>')
    if check.action:
        parts.append(
            f'<div class="bb-solution"><b>🛠️ Solution:</b> {_h(_with_emoji(check.action, "✅"))}</div>'
        )
    parts.append(f'<div class="bb-check-id">Check: {_h(check.check_id)}</div></div>')
    return "".join(parts)


def speed_html(report: Report) -> str:
    speed = report.speed
    if speed is None or speed.status_label == DATA_UNAVAILABLE:
        reason = speed.evidence[0] if speed and speed.evidence else "The speed test didn't run."
        detail = f'<span class="bb-none">{DATA_UNAVAILABLE}</span> · {_h(reason)}'
    else:
        css = STATUS_CLASS[speed.status_label]
        detail = f'<span class="bb-{css}">{_h(speed.evidence[0])}</span>'
    return (
        f'<div class="bb bb-speed">{ICONS["gauge"]}<div><div class="t">Homepage speed</div>'
        f'<div class="d">{detail}</div></div></div>'
    )


def show_pages(report: Report) -> None:
    with st.expander(f"Pages scanned: {len(report.pages_scanned)}"):
        items = "".join(f"<li>{_h(url)}</li>" for url in report.pages_scanned) or "<li>None</li>"
        st.html(f'<ul class="bb bb-pages">{items}</ul>')
    if report.pages_not_scanned:
        with st.expander(f"Pages not scanned: {len(report.pages_not_scanned)}"):
            items = "".join(
                f"<li>{_h(page.url)}: {_h(page.reason)}</li>" for page in report.pages_not_scanned
            )
            st.html(f'<ul class="bb bb-pages">{items}</ul>')


def show_actions(report: Report) -> None:
    _, again, download = st.columns([3, 1, 1])
    _action_buttons(report, again, download)


def _action_buttons(report: Report, again, download) -> None:
    # The keys give each button a CSS class, used for the outlined and solid styles.
    again.button("Run a new audit", on_click=_clear_report, width="stretch", key="new_audit")
    download.download_button(
        "Download report",
        data=to_text(report),
        file_name=_report_file_name(report.url),
        mime="text/plain",
        type="primary",
        icon=":material/download:",
        width="stretch",
        key="download_report",
    )


def _report_file_name(url: str) -> str:
    host = re.sub(r"[^a-z0-9.-]", "", (urlsplit(url).hostname or "").lower())
    return f"bizboost-report-{host or 'website'}.txt"


def _clear_report() -> None:
    st.session_state.pop(REPORT_KEY, None)


# --- Page --------------------------------------------------------------------------------


def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    show_header()

    report = st.session_state.get(REPORT_KEY)
    if report:
        show_results(report)
        return

    screen = st.empty()
    with screen.container():
        submitted, raw_url, error_slot = show_landing()
    if not submitted:
        return
    st.session_state[ADDRESS_KEY] = raw_url

    try:
        with error_slot.container(), st.spinner("Checking your website address..."):
            url = validate_url(raw_url)
    except URLValidationError as error:
        error_slot.error(str(error))
        return

    screen.empty()
    with screen.container():
        report = run_full_audit(url)
    screen.empty()
    st.session_state[REPORT_KEY] = report
    show_results(report)


if __name__ == "__main__":  # Streamlit runs the script as __main__; tests can import it safely
    main()
