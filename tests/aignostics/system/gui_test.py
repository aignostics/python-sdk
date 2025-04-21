"""Tests to verify the GUI functionality of the info module."""

from nicegui.testing import User

from aignostics.utils import __project_name__, gui_register_pages


async def test_gui_info(user: User) -> None:
    """Test that the user sees the info page, and the output includes the project name."""
    gui_register_pages()
    await user.open("/info")
    await user.should_see("Home")
    await user.should_see(__project_name__)
