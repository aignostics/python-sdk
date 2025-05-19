"""Tests to verify the CLI functionality of the system module."""

import os
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

THE_VALUE = "THE_VALUE"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


@pytest.mark.scheduled
def test_cli_health(runner: CliRunner) -> None:
    """Check health is true."""
    result = runner.invoke(cli, ["system", "health"])
    assert result.exit_code == 0
    assert "UP" in result.output


@pytest.mark.sequential
def test_cli_info(runner: CliRunner) -> None:
    """Check health is true."""
    result = runner.invoke(cli, ["system", "info"])
    assert result.exit_code == 0
    assert "aignostics.log" in result.output


@pytest.mark.sequential
def test_cli_info_secrets(runner: CliRunner) -> None:
    """Check secrets only shown if requested."""
    with runner.isolated_filesystem():
        # Set environment variable for the test
        env = os.environ.copy()
        env["AIGNOSTICS_SYSTEM_TOKEN"] = THE_VALUE

        # custom
        env["AIGNOSTICS_CLIENT_ID_DEVICE"] = THE_VALUE
        env["AIGNOSTICS_CLIENT_ID_INTERACTIVE"] = THE_VALUE
        # end custon

        # Run the CLI with the runner
        result = runner.invoke(cli, ["system", "info"], env=env)
        assert result.exit_code == 0
        assert THE_VALUE not in result.output

        # Run the CLI with the runner
        result = runner.invoke(cli, ["system", "info", "--no-filter-secrets"], env=env)
        assert result.exit_code == 0
        assert THE_VALUE in result.output


@patch("aignostics.utils._gui.gui_register_pages")
@patch("nicegui.ui.run")
def test_cli_serve_api_and_app(mock_ui_run, mock_register_pages, runner: CliRunner) -> None:
    """Check serve command starts the server with API and GUI app."""
    # Create mocks for components needed in gui_run
    mock_app = MagicMock()

    # Patch nicegui imports inside gui_run function
    with patch("nicegui.native.find_open_port", return_value=8123), patch("nicegui.app", mock_app):
        result = runner.invoke(cli, ["system", "serve", "--host", "127.0.0.1", "--port", "8000"])

        assert result.exit_code == 0
        assert "Starting web application server at http://127.0.0.1:8000" in result.output

        # Check that gui_register_pages was called
        mock_register_pages.assert_called_once()

        # Check that ui.run was called with the correct parameters
        mock_ui_run.assert_called_once_with(
            title="aignostics",
            favicon="",
            native=False,
            reload=False,
            dark=False,
            host="127.0.0.1",
            port=8000,
            frameless=False,
            show_welcome_message=True,
            show=False,
            window_size=None,
        )


def test_cli_openapi_yaml(runner: CliRunner) -> None:
    """Check openapi command outputs YAML schema."""
    result = runner.invoke(cli, ["system", "openapi", "--output-format", "yaml"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output

    result = runner.invoke(cli, ["system", "openapi", "--api-version", "v3", "--output-format", "yaml"])
    assert result.exit_code == 1
    assert "Error: Invalid API version 'v3'. Available versions: v1" in result.output


def test_cli_openapi_json(runner: CliRunner) -> None:
    """Check openapi command outputs JSON schema."""
    result = runner.invoke(cli, ["system", "openapi"])
    assert result.exit_code == 0
    # Check for common OpenAPI JSON elements
    assert '"openapi":' in result.output
    assert '"info":' in result.output
    assert '"paths":' in result.output


def test_cli_install(runner: CliRunner) -> None:
    """Check install command runs successfully."""
    result = runner.invoke(cli, ["system", "install"])
    assert result.exit_code == 0


def test_cli_whoami(runner: CliRunner) -> None:
    """Check install command runs successfully."""
    result = runner.invoke(cli, ["system", "whoami"])
    assert result.exit_code == 0
