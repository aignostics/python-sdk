"""Tests to verify the GUI functionality of the idc module."""

from asyncio import sleep
from pathlib import Path
from unittest.mock import patch

from nicegui.testing import User

from aignostics.utils import gui_register_pages


async def test_gui_idc_shows(user: User) -> None:
    """Test that the user sees the dataset page."""
    gui_register_pages()
    await user.open("/idc")
    await user.should_see("Explore Portal")


async def test_gui_idc_downloads(user: User, tmpdir) -> None:
    """Test that the user can download a dataset to a temporary directory."""
    # Mock Path.home() to return the tmpdir for this test
    with patch("pathlib.Path.home", return_value=Path(tmpdir)):
        gui_register_pages()
        await user.open("/idc")
        user.find(marker="BUTTON_EXAMPLE_DATASET").click()
        await user.should_see("1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0")

        user.find(marker="SOURCE_INPUT").clear()
        user.find(marker="SOURCE_INPUT").type("1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0")
        await user.should_see("1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0")

        user.find(marker="BUTTON_DOWNLOAD_DESTINATION").click()
        await user.should_see(marker="BUTTON_FILEPICKER_CANCEL")
        user.find(marker="BUTTON_FILEPICKER_CANCEL").click()
        await user.should_see("No download folder selected")

        user.find(marker="BUTTON_DOWNLOAD_DESTINATION_HOME").click()
        await user.should_not_see("No download folder selected")
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
