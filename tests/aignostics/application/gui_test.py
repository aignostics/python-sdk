"""Tests to verify the GUI functionality of the hello module."""

from nicegui.testing import User

from aignostics.utils import gui_register_pages


async def test_gui_index(user: User) -> None:
    """Test that the user sees the index page, and sees the output of the Hello service on click."""
    gui_register_pages()
    await user.open("/")
    await user.should_see("Click me")
    user.find(marker="BUTTON_CLICK_ME").click()
    await user.should_see("Hello, world!")
    await user.should_see("Choose file")
    user.find(marker="BUTTON_CHOOSE_FILE").click()
    await user.should_see("Cancel")
    user.find(marker="BUTTON_CANCEL").click()
    await user.should_see("You chose None")
    await user.should_see("Choose file")
    user.find(marker="BUTTON_CHOOSE_FILE").click()
    await user.should_see("Ok")
    user.find(marker="BUTTON_OK").click()
    await user.should_see("You chose")
