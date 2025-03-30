"""Tests to verify the CLI functionality of Aignostics Python SDK."""

import os
import subprocess
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


def test_cli_echo(runner: CliRunner) -> None:
    """Check hello world printed."""
    result = runner.invoke(cli, ["echo", "hello"])
    assert result.exit_code == 0
    assert "HELLO" in result.output


def test_cli_echo_fails_on_silence(runner: CliRunner) -> None:
    """Check hello world printed."""
    result = runner.invoke(cli, ["echo", ""])
    assert result.exit_code == 1


def test_cli_echo_json(runner: CliRunner) -> None:
    """Check hello world printed."""
    result = runner.invoke(cli, ["echo", "hello", "--json"])
    assert result.exit_code == 0
    assert '{\n  "text": "HELLO"\n}\n' in result.output


def test_cli_hello_world(runner: CliRunner) -> None:
    """Check hello world printed."""
    result = runner.invoke(cli, ["hello-world"])
    assert result.exit_code == 0
    assert "Hello, world!" in result.output


def test_cli_hello_world_german() -> None:
    """Check hello world printed."""
    env_de = os.environ.copy()
    env_de.update({"AIGNOSTICS_LANGUAGE": "de_DE"})
    completed_process = subprocess.run(["aignostics", "hello-world"], capture_output=True, check=False, env=env_de)
    assert completed_process.stdout == b"Hallo, Welt!\n"


@patch("uvicorn.run")
def test_cli_serve(mock_uvicorn_run, runner: CliRunner) -> None:
    """Check serve command starts the server."""
    result = runner.invoke(cli, ["serve", "--host", "127.0.0.1", "--port", "8000", "--no-watch"])
    assert result.exit_code == 0
    assert "Starting API server at http://127.0.0.1:8000" in result.output
    mock_uvicorn_run.assert_called_once_with(
        "aignostics.api:app",
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
    assert "Echo:" in result.output

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
