"""Tests to verify the CLI functionality of the bucket module."""

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_bucket_ls(runner: CliRunner) -> None:
    """Check bucket ls command runs successfully."""
    result = runner.invoke(cli, ["bucket", "ls"])
    assert result.exit_code == 0
    assert "aignostics-platform-ext-a4f7e9/helmut/" in result.output


def test_cli_bucket_find(runner: CliRunner) -> None:
    """Check bucket find command runs successfully."""
    result = runner.invoke(cli, ["bucket", "find"])
    assert result.exit_code == 0
    assert "030b1486ca88" in result.output


def test_cli_bucket_delete_not_found(runner: CliRunner) -> None:
    """Check bucket find command runs successfully."""
    result = runner.invoke(cli, ["bucket", "delete", "4711"])
    assert result.exit_code == 0
    assert "Object with key '4711' not found" in result.output


def test_cli_bucket_purge(runner: CliRunner) -> None:
    """Check bucket purge command runs successfully."""
    result = runner.invoke(cli, ["bucket", "purge"])
    assert result.exit_code == 0
    assert MESSAGE_NOT_YET_IMPLEMENTED in result.output
