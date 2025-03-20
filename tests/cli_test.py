"""Tests to verify the CLI functionality of Aignostics Python SDK."""

from unittest.mock import patch

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


def test_cli_echo(runner: CliRunner) -> None:
    """Check hello world printed."""
    result = runner.invoke(cli, ["echo", "4711"])
    assert result.exit_code == 0
    assert "4711" in result.output


def test_cli_hello_world(runner: CliRunner) -> None:
    """Check hello world printed."""
    result = runner.invoke(cli, ["hello-world"])
    assert result.exit_code == 0
    assert "Hello, world!" in result.output


@patch("uvicorn.run")
def test_cli_serve(mock_uvicorn_run, runner: CliRunner) -> None:
    """Check serve command starts the server."""
    result = runner.invoke(cli, ["serve", "--host", "127.0.0.1", "--port", "8000", "--no-watch"])
    assert result.exit_code == 0
    assert "Starting API server at http://127.0.0.1:8000" in result.output
    mock_uvicorn_run.assert_called_once_with(
        "aignostics.api:api",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


def test_cli_openapi_yaml(runner: CliRunner) -> None:
    """Check openapi command outputs YAML schema."""
    result = runner.invoke(cli, ["openapi"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output
    # Check for specific v1 elements
    assert "EchoRequest:" in result.output

    result = runner.invoke(cli, ["openapi", "--api-version", "v2"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output
    # Check for specific v2 elements
    assert "Utterance:" in result.output


def test_cli_openapi_json(runner: CliRunner) -> None:
    """Check openapi command outputs JSON schema."""
    result = runner.invoke(cli, ["openapi", "--output-format", "json"])
    assert result.exit_code == 0
    # Check for common OpenAPI JSON elements
    assert '"openapi":' in result.output
    assert '"info":' in result.output
    assert '"paths":' in result.output
