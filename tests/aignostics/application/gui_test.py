"""Tests to verify the GUI functionality of the application module."""

import re
import tempfile
from asyncio import sleep
from pathlib import Path
from unittest.mock import patch

import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.application import Service
from aignostics.cli import cli
from aignostics.platform import ApplicationRunStatus
from aignostics.utils import get_logger, gui_register_pages
from tests.conftest import assert_notified, normalize_output, print_directory_structure

logger = get_logger(__name__)

HETA_APPLICATION_VERSION_ID = "he-tme:v0.51.0"
HETA_APPLICATION_ID = "he-tme"


async def test_gui_index(user: User) -> None:
    """Test that the user sees the index page, and sees the intro."""
    gui_register_pages()
    await user.open("/")
    await user.should_see("Atlas H&E-TME")
    await user.should_see("Download Datasets")


@pytest.mark.parametrize(
    ("application_id", "application_name", "expected_text"),
    [
        (
            "he-tme",
            "Atlas H&E-TME",
            "The Atlas H&E TME is an AI application",
        ),
        (
            "test-app",
            "Test Application",
            "This is the test application with two algorithms",
        ),
    ],
)
async def test_gui_home_to_application(
    user: User, application_id: str, application_name: str, expected_text: str, silent_logging: None
) -> None:
    """Test that the user sees the specific application page with expected content."""
    gui_register_pages()
    await user.open("/")
    await user.should_see(application_name, retries=100)
    user.find(marker=f"SIDEBAR_APPLICATION:{application_id}").click()
    await user.should_see(expected_text, retries=100)


@pytest.mark.flaky(retries=1, delay=5, only_on=[AssertionError])
async def test_gui_cli_to_run_cancel(user: User, runner: CliRunner, silent_logging) -> None:
    """Test that the user sees the index page, and sees the intro."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gui_register_pages()

        tmp_path = Path(tmpdir)

        latest_version = Service().application_version_latest(Service().application(HETA_APPLICATION_ID))
        latest_version_id = latest_version.application_version_id

        # Submit run
        csv_content = (
            "reference;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
        )
        csv_content += "platform_bucket_url\n"
        csv_content += ";5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test"
        csv_path = tmp_path / "dummy.csv"
        csv_path.write_text(csv_content)
        result = runner.invoke(cli, ["application", "run", "submit", HETA_APPLICATION_ID, str(csv_path)])
        assert result.exit_code == 0

        # Extract the run ID from the output
        output = normalize_output(result.output)
        run_id_match = re.search(r"Submitted run with id '([0-9a-f-]+)' for '", output)
        assert run_id_match is not None, f"Could not extract run ID from output: {output}"
        run_id = run_id_match.group(1)

        # Run shown in he GUI
        await user.open("/")
        await user.should_see("Applications")
        await user.should_see("Atlas H&E-TME")
        await user.should_see("Runs")
        await user.should_see(HETA_APPLICATION_VERSION_ID, marker="SIDEBAR_RUN_ITEM:0", retries=1000)

        # Navigate to the extracted run ID
        await user.open(f"/application/run/{run_id}")
        await user.should_see(f"Run of {latest_version_id}")
        await user.should_see(f"Application Version: {latest_version_id}")
        await user.should_see("status RUNNING")
        await user.should_see(marker="BUTTON_APPLICATION_RUN_CANCEL")
        user.find(marker="BUTTON_APPLICATION_RUN_CANCEL").click()
        await assert_notified(user, f"Canceling application run with id '{run_id}' ...")
        await assert_notified(user, "Application run cancelled!")

        # Check user sees refreshed run page and run is cancelled
        await user.should_see("status CANCELED_USER", retries=200)


@pytest.mark.long_running
async def test_gui_download_dataset_via_application_to_run_cancel(  # noqa: PLR0915
    user: User, runner: CliRunner, tmp_path: Path, silent_logging: None
) -> None:
    """Test that the user can download a dataset via the application page and cancel the run."""
    with patch("aignostics.application._gui._page_application_describe.Path.home", return_value=tmp_path):
        gui_register_pages()

        # Download example wsi
        result = runner.invoke(
            cli,
            [
                "dataset",
                "aignostics",
                "download",
                "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Successfully downloaded" in normalize_output(result.stdout)
        assert "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff" in normalize_output(result.stdout)
        expected_file = Path(tmp_path) / "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
        assert expected_file.exists(), f"Expected file {expected_file} not found"
        assert expected_file.stat().st_size == 14681750

        # Open the GUI and navigate to Atlas H&E-TME application
        await user.open("/")
        await user.should_see("Applications")
        await user.should_see("Atlas H&E-TME")
        await user.should_see(marker="SIDEBAR_APPLICATION:he-tme")
        user.find(marker="SIDEBAR_APPLICATION:he-tme").click()
        await user.should_see("Atlas H&E-TME")
        await user.should_see("The Atlas", retries=100)
        await user.should_see("The Atlas H&E TME is an AI application")

        # Check the latest application version is shown and select it
        application_versions = Service().application_versions("he-tme")
        latest_application_version = application_versions[0]
        await user.should_see(latest_application_version.version)
        user.find(marker="BUTTON_APPLICATION_VERSION_NEXT").click()

        # Check the file picker opens and closes
        await user.should_see("Select the folder with the whole slide images you want to analyze then click Next")
        user.find(marker="BUTTON_WSI_SELECT_DATA").click()
        await user.should_see("Ok")
        await user.should_see("Cancel")
        user.find(marker="BUTTON_WSI_SELECT_CUSTOM").click()
        await user.should_see("Ok")
        await user.should_see("Cancel")
        user.find(marker="BUTTON_FILEPICKER_CANCEL").click()
        await assert_notified(user, "You did not make a selection")

        # Select the home directory and trigger metadata generation
        user.find(marker="BUTTON_PYTEST_HOME").click()
        await user.should_see(f"Selected folder {tmp_path!s} to analyze.")
        await assert_notified(user, f"You chose directory {tmp_path!s}.")
        user.find(marker="BUTTON_WSI_NEXT").click()
        await assert_notified(user, "Found 1 slides for analysis", wait_seconds=20)
        await sleep(10)

        # Generate remaining metadata, going to upload UI
        await user.should_see(
            "The Launchpad has found all compatible slide files in your selected folder.",
            retries=100,
        )
        user.find(marker="BUTTON_PYTEST_META").click()
        await assert_notified(user, "Your metadata is now valid! Feel free to continue to the next step.")
        user.find(marker="BUTTON_METADATA_NEXT").click()
        await assert_notified(user, "Prepared upload UI.")
        print(user.current_layout)
        await user.should_see("Upload and submit your 1 slide(s) for analysis.", retries=100)

        # Trigger upload and submission
        await user.should_see(marker="BUTTON_SUBMISSION_UPLOAD")
        user.find(marker="BUTTON_SUBMISSION_UPLOAD").click()
        await assert_notified(user, "Uploading whole slide images to Aignostics Platform ...")
        await assert_notified(user, "Upload to Aignostics Platform completed.", wait_seconds=30)
        await assert_notified(user, "Submitting application run ...")
        await assert_notified(user, "Application run submitted with id", wait_seconds=10)

        # Check user is redirected to the run page and run is running
        await user.should_see(f"Run of he-tme:v{latest_application_version.version}", retries=200)
        await user.should_see("status RUNNING")

        # Check user can cancel run
        await user.should_see(marker="BUTTON_APPLICATION_RUN_CANCEL")
        user.find(marker="BUTTON_APPLICATION_RUN_CANCEL").click()
        await assert_notified(user, "Canceling application run with id")
        await assert_notified(user, "Application run cancelled!")

        # Check user sees refreshed run page and run is cancelled
        await user.should_see("status CANCELED_USER", retries=200)


@pytest.mark.sequential
async def test_gui_run_download(user: User, runner: CliRunner, tmp_path: Path, silent_logging: None) -> None:
    """Test that the user can download a run result via the GUI."""
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
        await user.should_see(marker="BUTTON_DOWNLOAD_RUN")
        user.find(marker="BUTTON_DOWNLOAD_RUN").click()

        # Step 3: Select Data
        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA")
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()

        # Step 3: Trigger Download
        await user.should_see(marker="DIALOG_BUTTON_DOWNLOAD_RUN")
        user.find(marker="DIALOG_BUTTON_DOWNLOAD_RUN").click()

        # Check: Download completed
        await assert_notified(user, "Download completed.", 60)
        print_directory_structure(tmp_path, "execute")
        run_out_dir = tmp_path / run.application_run_id
        assert run_out_dir.is_dir(), f"Expected run directory {run_out_dir} not found"
        # Find any subdirectory in the run_out_dir
        subdirs = [d for d in run_out_dir.iterdir() if d.is_dir()]
        assert len(subdirs) > 0, f"Expected at least one subdirectory in {run_out_dir}, but found none"

        # Take the first subdirectory found (item_out_dir)
        item_out_dir = subdirs[0]
        print(f"Found subdirectory: {item_out_dir.name}")

        # Check for files in the item directory
        files_in_item_dir = list(item_out_dir.glob("*"))
        assert len(files_in_item_dir) == 9, (
            f"Expected 9 files in {item_out_dir}, but found {len(files_in_item_dir)}: "
            f"{[f.name for f in files_in_item_dir]}"
        )
