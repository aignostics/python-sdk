"""Tests for the project constants in aignostics.constants."""

import pytest

from aignostics.constants import CONSOLE_URL, DEPRECATION_NOTICE, PLATFORM_API_DOCS_URL


@pytest.mark.unit
def test_deprecation_notice_names_end_date_and_alternatives() -> None:
    """The deprecation notice names the end of support and both alternatives."""
    assert "April 30, 2027" in DEPRECATION_NOTICE
    assert PLATFORM_API_DOCS_URL in DEPRECATION_NOTICE
    assert CONSOLE_URL in DEPRECATION_NOTICE
