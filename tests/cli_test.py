"""Tests to verify the CLI functionality of Aignostics Python SDK."""

import pytest
from typer.testing import CliRunner

from aignostics import (
    __version__,
)
from aignostics.cli import cli

BUILT_WITH_LOVE = "built with love in Berlin"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_built_with_love(runner) -> None:
    """Check epilog shown."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert BUILT_WITH_LOVE in result.output
    assert __version__ in result.output


def test_cli_health(runner: CliRunner) -> None:
    """Check health is true."""
    result = runner.invoke(cli, ["system", "health"])
    assert result.exit_code == 0
    assert "True" in result.output


def test_cli_info(runner: CliRunner) -> None:
    """Check health is true."""
    result = runner.invoke(cli, ["system", "info"])
    assert result.exit_code == 0
    assert "CPython" in result.output


def test_cli_openapi_yaml(runner: CliRunner) -> None:
    """Check openapi command outputs YAML schema."""
    result = runner.invoke(cli, ["system", "openapi"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output


def test_cli_openapi_json(runner: CliRunner) -> None:
    """Check openapi command outputs JSON schema."""
    result = runner.invoke(cli, ["system", "openapi", "--output-format", "json"])
    assert result.exit_code == 0
    # Check for common OpenAPI JSON elements
    assert '"openapi":' in result.output
    assert '"info":' in result.output
    assert '"paths":' in result.output
