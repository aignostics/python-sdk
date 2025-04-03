"""Tests to verify the CLI functionality of Aignostics Python SDK."""

import os
import subprocess

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
    result = runner.invoke(cli, ["health"])
    assert result.exit_code == 0
    assert "True" in result.output


def test_cli_info(runner: CliRunner) -> None:
    """Check health is true."""
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "en_US" in result.output


def test_cli_info_de() -> None:
    """Check hello world printed."""
    env_de = os.environ.copy()
    env_de.update({"AIGNOSTICS_LANGUAGE": "de_DE"})
    cli = "aignostics"
    completed_process = subprocess.run([cli, "info"], capture_output=True, check=False, env=env_de)
    assert completed_process.stdout == b'{"language":"de_DE"}\n'


def test_cli_openapi_yaml(runner: CliRunner) -> None:
    """Check openapi command outputs YAML schema."""
    result = runner.invoke(cli, ["openapi"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output


def test_cli_openapi_json(runner: CliRunner) -> None:
    """Check openapi command outputs JSON schema."""
    result = runner.invoke(cli, ["openapi", "--output-format", "json"])
    assert result.exit_code == 0
    # Check for common OpenAPI JSON elements
    assert '"openapi":' in result.output
    assert '"info":' in result.output
    assert '"paths":' in result.output
