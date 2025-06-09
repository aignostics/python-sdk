"""Tests to verify the GUI functionality of the QuPath."""

import json
import platform
import re
from asyncio import sleep
from pathlib import Path
from unittest.mock import patch

import appdirs
import psutil
import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.application import Service
from aignostics.cli import cli
from aignostics.gui import HEALTH_UPDATE_INTERVAL
from aignostics.platform import ApplicationRunStatus
from aignostics.qupath import QUPATH_LAUNCH_MAX_WAIT_TIME, QUPATH_VERSION
from aignostics.utils import __project_name__, gui_register_pages
from tests.conftest import assert_notified, normalize_output, print_directory_structure

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"
HETA_APPLICATION_ID = "he-tme"


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
    notification = await assert_notified(
        user,
        "QuPath launched successfully with process id",
        wait_seconds=35,
    )
    pid_match = re.search(r"process id '(\d+)'", notification)
    if pid_match:
        pid = int(pid_match.group(1))
        assert psutil.Process(pid).is_running(), "QuPath process is not running"
    else:
        pytest.fail(f"Could not extract process ID from notification: {notification}")
    try:
        psutil.Process(pid).kill()
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Failed to kill QuPath process: {e}")

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])


@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.sequential
async def test_gui_run_qupath_install_to_inspect(  # noqa: PLR0914, PLR0915
    user: User, runner: CliRunner, tmp_path: Path, silent_logging: None
) -> None:
    """Test that the user can open QuPath on a run."""
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert result.exit_code in {0, 2}, f"Uninstall command failed with exit code {result.exit_code}"
    was_installed = not result.exit_code

    result = runner.invoke(cli, ["qupath", "install"])
    assert f"QuPath v{QUPATH_VERSION} installed successfully" in normalize_output(result.output)
    assert result.exit_code == 0

    with patch(
        "aignostics.application._gui._page_application_run_describe.get_user_data_directory", return_value=tmp_path
    ):
        gui_register_pages()

        latest_version = Service().application_version_latest(Service().application(HETA_APPLICATION_ID))
        latest_version_id = latest_version.application_version_id
        runs = Service().application_runs(limit=1, status=ApplicationRunStatus.COMPLETED)

        if not runs:
            pytest.fail("No completed runs found, please run the test first.")
        # Find a completed run with the latest application version ID
        run = None
        for potential_run in runs:
            if potential_run.application_version_id == latest_version_id:
                run = potential_run
                break
        if not run:
            pytest.skip(f"No completed runs found with version {latest_version_id}")

        # Step 1: Go to latest completed run
        print(f"Found existing run: {run.application_run_id}, status: {run.status}")
        await user.open(f"/application/run/{run.application_run_id}")
        await user.should_see(f"Run {run.application_run_id}")
        await user.should_see(f"Run of {latest_version_id}")

        # Step 2: Open Result Download dialog
        await user.should_see(marker="BUTTON_OPEN_QUPATH")
        user.find(marker="BUTTON_OPEN_QUPATH").click()

        # Step 3: Select Data
        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA")
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()

        # Step 3: Trigger Download
        await user.should_see(marker="DIALOG_BUTTON_DOWNLOAD_RUN")
        user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").click()

        # Check: Download completed
        await assert_notified(user, "Download and QuPath project creation completed.", 60)
        print_directory_structure(tmp_path, "execute")
        run_out_dir = tmp_path / run.application_run_id
        assert run_out_dir.is_dir(), f"Expected run directory {run_out_dir} not found"
        # Find any subdirectory in the run_out_dir that is not qupath
        subdirs = [d for d in run_out_dir.iterdir() if d.is_dir() and d.name != "qupath"]
        assert len(subdirs) > 0, f"Expected at least one non-qupath subdirectory in {run_out_dir}, but found none"

        # Take the first subdirectory found (item_out_dir)
        item_out_dir = subdirs[0]
        print(f"Found subdirectory: {item_out_dir.name}")

        # Check for files in the item directory
        files_in_item_dir = list(item_out_dir.glob("*"))
        assert len(files_in_item_dir) == 9, (
            f"Expected 9 files in {item_out_dir}, but found {len(files_in_item_dir)}: "
            f"{[f.name for f in files_in_item_dir]}"
        )

        # Check QuPath is running
        notification = await assert_notified(user, "QuPath opened successfully", 30)
        pid_match = re.search(r"process id '(\d+)'", notification)
        if pid_match:
            pid = int(pid_match.group(1))
            assert psutil.Process(pid).is_running(), "QuPath process is not running"
        else:
            pytest.fail(f"Could not extract process ID from notification: {notification}")
        try:
            psutil.Process(pid).kill()
        except Exception as e:  # noqa: BLE001
            pytest.fail(f"Failed to kill QuPath process: {e}")

        # Step 5: Inspect QuPath results
        result = runner.invoke(cli, ["qupath", "inspect", str(run_out_dir / "qupath")])
        assert result.exit_code == 0

        # Check images have been annotated in the QuPath project created
        project_info = json.loads(result.output)
        annotations_total = 0
        for image in project_info["images"]:
            hierarchy = image.get("hierarchy", {})
            total = hierarchy.get("total", 0)
            if total > 0:
                annotations_total += total
        assert annotations_total > 1000, "Expected at least 1001 annotations in the QuPath results"

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])
