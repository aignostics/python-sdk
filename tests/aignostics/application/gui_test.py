"""Tests to verify the GUI functionality of the application module."""

import logging
import re
from asyncio import sleep
from pathlib import Path
from unittest.mock import patch

import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.application import Service
from aignostics.cli import cli
from aignostics.utils import get_logger, gui_register_pages

logger = get_logger(__name__)


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


async def _assert_notified(user: User, expected_notification: str, wait_seconds=5):
    """Check if the user receives a notification within the specified time."""
    for _ in range(wait_seconds):
        if user.notify.contains(expected_notification):
            break
        await sleep(1)
    assert user.notify.contains(expected_notification)


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
            "The Atlas H&E TME is an AI application designed to examine FFPE (formalin-fixed, paraffin-embedded) "
            "tissues stained with H&E (hematoxylin and eosin), delivering comprehensive insights into the "
            "tumor microenvironment.",
        ),
        (
            "test-app",
            "Test Application",
            "This is the test application with two algorithms: TissueQc and Tissue Segmentation.",
        ),
    ],
)
async def test_gui_home_to_application(
    user: User, application_id: str, application_name: str, expected_text: str, silent_logging: None
) -> None:
    """Test that the user sees the specific application page with expected content."""
    gui_register_pages()
    await user.open("/?noruns=true")
    await user.should_see(application_name, retries=100)
    user.find(marker=f"SIDEBAR_APPLICATION:{application_id}").click()
    await user.should_see(expected_text, retries=100)


async def test_gui_cli_to_run_cancel(user: User, runner: CliRunner, tmp_path: Path) -> None:
    """Test that the user sees the index page, and sees the intro."""
    gui_register_pages()

    # Submit run
    csv_content = "reference;source;checksum_crc32c;mpp;width;height;staining;tissue_type;disease;"
    csv_content += "file_size_human;file_upload_progress;platform_bucket_url\n"
    csv_content += ";;5onqtA==;0.26268186053789266;7447;7196;H&E;lung;lung;;;gs://bucket/test"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)
    result = runner.invoke(cli, ["application", "run", "submit", "he-tme:v0.45.0", str(csv_path)])
    assert result.exit_code == 0

    # Extract the run ID from the output
    run_id_match = re.search(r"Application run `([0-9a-f-]+)`", result.output)
    assert run_id_match is not None, f"Could not extract run ID from output: {result.output}"
    run_id = run_id_match.group(1)

    # Run shown in he GUI
    await user.open("/")
    await user.should_see("Applications")
    await user.should_see("Atlas H&E-TME")
    await user.should_see("Runs")
    await user.should_see("he-tme:v0.45.0", marker="SIDEBAR_RUN_ITEM:0", retries=1000)

    # Navigate to the extracted run ID
    await user.open(f"/application/run/{run_id}")
    await user.should_see("Run of he-tme:v0.45.0")
    await user.should_see("Application Version: he-tme:v0.45.0")
    user.should_see("Status: running")
    user.find(marker="BUTTON_APPLICATION_RUN_CANCEL").click()
    await _assert_notified(user, f"Canceling application run with id '{run_id}' ...")
    await _assert_notified(user, "Application run cancelled!")
    await user.should_see("Status: canceled_user")


async def test_gui_download_dataset_via_application_to_run_cancel(
    user: User, runner: CliRunner, tmp_path: Path, silent_logging: None
) -> None:
    """Test that the user can navigate to a run."""
    with patch("pathlib.Path.home", return_value=tmp_path):
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
        assert "Successfully downloaded" in result.stdout
        assert "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff" in result.stdout
        expected_file = Path(tmp_path) / "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
        assert expected_file.exists(), f"Expected file {expected_file} not found"
        assert expected_file.stat().st_size == 14681750

        # Open the GUI and navigate to Atlas H&E-TME application
        await user.open("/?noruns=true")
        await user.should_see("Applications")
        await user.should_see("Atlas H&E-TME")
        user.find(marker="SIDEBAR_APPLICATION:he-tme").click()
        await user.should_see("The Atlas H&E TME is an AI application designed to examine FFPE (")

        # Check the latest application version is shown and select it
        application_versions = Service().application_versions("he-tme")
        latest_application_version = application_versions[0]
        await user.should_see(latest_application_version.version)
        user.find(marker="BUTTON_APPLICATION_VERSION_NEXT").click()

        # Check the file picker opens and closes
        await user.should_see("Select a folder with whole slide images you want to analyze")
        user.find(marker="BUTTON_WSI_SELECT").click()
        await user.should_see("Ok")
        await user.should_see("Cancel")
        user.find(marker="BUTTON_FILEPICKER_CANCEL").click()
        await _assert_notified(user, "You did not make a selection")

        # Select the home directory and trigger metadata generation
        user.find(marker="BUTTON_PYTEST_HOME").click()
        await user.should_see(f"Selected folder {Path.home()!s} to analyze.")
        await _assert_notified(user, f"You chose directory {Path.home()!s}.")
        user.find(marker="BUTTON_WSI_NEXT").click()
        assert _assert_notified(user, "Found 1 slides for analysis")
        await sleep(10)

        # Generate remaining metadata, going to upload UI
        await user.should_see(
            "Check extracted and provide missing metadata.",
            retries=100,
        )
        user.find(marker="BUTTON_PYTEST_META").click()
        await _assert_notified(user, "Your metadata is now valid!")
        user.find(marker="BUTTON_METADATA_NEXT").click()
        await _assert_notified(user, "Prepared upload UI.")
        await user.should_see("1. Upload 1 slides you prepared to the Aignostics Platform.")

        # Trigger upload
        user.find(marker="BUTTON_SUBMISSION_UPLOAD").click()
        await _assert_notified(user, "Uploading whole slide images to Aignostics Platform ...")
        await _assert_notified(user, "Upload to Aignostics Platform completed.", wait_seconds=30)

        # Trigger submission
        user.find(marker="BUTTON_SUBMISSION_SUBMIT").click()
        await _assert_notified(user, "Submitting application run ...")
        await _assert_notified(user, "Application run submitted with id", wait_seconds=10)

        # Check user is redirected to the run page and run is running
        await user.should_see(f"Run of he-tme:v{latest_application_version.version}")
        await user.should_see("Status: running")

        # Check user can cancel run
        user.find(marker="BUTTON_APPLICATION_RUN_CANCEL").click()
        await _assert_notified(user, "Canceling application run with id")
        await _assert_notified(user, "Application run cancelled!")
        await user.should_see("Status: canceled_user")
