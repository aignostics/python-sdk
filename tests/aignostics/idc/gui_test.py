"""Tests to verify the GUI functionality of the idc module."""

from nicegui.testing import User

from aignostics.utils import gui_register_pages


async def test_gui_idc(user: User) -> None:
    """Test that the user sees the dataset page."""
    gui_register_pages()
    await user.open("/idc")
    await user.should_see("Explore Portal")
