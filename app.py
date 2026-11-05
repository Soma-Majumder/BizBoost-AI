"""BizBoost AI: Streamlit interface. The audit itself runs in ``orchestrator.py``."""

import streamlit as st
from dotenv import load_dotenv

from orchestrator import AuditResult, run_audit
from url_validator import URLValidationError, validate_url

load_dotenv()  # API keys from .env, read by the PageSpeed, backlink and AI integrations

st.set_page_config(page_title="BizBoost AI", page_icon="🚀")

CATEGORY_LABELS = {
    "technical_seo": "Technical SEO",
    "keyword_optimization": "Keywords",
    "content_quality": "Content",
    "local_seo": "Local SEO",
    "credibility_backlinks": "Credibility",
}
DATA_UNAVAILABLE = "Data unavailable"


def show_audit(url: str) -> None:
    progress = st.progress(0.0, text="Starting the scan...")

    def on_progress(done: int, total: int) -> None:
        progress.progress(min(done / total, 1.0), text=f"Scanned {done} of {total} pages")

    with st.spinner("Running your audit. This can take up to 2 minutes."):
        result = run_audit(url, on_progress=on_progress)
    progress.empty()

    if result.completed:
        show_scores(result)
    else:
        st.warning(result.site.message)
    show_pages(result)


def show_scores(result: AuditResult) -> None:
    """A simple score summary. The full results dashboard is issue #17."""
    st.metric("Overall score", _score_text(result.scores.overall))
    categories = result.scores.categories
    for column, key in zip(st.columns(len(CATEGORY_LABELS)), CATEGORY_LABELS):
        column.metric(CATEGORY_LABELS[key], _score_text(categories[key].score))


def show_pages(result: AuditResult) -> None:
    st.write(f"Pages scanned: {len(result.site.pages)}")
    if result.site.not_scanned:
        with st.expander(f"Pages not scanned: {len(result.site.not_scanned)}"):
            for page in result.site.not_scanned:
                st.markdown(f"- `{page.url}`: {page.reason}")


def _score_text(score: float | None) -> str:
    return DATA_UNAVAILABLE if score is None else f"{round(score)} / 100"


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

    if not submitted:
        return

    try:
        with st.spinner("Checking your website address..."):
            url = validate_url(raw_url)
    except URLValidationError as error:
        st.error(str(error))
        return

    st.success(f"Scanning {url}")
    show_audit(url)


main()
