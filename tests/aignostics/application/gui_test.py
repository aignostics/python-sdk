"""Tests to verify the GUI functionality of the application module."""

import re
from pathlib import Path

import pytest
from nicegui.testing import User
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import gui_register_pages


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


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


async def test_runs_shown(user: User, runner: CliRunner, tmp_path: Path) -> None:
    """Test that the user can navigate to a run."""
    gui_register_pages()

    # Submit run
    csv_content = "source;checksum_crc32c;base_mpp;width;height;cancer.type;cancer.tissue\n"
    csv_content += "gs://bucket/test;5onqtA==;0.26268186053789266;7447;7196;lung;lung"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)
    result = runner.invoke(
        cli, ["application", "run", "submit", "--application-version-id", "he-tme:v0.45.0", "--source", str(csv_path)]
    )
    assert result.exit_code == 0
    assert re.search(
        r"submitted run with id 'Application run `[0-9a-f-]+`:\s+running, 1 items - \(1/0/0\)", result.output
    ), f"Output '{result.output}' doesn't match expected pattern"

    # Open the GUI and check that the run is shown
    await user.open("/")
    await user.should_see("Applications")
    await user.should_see("Atlas H&E-TME")
    await user.should_see("Runs")
    await user.should_see("he-tme:v0.45.0", marker="SIDEBAR_RUN_ITEM:0", retries=1000)
