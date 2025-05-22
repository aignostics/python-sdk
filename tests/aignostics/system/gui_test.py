"""Tests to verify the GUI functionality of the info module."""

import pytest
from nicegui.testing import User

from aignostics.utils import __project_name__, gui_register_pages


@pytest.mark.sequential
async def test_gui_system(user: User) -> None:
    """Test that the user sees the info page, and the output includes the project name."""
    gui_register_pages()
    await user.open("/system")
    await user.should_see("Health")
    await user.should_see("Info")
    await user.should_see(__project_name__)
