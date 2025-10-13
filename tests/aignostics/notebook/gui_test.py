"""Tests to verify the GUI functionality of the Notebook module."""

import pytest
from nicegui.testing import User
from typer.testing import CliRunner


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
async def test_gui_marimo_extension(user: User, runner: CliRunner, silent_logging: None) -> None:
    """Test that the user can install and launch Marimo via the GUI."""
    # Step 1: Check we are on the Notebook page
    await user.open("/notebook")
    await user.should_see("Manage your Marimo Extension")

    await user.should_see(marker="LINK_NOTEBOOK_LAUNCH")
    user.find(marker="LINK_NOTEBOOK_LAUNCH").click()

    await user.should_not_see("Manage your Marimo Extension", retries=100)
    await user.should_see(marker="BUTTON_NOTEBOOK_BACK")
    await user.should_see("marimo_iframe")
    user.find(marker="BUTTON_NOTEBOOK_BACK").click()

    await user.should_see("Marimo Extension", retries=100)
