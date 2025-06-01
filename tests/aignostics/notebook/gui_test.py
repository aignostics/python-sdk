"""Tests to verify the GUI functionality of the Notebook module."""

import logging
from asyncio import sleep

import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.utils import gui_register_pages


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


async def _assert_notified(user: User, expected_notification: str, wait_seconds=5) -> str:
    """Check if the user receives a notification within the specified time."""
    for _ in range(wait_seconds):
        matching_messages = [msg for msg in user.notify.messages if expected_notification in msg]
        if matching_messages:
            return matching_messages[0]
        await sleep(1)
    pytest.fail(f"No notification containing '{expected_notification}' was found within {wait_seconds} seconds")


@pytest.mark.sequential
@pytest.fixture
def silent_logging(caplog) -> None:
    """Suppress logging output during test execution.

    Args:
        caplog (pytest.LogCaptureFixture): The pytest fixture for capturing log messages.

    Yields:
        None: This fixture doesn't yield any value.
    """
    with caplog.at_level(logging.CRITICAL + 1):
        yield


async def test_gui_marimo_extension(user: User, runner: CliRunner, silent_logging: None) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    gui_register_pages()

    # Step 1: Check we are on the Notebook page
    await user.open("/notebook")
    await user.should_see("Manage your Marimo Extension")

    await user.should_see(marker="BUTTON_NOTEBOOK_LAUNCH")
    user.find(marker="BUTTON_NOTEBOOK_LAUNCH").click()
    await _assert_notified(user, "Launching Python Notebook...", wait_seconds=5)

    await user.should_see(marker="BUTTON_NOTEBOOK_BACK")
    await user.should_not_see("Manage your Marimo Extension")
    user.find(marker="BUTTON_NOTEBOOK_BACK").click()

    await user.should_see("Marimo Extension")
