"""Tests to verify the GUI functionality of the QuPath."""

import platform
import re
from asyncio import sleep

import appdirs
import psutil
import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.gui import HEALTH_UPDATE_INTERVAL
from aignostics.qupath import QUPATH_LAUNCH_MAX_WAIT_TIME, QUPATH_VERSION
from aignostics.utils import __project_name__, gui_register_pages
from tests.conftest import assert_notified

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"


@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.sequential
async def test_gui_qupath_install(user: User, runner: CliRunner, silent_logging: None) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    gui_register_pages()

    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert result.exit_code in {0, 2}, f"Uninstall command failed with exit code {result.exit_code}"
    was_installed = not result.exit_code

    # Step 1: Check we are on the QuPath page
    await user.open("/qupath")
    await user.should_see("QuPath Extension")

    # Step 2: Check we indicate QuPath is not installed
    await sleep(HEALTH_UPDATE_INTERVAL * 2)  # Health UI updated in background
    await user.should_see("Launchpad is unhealthy")
    await user.should_see("Install QuPath to enable visualizing your Whole Slide Image and application results")

    # Step 3: Install QuPath
    await user.should_see(marker="BUTTON_QUPATH_INSTALL")
    user.find("BUTTON_QUPATH_INSTALL").click()
    app_dir = appdirs.user_data_dir(__project_name__)
    await assert_notified(
        user,
        f"QuPath installed successfully to '{app_dir}",
        wait_seconds=35,
    )

    # Step 4: Check we indicate QuPath is installed
    await sleep(HEALTH_UPDATE_INTERVAL * 2)  # Health UI updated in background
    await user.should_see(f"QuPath {QUPATH_VERSION} is installed and ready to execute.")
    await user.should_see("Launchpad is healthy")
    await user.should_see(marker="BUTTON_QUPATH_LAUNCH")

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])


@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.long_running
async def test_gui_qupath_install_and_launch(
    user: User, runner: CliRunner, silent_logging: None, qupath_teardown
) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert result.exit_code in {0, 2}, f"Uninstall command failed with exit code {result.exit_code}"
    was_installed = not result.exit_code

    gui_register_pages()

    # Step 1: Check we are on the QuPath page
    await user.open("/qupath")
    await user.should_see("QuPath Extension")

    # Step 2: Check we indicate QuPath is not installed
    await user.should_see(
        "Install QuPath to enable visualizing your Whole Slide Image and application results",
        retries=QUPATH_LAUNCH_MAX_WAIT_TIME * 20,
    )

    # Step 3: Install QuPath
    await user.should_see(marker="BUTTON_QUPATH_INSTALL")
    user.find("BUTTON_QUPATH_INSTALL").click()
    app_dir = appdirs.user_data_dir(__project_name__)
    await assert_notified(
        user,
        f"QuPath installed successfully to '{app_dir}",
        wait_seconds=35,
    )

    # Step 4: Check we indicate QuPath is installed
    await user.should_see(
        f"QuPath {QUPATH_VERSION} is installed and ready to execute.", retries=QUPATH_LAUNCH_MAX_WAIT_TIME * 20
    )

    # Step 5: Check we can launch QuPath
    await user.should_see(marker="BUTTON_QUPATH_LAUNCH")
    user.find("BUTTON_QUPATH_LAUNCH").click()
    message = await assert_notified(
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
        psutil.Process(pid).kill()
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Failed to kill QuPath process: {e}")

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])
