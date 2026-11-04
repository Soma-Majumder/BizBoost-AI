"""BizBoost AI: Streamlit interface and audit orchestrator."""

import streamlit as st

from url_validator import URLValidationError, validate_url

st.set_page_config(page_title="BizBoost AI", page_icon="🚀")


def run_audit(url: str) -> None:
    """Placeholder for the audit pipeline (crawl, analyze, score, explain).

    The orchestrator (issue #16) will replace this body.
    """
    st.info(
        "The audit engine isn't connected yet. "
        "Your address passed validation and is ready to scan."
    )


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
    run_audit(url)


main()
