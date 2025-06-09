"""Tests to verify the GUI functionality of the info module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from nicegui.testing import User, UserInteraction
    from nicegui.ui import switch

from aignostics.utils import __project_name__, gui_register_pages


@pytest.mark.sequential
async def test_gui_system_switch_right(user: User, silent_logging) -> None:
    """Test that the user sees the info page with the mask secrets switch on by default."""
    gui_register_pages()
    await user.open("/system")
    await user.should_see(__project_name__)
    await user.should_see("Health")
    await user.should_see("Info")
    await user.should_see("Settings")
    await user.should_see("Mask secrets", retries=5 * 100)
    switch_interaction: UserInteraction = user.find("Mask secrets")
    switch_element: switch = switch_interaction.elements.pop()
    assert switch_element.value is True
