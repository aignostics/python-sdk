"""Tests to verify the GUI functionality of the bucket module."""

from nicegui.testing import User

from aignostics.utils import gui_register_pages


async def test_gui_bucket(user: User) -> None:
    """Test that the user sees the dataset page."""
    gui_register_pages()
    await user.open("/bucket")
    await user.should_see("The bucket is securely hosted on Google Cloud in EU")
