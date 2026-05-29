"""Tests for console module."""

import pytest

from aignostics_sdk.utils._console import _get_console


@pytest.mark.unit
def test_get_console_default_width(monkeypatch: pytest.MonkeyPatch, record_property) -> None:
    """Test that the console is created with default width when no env var is set."""
    record_property("tested-item-id", "SPEC-UTILS-CONSOLE")

    monkeypatch.delenv("AIGNOSTICS_CONSOLE_WIDTH", raising=False)
    console = _get_console()
    assert console.width == 80, "Default console width should be 80."


@pytest.mark.unit
def test_get_console_custom_width(monkeypatch: pytest.MonkeyPatch, record_property) -> None:
    """Test that the console is created with custom width from env var."""
    record_property("tested-item-id", "SPEC-UTILS-CONSOLE")

    monkeypatch.setenv("AIGNOSTICS_CONSOLE_WIDTH", "100")
    console = _get_console()
    assert console.width == 100, "Console width should be set to 100 from env var."
