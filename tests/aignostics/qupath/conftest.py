"""Shared fixtures for QuPath tests."""

from collections.abc import Generator

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli


@pytest.fixture
def qupath_save_restore(runner: CliRunner) -> Generator[None, None, None]:
    """Uninstall QuPath for clean state, restore after test if it was installed."""
    result = runner.invoke(cli, ["qupath", "uninstall"])
    assert result.exit_code in {0, 2}, (
        f"Unexpected exit code {result.exit_code} from 'qupath uninstall': {result.output}"
    )
    was_installed = result.exit_code == 0
    yield
    if was_installed:
        reinstall_result = runner.invoke(cli, ["qupath", "install"])
        if reinstall_result.exit_code != 0:
            pytest.fail(
                f"Failed to reinstall QuPath in qupath_save_restore fixture "
                f"(exit code {reinstall_result.exit_code}). Output:\n{reinstall_result.output}"
            )
