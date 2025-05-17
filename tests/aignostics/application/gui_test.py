"""Tests to verify the GUI functionality of the application module."""

import pytest
from nicegui.testing import User

from aignostics.utils import gui_register_pages


async def test_gui_index(user: User) -> None:
    """Test that the user sees the index page, and sees the intro."""
    gui_register_pages()
    await user.open("/")
    await user.should_see("Atlas H&E-TME")
    await user.should_see("Download Datasets")


@pytest.mark.parametrize(
    ("route", "expected_text"),
    [
        (
            "/application/he-tme",
            "Atlas H&E TME is an AI application designed to examine FFPE",
        ),
        (
            "/application/test-app",
            "This is the test application with two algorithms: TissueQc and Tissue Segmentation",
        ),
    ],
)
async def test_gui_applications(user: User, route: str, expected_text: str) -> None:
    """Test that the user sees the specific application page with expected content."""
    gui_register_pages()
    await user.open(route)
    await user.should_see(expected_text)


async def test_gui_run(user: User) -> None:
    """Test that the user sees the index page, and sees the intro."""
    gui_register_pages()
    await user.open("/application/run/6adbd0fe-a82a-4fda-9eab-a9619d82299f")
    await user.should_see("Run of")


async def test_runs_shown(user: User) -> None:
    """Test that the user can navigate to a run."""
    gui_register_pages()
    await user.open("/")
    await user.should_see("Atlas H&E-TME")
    await user.should_see("Runs")
    await user.should_see("he-tme", marker="SIDEBAR_RUN_ITEM:0", retries=100)
