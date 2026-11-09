"""BizBoost AI: Streamlit interface. The audit runs in ``orchestrator.py``, the report is
built in ``report.py``, and this file only decides how they look.

Text in the report can quote the scanned website, so it always goes through ``_md`` before
display. Otherwise a hostile page title could add its own links or images to the report.
"""

import re
import time
from urllib.parse import urlsplit

import streamlit as st
from dotenv import load_dotenv

from agent.output_validator import explain_audit
from agent.reasoning import BusinessContext
from orchestrator import AuditResult, run_audit
from report import Report, ReportCategory, ReportCheck, build_report, score_text, to_text
from url_validator import URLValidationError, validate_url

load_dotenv()  # API keys from .env, read by the PageSpeed, backlink and AI integrations

st.set_page_config(page_title="BizBoost AI", page_icon="🚀")

# Streamlit reruns this script on every click, so the report is kept for this browser
# session, in memory only. Nothing is saved after the session ends.
REPORT_KEY = "report"

STATUS_ICONS = {"Problem": "❌", "Needs attention": "⚠️", "Data unavailable": "➖", "Passed": "✅"}

_MARKDOWN_PUNCTUATION_RE = re.compile(r"([!-/:-@\[-`{-~])")
# Streamlit also turns bare addresses into links, even when their symbols are escaped.
# An invisible space inside these patterns stops that without changing how they look.
_AUTOLINK_RE = re.compile(r"(?<=:)(?=//)|(?<=www)(?=\.)|(?=@)", re.I)
INVISIBLE_SPACE = "​"


def _md(text: str) -> str:
    """Untrusted text, safe to put in Markdown: every symbol shows as itself, no links."""
    unlinked = _AUTOLINK_RE.sub(INVISIBLE_SPACE, " ".join(text.split()))
    return _MARKDOWN_PUNCTUATION_RE.sub(r"\\\1", unlinked)


def run_full_audit(url: str) -> Report:
    started = time.monotonic()
    progress = st.progress(0.0, text="Starting the scan...")

    def on_progress(done: int, total: int) -> None:
        progress.progress(min(done / total, 1.0), text=f"Scanned {done} of {total} pages")

    with st.spinner("Scanning your website. The full audit can take up to 2 minutes."):
        audit = run_audit(url, on_progress=on_progress)
    progress.empty()

    explanation = None
    if audit.completed:
        with st.spinner("Writing your plain-language explanations..."):
            explanation = explain_audit(audit.findings, audit.scores, _business_context(audit))
    return build_report(audit, explanation, seconds=time.monotonic() - started)


def _business_context(audit: AuditResult) -> BusinessContext:
    return BusinessContext(name=audit.site.homepage.title)


def show_report(report: Report) -> None:
    st.divider()
    st.subheader(f"Results for {_md(report.url)}")

    if not report.completed:
        st.warning(report.message or "The audit could not be completed.")
        show_pages(report)
        show_actions(report)
        return

    if report.note:
        st.info(report.note)
    show_scores(report)
    show_top_fixes(report)

    st.subheader("All findings")
    for category in report.categories:
        show_category(category)

    show_pages(report)
    if report.seconds is not None:
        st.caption(f"Finished in {report.seconds:.0f} seconds.")
    show_actions(report)


def show_scores(report: Report) -> None:
    st.metric("Overall score", score_text(report.overall))
    for category in report.categories:
        if category.score is None:
            st.markdown(f"**{category.label}:** {score_text(None)}")
        else:
            st.progress(category.score / 100, text=f"**{category.label}:** {score_text(category.score)}")


def show_top_fixes(report: Report) -> None:
    st.subheader("What to fix first")
    if not report.top_fixes:
        st.success("We found nothing to fix in the checks we could measure.")
        return
    for number, fix in enumerate(report.top_fixes, start=1):
        st.markdown(f"**{number}. {_md(fix.title)}**")
        st.markdown(_md(fix.reason))
        if fix.action:
            st.markdown(f"✅ **What to do:** {_md(fix.action)}")
        st.caption(f"From the check: {_md(fix.name)} ({_md(fix.check_id)})")


def show_category(category: ReportCategory) -> None:
    counts = [f"{len(category.to_fix)} to fix"]
    if category.unavailable:
        counts.append(f"{len(category.unavailable)} unavailable")
    label = f"{category.label}: {score_text(category.score)} ({', '.join(counts)})"

    with st.expander(label):
        for check in (*category.to_fix, *category.unavailable):
            show_check(check)
        if category.passed:
            st.markdown("**Passed**")
            for check in category.passed:
                show_check(check)


def _with_emoji(text: str, default: str) -> str:
    """The AI starts its lines with an emoji. Rule-based text does not, so give it the default."""
    return text if text[:1] and not text[0].isascii() else f"{default} {text}"


def show_check(check: ReportCheck) -> None:
    icon = STATUS_ICONS[check.status_label]
    st.markdown(f"{icon} **{_md(check.name)}**: {check.status_label}")
    if check.explanation:
        st.markdown(f"- {_md(_with_emoji(check.explanation, '🔍'))}")
    if check.why_it_matters:
        st.markdown(f"- {_md(_with_emoji(check.why_it_matters, '💡'))}")
    st.markdown("\n".join(f"- {_md(line)}" for line in check.evidence))
    if check.action:
        st.markdown(f"**🛠️ Solution for {_md(check.name)}**")
        st.markdown(f"- {_md(_with_emoji(check.action, '✅'))}")
    st.caption(f"Check: {_md(check.check_id)}")


def show_pages(report: Report) -> None:
    with st.expander(f"Pages scanned: {len(report.pages_scanned)}"):
        for url in report.pages_scanned:
            st.markdown(f"- {_md(url)}")
    if report.pages_not_scanned:
        with st.expander(f"Pages not scanned: {len(report.pages_not_scanned)}"):
            for page in report.pages_not_scanned:
                st.markdown(f"- {_md(page.url)}: {_md(page.reason)}")


def show_actions(report: Report) -> None:
    download, again = st.columns(2)
    download.download_button(
        "Download report",
        data=to_text(report),
        file_name=_report_file_name(report.url),
        mime="text/plain",
    )
    again.button("Run another audit", on_click=_clear_report)


def _report_file_name(url: str) -> str:
    host = re.sub(r"[^a-z0-9.-]", "", (urlsplit(url).hostname or "").lower())
    return f"bizboost-report-{host or 'website'}.txt"


def _clear_report() -> None:
    st.session_state.pop(REPORT_KEY, None)


def show_landing() -> None:
    st.title("🚀 BizBoost AI")
    st.subheader("A free SEO audit for your website, in plain English.")
    st.write(
        "Enter your public website address. We scan up to 10 pages, check five areas "
        "of SEO, and show you what to fix first, with the evidence behind every finding."
    )
    col1, col2, col3 = st.columns(3)
    col1.markdown("**No account**  \nJust paste your address.")
    col2.markdown("**Plain language**  \nNo SEO jargon.")
    col3.markdown("**Evidence-backed**  \nEvery finding shows where it came from.")
    with st.expander("What do we check?"):
        st.markdown(
            "- Keyword optimization\n"
            "- Content quality\n"
            "- Local SEO\n"
            "- Technical SEO and site speed\n"
            "- Credibility and backlinks\n\n"
            "Anything we can't check is marked **Data unavailable**, never counted "
            "against you."
        )


def main() -> None:
    show_landing()
    st.divider()

    with st.form("audit_form"):
        raw_url = st.text_input(
            "Your website address",
            placeholder="www.yourbusiness.com",
            help="You can leave off https://. Only public websites can be scanned.",
        )
        submitted = st.form_submit_button("Start Audit", type="primary")

    if submitted:
        _clear_report()
        try:
            with st.spinner("Checking your website address..."):
                url = validate_url(raw_url)
        except URLValidationError as error:
            st.error(str(error))
            return
        st.session_state[REPORT_KEY] = run_full_audit(url)

    report = st.session_state.get(REPORT_KEY)
    if report:
        show_report(report)


main()
