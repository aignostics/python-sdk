"""Tests to verify the CLI functionality of the QuPath module."""

import os
import re
import signal

import appdirs
import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import __project_name__


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_defaults(runner: CliRunner) -> None:
    """Check expected output and exit code."""
    result = runner.invoke(cli, ["qupath", "defaults"])
    assert all(index in result.output.replace("\n", "") for index in ["qupath_search_dirs"])
    assert result.exit_code == 0


def test_cli_settings(runner: CliRunner) -> None:
    """Check expected output and exit code."""
    result = runner.invoke(cli, ["qupath", "settings"])
    assert all(index in result.output.replace("\n", "") for index in [appdirs.user_data_dir(__project_name__)])
    assert result.exit_code == 0


@pytest.mark.sequential
def test_cli_install_and_launch(runner: CliRunner) -> None:
    """Check expected column returned."""
    # Uninstall QuPath if it exists to have a clean state for the test
    result = runner.invoke(cli, ["qupath", "uninstall"])
    was_installed = result.exit_code == 0

    # Step 1: Check QuPath launch fails if not installed
    result = runner.invoke(cli, ["qupath", "launch"])
    assert "QuPath is not installed. Use 'uvx aignostics qupath install' to install it." in result.output.replace(
        "\n", ""
    )
    assert result.exit_code == 2

    # Step 2: Check QuPath install succeeds
    result = runner.invoke(cli, ["qupath", "install"])
    assert "QuPath v0.5.1 installed successfully" in result.output.replace("\n", "")
    assert result.exit_code == 0

    # Step 3: Check QuPath can now launch successfully
    result = runner.invoke(cli, ["qupath", "launch"])
    assert "QuPath launched successfully" in result.output.replace("\n", "")
    assert result.exit_code == 0
    pid_match = re.search(r"QuPath launched successfully with process id '(\d+)'.", result.output.replace("\n", ""))
    assert pid_match is not None, "PID not found in launch output"
    pid = int(pid_match.group(1))
    try:
        os.kill(pid, 0)  # Signal 0 just tests if process exists
        process_exists = True
    except OSError:
        process_exists = False
    assert process_exists, f"Process with PID {pid} is not running"
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError as e:
        pytest.fail(f"Failed to kill QuPath process: {e}")

    # Step 4: Check QuPath install succeeds (idempotent operation)
    result = runner.invoke(cli, ["qupath", "install"])
    assert "QuPath v0.5.1 installed successfully" in result.output.replace("\n", "")
    assert result.exit_code == 0

    # Step 5: Uninstall QuPath
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert "QuPath uninstalled successfully." in result.output.replace("\n", "")
    assert result.exit_code == 0

    # Step 6: Check QuPath launch fails if not installed
    result = runner.invoke(cli, ["qupath", "launch"])
    assert "QuPath is not installed. Use 'uvx aignostics qupath install' to install it." in result.output.replace(
        "\n", ""
    )
    assert result.exit_code == 2

    # Step 7: Reinstall QuPath if it was installed before
    if was_installed:
        result = runner.invoke(cli, ["qupath", "install"])
