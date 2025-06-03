"""Tests to verify the GUI functionality of the info module."""

import logging
from collections.abc import Generator

import pytest
from nicegui.testing import User

from aignostics.utils import __project_name__, gui_register_pages


@pytest.fixture
def silent_logging(caplog) -> Generator[None, None, None]:
    """Suppress logging output during test execution.

    Args:
        caplog (pytest.LogCaptureFixture): The pytest fixture for capturing log messages.

    Yields:
        None: This fixture doesn't yield any value.
    """
    with caplog.at_level(logging.CRITICAL + 1):
        yield


@pytest.mark.sequential
async def test_gui_system(user: User, silent_logging) -> None:
    """Test that the user sees the info page, and the output includes the project name."""
    gui_register_pages()
    await user.open("/system")
    await user.should_see("Health")
    await user.should_see("Info")
    await user.should_see("Settings")
    await user.should_see(__project_name__)
