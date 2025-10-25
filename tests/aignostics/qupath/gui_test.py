"""Tests to verify the GUI functionality of the QuPath."""

import json
import platform
import re
from asyncio import sleep
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import platformdirs
import psutil
import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.application import Service
from aignostics.cli import cli
from aignostics.qupath import QUPATH_LAUNCH_MAX_WAIT_TIME, QUPATH_VERSION
from aignostics.utils import __project_name__
from tests.conftest import assert_notified, normalize_output, print_directory_structure
from tests.contants_test import HETA_APPLICATION_ID, HETA_APPLICATION_VERSION, HETA_SINGLE_SPOT_GS_URL

if TYPE_CHECKING:
    from nicegui import ui

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
async def test_gui_qupath_install_only(user: User, runner: CliRunner, silent_logging: None) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert result.exit_code in {0, 2}, f"Uninstall command failed with exit code {result.exit_code}"
    was_installed = not result.exit_code

    # Step 1: Check we are on the QuPath page
    await user.open("/qupath")
    await user.should_see("QuPath Extension")

    # Step 2: Check we indicate QuPath is not installed
    await user.should_see("Install QuPath to enable visualizing your Whole Slide Image and application results")

    # Step 3: Install QuPath
    await user.should_see(marker="BUTTON_QUPATH_INSTALL")
    user.find("BUTTON_QUPATH_INSTALL").click()
    app_dir = platformdirs.user_data_dir(__project_name__)
    await assert_notified(
        user,
        f"QuPath installed successfully to '{app_dir}",
        wait_seconds=60 * 2,
    )

    # Step 4: Check we indicate QuPath is installed
    await sleep(5)
    await user.should_see(f"QuPath {QUPATH_VERSION} is installed and ready to execute.")
    await user.should_see(marker="BUTTON_QUPATH_LAUNCH")

    if not was_installed:
        result = runner.invoke(cli, ["qupath", "uninstall"])


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"arm64", "aarch64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
async def test_gui_qupath_install_and_launch(
    user: User, runner: CliRunner, silent_logging: None, qupath_teardown
) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert result.exit_code in {0, 2}, f"Uninstall command failed with exit code {result.exit_code}"
    was_installed = not result.exit_code

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
    app_dir = platformdirs.user_data_dir(__project_name__)
    await assert_notified(
        user,
        f"QuPath installed successfully to '{app_dir}",
        wait_seconds=60 * 8,
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


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.skipif(
    (platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"}) or platform.system() == "Windows",
    reason="QuPath is not supported on ARM64 Linux; Windows support is not implemented yet",
)
@pytest.mark.timeout(timeout=60 * 15)
@pytest.mark.sequential
async def test_gui_run_qupath_install_to_inspect(  # noqa: PLR0914, PLR0915
    user: User, runner: CliRunner, tmp_path: Path, silent_logging: None, qupath_teardown: None
) -> None:
    """Test installing QuPath, downloading run results, creating QuPath project from it, and inspecting results."""
    # Find run
    runs = Service().application_runs(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        external_id=HETA_SINGLE_SPOT_GS_URL,
        has_output=False,
        limit=1,
    )
    if not runs:
        message = f"No matching runs found for application {HETA_APPLICATION_ID} ({HETA_APPLICATION_VERSION}). "
        message += "This test requires the scheduled test test_application_runs_heta_version passing first."
        pytest.skip(message)

    run_id = runs[0].run_id

    # Explore run
    run = Service().application_run(run_id).details()
    print(
        f"Found existing run: {run.run_id}\n"
        f"application: {run.application_id} ({run.version_number})\n"
        f"status: {run.state}, output: {run.output}\n"
        f"submitted at: {run.submitted_at}, terminated at: {run.terminated_at}\n"
        f"statistics: {run.statistics!r}\n",
        f"custom_metadata: {run.custom_metadata!r}\n",
    )

    # Explore results
    results = list(Service().application_run(run_id).results())
    assert results, f"No results found for run {run_id}"
    for item in results:
        print(
            f"Found item: {item.item_id}, status: {item.state}, output: {item.output}, "
            f"external_id: {item.external_id}\n"
            f"custom_metadata: {item.custom_metadata!r}\n",
        )

    with patch(
        "aignostics.application._gui._page_application_run_describe.get_user_data_directory", return_value=tmp_path
    ):
        # Step 1: (Re)Install QuPath
        result = runner.invoke(cli, ["qupath", "uninstall"])
        assert result.exit_code in {0, 2}, f"Uninstall command failed with exit code {result.exit_code}"
        was_installed = not result.exit_code

        result = runner.invoke(cli, ["qupath", "install"])
        output = normalize_output(result.output, strip_ansi=True)
        assert f"QuPath v{QUPATH_VERSION} installed successfully" in output, (
            f"Expected 'QuPath v{QUPATH_VERSION} installed successfully' in output.\nOutput: {output}"
        )
        assert result.exit_code == 0

        # Step 2: Go to latest completed run via GUI
        await user.open(f"/application/run/{run.run_id}")
        await user.should_see(f"Run {run.run_id}")
        await user.should_see(f"Run of {HETA_APPLICATION_ID} ({HETA_APPLICATION_VERSION})")

        # Step 3: Open Result Download dialog
        await user.should_see(marker="BUTTON_OPEN_QUPATH", retries=100)
        user.find(marker="BUTTON_OPEN_QUPATH").click()

        # Step 4: Select Data destination
        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA")
        download_destination_data_button: ui.button = user.find(
            marker="BUTTON_DOWNLOAD_DESTINATION_DATA"
        ).elements.pop()
        assert download_destination_data_button.enabled, "Download destination button should be enabled"
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()
        await assert_notified(user, "Using Launchpad results directory", 30)

        # Step 5: Trigger Download
        await user.should_see(marker="DIALOG_BUTTON_DOWNLOAD_RUN")
        download_run_button: ui.button = user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").elements.pop()
        assert download_run_button.enabled, "Download button should be enabled before downloading"
        user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").click()
        await assert_notified(user, "Downloading ...", 30)

        # Step 6: Check download completes, QuPath project created, and QuPath launched
        await assert_notified(user, "Download and QuPath project creation completed.", 60 * 5)
        print_directory_structure(tmp_path, "execute")
        run_out_dir = tmp_path / run.run_id
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

        # Step 7: Inspect QuPath results
        result = runner.invoke(cli, ["qupath", "inspect", str(run_out_dir / "qupath")])
        output = normalize_output(result.output, strip_ansi=True)
        print(repr(output))
        assert result.exit_code == 0, f"QuPath inspect command failed with exit code {result.exit_code}"

        try:
            project_info = json.loads(output)
            annotations_total = 0
            for image in project_info["images"]:
                hierarchy = image.get("hierarchy", {})
                total = hierarchy.get("total", 0)
                if total > 0:
                    annotations_total += total
            # TODO(Helmut): More detailed checks on the annotations when improved above
            assert annotations_total >= 0, "Expected at least 0 annotations in the QuPath results"
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse QuPath inspect output as JSON: {e}\nOutput: {output!r}\n")

        if not was_installed:
            result = runner.invoke(cli, ["qupath", "uninstall"])
