"""Tests to verify the GUI functionality of the QuPath."""

import logging
import os
import platform
import re
from asyncio import sleep
from collections.abc import Generator

import appdirs
import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.qupath._service import QUPATH_VERSION
from aignostics.utils import __project_name__, gui_register_pages

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"


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
async def test_gui_qupath_install(user: User, runner: CliRunner, silent_logging: None) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    gui_register_pages()

    result = runner.invoke(cli, ["qupath", "uninstall"])
    was_installed = result.exit_code == 0

    # Step 1: Check we are on the QuPath page
    await user.open("/qupath")
    await user.should_see("QuPath Extension")

    # Step 2: Check we indicate QuPath is not installed
    await user.should_see("Install QuPath to enable visualizing your Whole Slide Image and application results")
    await sleep(5)  # Health UI updated in background
    await user.should_see("Launchpad is unhealthy")
    await user.should_see(marker="BUTTON_QUPATH_INSTALL")

    # Step 3: Install QuPath
    user.find("BUTTON_QUPATH_INSTALL").click()
    app_dir = appdirs.user_data_dir(__project_name__)
    await _assert_notified(
        user,
        f"QuPath installed successfully to '{app_dir}",
        wait_seconds=35,
    )

    # Step 4: Check we indicate QuPath is installed
    await user.should_see(f"QuPath {QUPATH_VERSION} is installed and ready to execute.")
    await sleep(5)  # Health UI updated in background
    await user.should_see("Launchpad is healthy")
    await user.should_see(marker="BUTTON_QUPATH_LAUNCH")

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])


@pytest.mark.sequential
async def test_gui_qupath_install_and_launch(user: User, runner: CliRunner, silent_logging: None) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    if platform.system() == "Linux":
        pytest.skip("unsupported test for Linux platform")

    gui_register_pages()

    result = runner.invoke(cli, ["qupath", "uninstall"])
    was_installed = result.exit_code == 0

    # Step 1: Check we are on the QuPath page
    await user.open("/qupath")
    await user.should_see("QuPath Extension")

    # Step 2: Check we indicate QuPath is not installed
    await user.should_see("Install QuPath to enable visualizing your Whole Slide Image and application results")
    await user.should_see(marker="BUTTON_QUPATH_INSTALL")

    # Step 3: Install QuPath
    user.find("BUTTON_QUPATH_INSTALL").click()
    app_dir = appdirs.user_data_dir(__project_name__)
    await _assert_notified(
        user,
        f"QuPath installed successfully to '{app_dir}",
        wait_seconds=35,
    )

    # Step 4: Check we indicate QuPath is installed
    await user.should_seef(f"QuPath {QUPATH_VERSION} is installed and ready to execute.")
    await user.should_see(marker="BUTTON_QUPATH_LAUNCH")

    # Step 5: Check we can launch QuPath
    user.find("BUTTON_QUPATH_LAUNCH").click()
    message = await _assert_notified(
        user,
        "QuPath launched successfully with process id",
        wait_seconds=35,
    )
    pid_match = re.search(r"process id '(\d+)'", message)
    if pid_match:
        pid = int(pid_match.group(1))
        assert pid > 0, "Process ID should be a positive integer"
    else:
        pytest.fail(f"Could not extract process ID from notification: {message}")
    try:
        os.kill(pid, 0)  # Signal 0 just tests if process exists
        process_exists = True
    except OSError:
        process_exists = False
    assert process_exists, f"Process with PID {pid} is not running"
    try:
        os.kill(pid, 9)  # Terminate the process
    except OSError as e:
        pytest.fail(f"Failed to kill QuPath process: {e}")

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])
