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
from aignostics_sdk.utils import __project_name__
from tests.conftest import assert_notified, normalize_output, print_directory_structure
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    SPOT_0_EXPECTED_CELLS_CLASSIFIED,
    SPOT_0_EXPECTED_RESULT_FILES,
    SPOT_0_FILENAME,
    SPOT_0_FILESIZE,
    SPOT_0_GS_URL,
    SPOT_0_HEIGHT,
    SPOT_0_WIDTH,
)

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
async def test_gui_qupath_install_only(
    user: User, runner: CliRunner, silent_logging: None, qupath_save_restore: None, record_property
) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    record_property("tested-item-id", "TC-QUPATH-01, SPEC-GUI-SERVICE")

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


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.skipif(
    platform.system() == "Linux" and platform.machine() in {"arm64", "aarch64"},
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.timeout(timeout=60 * 10)
@pytest.mark.sequential
async def test_gui_qupath_install_and_launch(  # noqa: PLR0913, PLR0917
    user: User, runner: CliRunner, silent_logging: None, qupath_teardown, qupath_save_restore: None, record_property
) -> None:
    """Test that the user can install and launch QuPath via the GUI."""
    record_property("tested-item-id", "TC-QUPATH-01, SPEC-GUI-SERVICE")

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
    except Exception as e:
        pytest.fail(f"Failed to kill QuPath process: {e}")


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.skipif(
    (platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"}),
    reason="QuPath is not supported on ARM64 Linux",
)
@pytest.mark.timeout(timeout=60 * 15)
@pytest.mark.sequential
async def test_gui_run_qupath_install_to_inspect(  # noqa: C901, PLR0912, PLR0913, PLR0914, PLR0915, PLR0917
    user: User,
    runner: CliRunner,
    tmp_path: Path,
    silent_logging: None,
    qupath_teardown: None,
    qupath_save_restore: None,
    record_property,
) -> None:
    """Test installing QuPath, downloading run results, creating QuPath project from it, and inspecting results."""
    record_property("tested-item-id", "TC-QUPATH-01, SPEC-GUI-SERVICE")

    # Find run
    runs = Service().application_runs(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        external_id=SPOT_0_GS_URL,
        tags=["scheduled"],
        has_output=True,
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

        # Check for directory layout as expected
        run_dir = tmp_path / run.run_id
        assert run_dir.is_dir(), f"Expected run directory {run_dir} not found"

        subdirs = [d for d in run_dir.iterdir() if d.is_dir()]
        assert len(subdirs) == 3, f"Expected three subdirectories in {run_dir}, but found {len(subdirs)}"

        input_dir = run_dir / "input"
        assert input_dir.is_dir(), f"Expected input directory {input_dir} not found"

        results_dir = run_dir / SPOT_0_FILENAME.replace(".tiff", "")
        assert results_dir.is_dir(), f"Expected run results directory {results_dir} not found"

        qupath_dir = run_dir / "qupath"
        assert qupath_dir.is_dir(), f"Expected QuPath directory {qupath_dir} not found"

        # Check for input file having been downloaded
        input_file = input_dir / SPOT_0_FILENAME
        assert input_file.exists(), f"Expected input file {input_file} not found"
        assert input_file.stat().st_size == SPOT_0_FILESIZE, (
            f"Expected input file size {SPOT_0_FILESIZE}, but got {input_file.stat().st_size}"
        )

        # Check for files in the results directory
        files_in_results_dir = list(results_dir.glob("*"))
        assert len(files_in_results_dir) == 9, (
            f"Expected 9 files in {results_dir}, but found {len(files_in_results_dir)}: "
            f"{[f.name for f in files_in_results_dir]}"
        )

        print(f"Found files in {results_dir}:")
        for filename, expected_size, tolerance_percent in SPOT_0_EXPECTED_RESULT_FILES:
            file_path = results_dir / filename
            if file_path.exists():
                actual_size = file_path.stat().st_size
                print(f"  {filename}: {actual_size} bytes (expected: {expected_size} ±{tolerance_percent}%)")
            else:
                print(f"  {filename}: NOT FOUND")
        for filename, expected_size, tolerance_percent in SPOT_0_EXPECTED_RESULT_FILES:
            file_path = results_dir / filename
            assert file_path.exists(), f"Expected file {filename} not found"
            actual_size = file_path.stat().st_size
            min_size = expected_size * (100 - tolerance_percent) // 100
            max_size = expected_size * (100 + tolerance_percent) // 100
            assert min_size <= actual_size <= max_size, (
                f"File size for {filename} ({actual_size} bytes) is outside allowed range "
                f"({min_size} to {max_size} bytes, ±{tolerance_percent}% of {expected_size})"
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
        except Exception as e:
            pytest.fail(f"Failed to kill QuPath process: {e}")

        # Step 7: Inspect QuPath results
        result = runner.invoke(cli, ["qupath", "inspect", str(qupath_dir)])
        output = normalize_output(result.output, strip_ansi=True)
        print(repr(output))

        # Check for (1) spot added to QuPath project, (2) heatmaps added, (3) spot annotated
        try:
            project_info = json.loads(output)
            spot_found = False
            spot_width = None
            spot_height = None
            qc_segmentation_map_found = False
            tissue_segmentation_map_found = False
            for image in project_info["images"]:
                if image.get("name") == SPOT_0_FILENAME:
                    spot_found = True
                    spot_width = image.get("width")
                    spot_height = image.get("height")
                    hierarchy = image.get("hierarchy", {})
                    spot_annotations = hierarchy.get("total", 0)
                if image.get("name") == "tissue_qc_segmentation_map_image.tiff":
                    qc_segmentation_map_found = True
                if image.get("name") == "tissue_segmentation_segmentation_map_image.tiff":
                    tissue_segmentation_map_found = True
            assert spot_found, f"Spot '{SPOT_0_FILENAME}' not found in QuPath project"
            assert spot_width == SPOT_0_WIDTH, f"Expected width of spot {SPOT_0_WIDTH}, but got {spot_width}"
            assert spot_height == SPOT_0_HEIGHT, f"Expected height of spot {SPOT_0_HEIGHT}, but got {spot_height}"
            assert qc_segmentation_map_found, "QC segmentation map image not found in QuPath project"
            assert tissue_segmentation_map_found, "Tissue segmentation map image not found in QuPath project"
            assert abs(spot_annotations - SPOT_0_EXPECTED_CELLS_CLASSIFIED[0]) <= (
                SPOT_0_EXPECTED_CELLS_CLASSIFIED[0] * SPOT_0_EXPECTED_CELLS_CLASSIFIED[1] // 100
            ), (
                f"Expected approximately {SPOT_0_EXPECTED_CELLS_CLASSIFIED[0]} "
                f"({SPOT_0_EXPECTED_CELLS_CLASSIFIED[1]}% tolerance) annotations in the QuPath results, "
                f"but found {spot_annotations}"
            )
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse QuPath inspect output as JSON: {e}\nOutput: {output!r}\n")

        # Validate the inspect command exited successfully
        assert result.exit_code == 0, f"QuPath inspect command failed with exit code {result.exit_code}"
