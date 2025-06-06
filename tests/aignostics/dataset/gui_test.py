"""Tests to verify the GUI functionality of the dataset module."""

from asyncio import sleep
from pathlib import Path
from unittest.mock import patch

import pytest
from nicegui.testing import User

from aignostics.utils import gui_register_pages

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"


async def _assert_notified(user: User, expected_notification: str, wait_seconds=5) -> str:
    """Check if the user receives a notification within the specified time."""
    for _ in range(wait_seconds):
        matching_messages = [msg for msg in user.notify.messages if expected_notification in msg]
        if matching_messages:
            return matching_messages[0]
        await sleep(1)
    pytest.fail(f"No notification containing '{expected_notification}' was found within {wait_seconds} seconds")


async def test_gui_idc_shows(user: User) -> None:
    """Test that the user sees the dataset page."""
    gui_register_pages()
    await user.open("/dataset/idc")
    await user.should_see("Explore Portal")


async def test_gui_idc_downloads(user: User, tmpdir) -> None:
    """Test that the user can download a dataset to a temporary directory."""
    # Mock get_user_data_directory to return the tmpdir for this test
    with patch("aignostics.system.Service.get_user_data_directory", return_value=Path(tmpdir)):
        gui_register_pages()
        await user.open("/dataset/idc")
        user.find(marker="BUTTON_EXAMPLE_DATASET").click()
        await user.should_see("1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0")

        user.find(marker="SOURCE_INPUT").clear()
        user.find(marker="SOURCE_INPUT").type("1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0")
        await user.should_see("1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0")

        user.find(marker="BUTTON_DOWNLOAD_DESTINATION").click()
        await user.should_see(marker="BUTTON_FILEPICKER_CANCEL")
        user.find(marker="BUTTON_FILEPICKER_CANCEL").click()
        await user.should_see(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)

        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()
        await user.should_not_see(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)

        user.find(marker="BUTTON_DOWNLOAD").click()

        for _ in range(30):
            expected_file = (
                Path(tmpdir)
                / "tcga_luad"
                / "TCGA-91-6830"
                / "2.25.5646130214350101265514421836879989792"
                / "SM_1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.2.0"
                / "975bc2fa-d403-4c4c-affa-0fbb08475651.dcm"
            )
            if expected_file.exists():
                break
            await sleep(1)

        assert expected_file.exists(), f"Expected file {expected_file} not found"
        assert expected_file.stat().st_size == 1369290, (
            f"File size {expected_file.stat().st_size} doesn't match expected 1369290 bytes"
        )


@pytest.mark.parametrize(
    ("source_input", "expected_notification"),
    [
        (" ", "Download failed: No IDs provided."),
        (
            "4711",
            "Download failed: None of the values passed matched any of the identifiers: "
            "collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID.",
        ),
        (
            " ",
            "Download failed: No IDs provided",
        ),
    ],
)
async def test_gui_idc_download_fails_with_invalid_inputs(
    user: User, tmpdir, source_input: str, expected_notification: str
) -> None:
    """Test that the download fails with appropriate notification when invalid IDs are provided."""
    with patch("aignostics.system.Service.get_user_data_directory", return_value=Path(tmpdir)):
        gui_register_pages()
        await user.open("/dataset/idc")
        user.find(marker="SOURCE_INPUT").clear()
        user.find(marker="SOURCE_INPUT").type(source_input)

        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_DATA").click()
        await user.should_not_see(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)

        user.find(marker="BUTTON_DOWNLOAD").click()

        await _assert_notified(user, expected_notification, wait_seconds=30)
