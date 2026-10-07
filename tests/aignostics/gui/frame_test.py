"""Tests of the shared Launchpad page frame."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from nicegui import ui

from aignostics.constants import CONSOLE_URL, DEPRECATION_NOTICE, PLATFORM_API_DOCS_URL

if TYPE_CHECKING:
    from nicegui.testing import User


@pytest.mark.integration
async def test_gui_deprecation_banner_on_start_page(user: User, silent_logging: None) -> None:
    """The start page shows the deprecation banner with the notice text."""
    await user.open("/")
    await user.should_see(marker="DEPRECATION_BANNER")
    await user.should_see(DEPRECATION_NOTICE)


@pytest.mark.integration
async def test_gui_deprecation_banner_on_system_page(user: User, silent_logging: None) -> None:
    """The system page shows the same banner, so the banner is part of the shared frame."""
    await user.open("/system")
    await user.should_see(marker="DEPRECATION_BANNER")
    await user.should_see(DEPRECATION_NOTICE)


@pytest.mark.integration
async def test_gui_deprecation_banner_links_to_alternatives(user: User, silent_logging: None) -> None:
    """The banner itself links to the REST API docs and the Console (the drawer link does not count)."""
    await user.open("/")
    await user.should_see(marker="DEPRECATION_BANNER")
    banner = user.find(marker="DEPRECATION_BANNER").elements.pop()
    link_targets = {link.props.get("href") for link in user.find(ui.link).elements if link in banner.descendants()}
    assert PLATFORM_API_DOCS_URL in link_targets
    assert CONSOLE_URL in link_targets
