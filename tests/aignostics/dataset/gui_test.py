"""Tests to verify the GUI functionality of the dataset module."""

from pathlib import Path
from unittest.mock import patch

import pytest
from nicegui.testing import User

from tests.conftest import assert_notified, print_directory_structure

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"
IDC_DOWNLOAD_MAX_DURATION = 60


@pytest.mark.integration
async def test_gui_idc_shows(user: User) -> None:
    """Test that the user sees the dataset page."""
    await user.open("/dataset/idc")
    await user.should_see("Explore Portal")


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.flaky(retries=1, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 5)
async def test_gui_idc_downloads(user: User, tmp_path: Path, silent_logging: bool, record_property) -> None:
    """Test that the user can download a dataset to a temporary directory."""
    record_property("tested-item-id", "TC-DATASET-GUI-01, SPEC-GUI-SERVICE")
    # Mock get_user_data_directory to return the tmpdir for this test
    with patch("aignostics.dataset._gui.get_user_data_directory", return_value=tmp_path):
        await user.open("/dataset/idc")

        await user.should_see(marker="BUTTON_EXAMPLE_DATASET")
        user.find(marker="BUTTON_EXAMPLE_DATASET").click()
        await user.should_see("1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0")

        await user.should_see(marker="SOURCE_INPUT")
        user.find(marker="SOURCE_INPUT").clear()
        user.find(marker="SOURCE_INPUT").type("1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0")
        await user.should_see("1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0")

        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION")
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION").click()

        await user.should_see(marker="BUTTON_FILEPICKER_CANCEL")
        user.find(marker="BUTTON_FILEPICKER_CANCEL").click()
        await user.should_see(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)

        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA")
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()
        await user.should_not_see(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)

        await user.should_see(marker="BUTTON_DOWNLOAD")
        user.find(marker="BUTTON_DOWNLOAD").click()
        await assert_notified(user, "Downloading", wait_seconds=5)

        await assert_notified(user, "Download completed", wait_seconds=120)

        print_directory_structure(tmp_path)
        expected_file = (
            tmp_path
            / "tcga_luad"
            / "TCGA-91-6830"
            / "2.25.5646130214350101265514421836879989792"
            / "SM_1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.2.0"
            / "975bc2fa-d403-4c4c-affa-0fbb08475651.dcm"
        )

        assert expected_file.exists(), f"Expected file {expected_file} does not exist."
        actual_size = expected_file.stat().st_size
        expected_size = 1369290
        assert expected_size == expected_file.stat().st_size, (
            f"File size {actual_size} doesn't match expected '{expected_size}' bytes.\n"
        )


async def _gui_idc_download_fails_with_invalid_inputs(  # noqa: PLR0913, PLR0917
    user: User, tmpdir, source_input: str, expected_notification: str, silent_logging: None, record_property
) -> None:
    """Test that the download fails with appropriate notification."""
    record_property("tested-item-id", "TC-DATASET-GUI-01, SPEC-GUI-SERVICE")

    with patch("aignostics.dataset._gui.get_user_data_directory", return_value=Path(tmpdir)):
        await user.open("/dataset/idc")
        await user.should_see(marker="SOURCE_INPUT")
        user.find(marker="SOURCE_INPUT").clear()
        user.find(marker="SOURCE_INPUT").type(source_input)

        await user.should_see(marker="BUTTON_DOWNLOAD_DESTINATION_DATA")
        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()
        await user.should_not_see(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)

        await user.should_see(marker="BUTTON_DOWNLOAD")
        user.find(marker="BUTTON_DOWNLOAD").click()

        await assert_notified(user, expected_notification, wait_seconds=60)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("source_input", "expected_notification"),
    [
        (" ", "Download failed: No IDs provided."),
    ],
)
@pytest.mark.timeout(timeout=60)
async def test_gui_idc_download_fails_with_no_inputs(  # noqa: PLR0913, PLR0917
    user: User, tmpdir, source_input: str, expected_notification: str, silent_logging: None, record_property
) -> None:
    """Test that the download fails with appropriate notification when no IDs are provided."""
    record_property("tested-item-id", "TC-DATASET-GUI-01, SPEC-GUI-SERVICE")

    await _gui_idc_download_fails_with_invalid_inputs(
        user, tmpdir, source_input, expected_notification, silent_logging, record_property
    )


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5, only_on=[AssertionError])
@pytest.mark.timeout(timeout=60 * 2)
@pytest.mark.parametrize(
    ("source_input", "expected_notification"),
    [
        (
            "4711",
            "Download failed: None of the values passed matched any of the identifiers: "
            "collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID.",
        ),
    ],
)
async def test_gui_idc_download_fails_with_invalid_inputs(  # noqa: PLR0913, PLR0917
    user: User, tmpdir, source_input: str, expected_notification: str, silent_logging: None, record_property
) -> None:
    """Test that the download fails with appropriate notification when invalid IDs are provided."""
    record_property("tested-item-id", "TC-DATASET-GUI-01, SPEC-GUI-SERVICE")

    await _gui_idc_download_fails_with_invalid_inputs(
        user, tmpdir, source_input, expected_notification, silent_logging, record_property
    )
