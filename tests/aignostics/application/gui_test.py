"""Tests to verify the GUI functionality of the hello module."""

from nicegui.testing import User

from aignostics.utils import gui_register_pages


async def test_gui_index(user: User) -> None:
    """Test that the user sees the index page, and sees the output of the Hello service on click."""
    gui_register_pages()
    await user.open("/")
    await user.should_see("Atlas H&E-TME")
    await user.should_see("Download Datasets")
