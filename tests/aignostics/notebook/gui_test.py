"""Tests to verify the GUI functionality of the Notebook module."""

from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.utils import gui_register_pages
from tests.conftest import assert_notified


async def test_gui_marimo_extension(user: User, runner: CliRunner, silent_logging: None, record_property) -> None:
    """Test that the user can install and launch Marimo via the GUI."""
    record_property("tested-item-id", "ADR-16-NOTEBOOK-WEB-INTEGRATION-ARCHITECTURE")
    record_property("tested-item-id", "ADR-21-RESULT-DOWNLOAD-WEB-INTERFACE")
    record_property("tested-item-id", "TEST-SWR-NOTEBOOK-2-MANAGEMENT-INTERFACE")

    gui_register_pages()

    # Step 1: Check we are on the Notebook page
    await user.open("/notebook")
    await user.should_see("Manage your Marimo Extension")

    await user.should_see(marker="BUTTON_NOTEBOOK_LAUNCH")
    user.find(marker="BUTTON_NOTEBOOK_LAUNCH").click()
    await assert_notified(user, "Launching Python Notebook...", wait_seconds=10)

    await user.should_see(marker="BUTTON_NOTEBOOK_BACK", retries=100)
    await user.should_not_see("Manage your Marimo Extension")
    user.find(marker="BUTTON_NOTEBOOK_BACK").click()

    await user.should_see("Marimo Extension", retries=100)
