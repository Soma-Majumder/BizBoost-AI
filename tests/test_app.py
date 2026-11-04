from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from url_validator import InvalidURLError

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _submit(url, side_effect=None, return_value=None):
    with patch("url_validator.validate_url", side_effect=side_effect, return_value=return_value):
        at = AppTest.from_file(APP).run()
        at.text_input[0].set_value(url)
        at.button[0].click()
        return at.run()


def test_landing_page_shows_form_and_no_error():
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert at.title[0].value.endswith("BizBoost AI")
    assert at.button[0].label == "Start Audit"
    assert not at.error


def test_invalid_url_shows_plain_message():
    at = _submit("not a url", side_effect=InvalidURLError("Bad address."))
    assert at.error[0].value == "Bad address."


def test_valid_url_starts_audit():
    at = _submit("example.com", return_value="https://example.com/")
    assert not at.error
    assert "https://example.com/" in at.success[0].value
