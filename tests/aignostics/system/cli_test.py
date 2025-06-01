"""Tests to verify the CLI functionality of the system module."""

import logging
import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import __project_name__

THE_VALUE = "THE_VALUE"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


@pytest.fixture
def silent_logging(caplog) -> Generator[None, None, None]:
    """Suppress logging output during test execution.

    Args:
        caplog (pytest.LogCaptureFixture): The pytest fixture for capturing log messages.

    Yields:
        None: This fixture doesn't yield any value.
    """
    with caplog.at_level(logging.CRITICAL + 1):
        yield


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


@pytest.mark.sequential
def test_cli_set_unset_get(runner: CliRunner, silent_logging, tmp_path) -> None:
    """Check set, unset, and get commands."""
    with patch("aignostics.system.Service._get_env_files_paths", return_value=[tmp_path / ".env"]):
        (tmp_path / ".env").touch()
        result = runner.invoke(cli, ["system", "config", "unset", "test_key"])

        # Get a value
        result = runner.invoke(cli, ["system", "config", "get", "test_key"])
        assert result.exit_code == 0
        assert "None" in result.output

        # Set a value
        result = runner.invoke(cli, ["system", "config", "set", "test_key", "test_value"])
        assert result.exit_code == 0
        assert "Configuration 'TEST_KEY' set to 'test_value'." in result.output

        # Get the value again
        result = runner.invoke(cli, ["system", "config", "get", "test_key"])
        assert result.exit_code == 0
        assert "test_value" in result.output

        # Unset the value
        result = runner.invoke(cli, ["system", "config", "unset", "test_key"])
        assert result.exit_code == 0
        assert "Configuration 'TEST_KEY' unset." in result.output

        # Get the value after unset
        result = runner.invoke(cli, ["system", "config", "get", "test_key"])
        assert result.exit_code == 0
        assert "None" in result.output

    @pytest.mark.sequential
    def test_cli_remote_diagnostics(runner: CliRunner, silent_logging, tmp_path: Path) -> None:
        """Check disable/enable remote diagnostics."""
        with patch("aignostics.system.Service._get_env_files_paths", return_value=[tmp_path / ".env"]):
            (tmp_path / ".env").touch()
            result = runner.invoke(cli, ["system", "config", "remote-diagnostics-disable"])

            # Check not set
            result = runner.invoke(cli, ["system", "config", "get", __project_name__ + "_SENTRY_ENABLED"])
            assert result.exit_code == 0
            assert "None" in result.output

            result = runner.invoke(cli, ["system", "config", "get", __project_name__ + "_LOGFIRE_ENABLED"])
            assert result.exit_code == 0
            assert "None" in result.output

            # Enable
            result = runner.invoke(cli, ["system", "config", "remote-diagnostics-enable"])
            assert result.exit_code == 0
            assert "Remote diagnostics enabled." in result.output

            result = runner.invoke(cli, ["system", "config", "get", __project_name__ + "_SENTRY_ENABLED"])
            assert result.exit_code == 0
            assert "1" in result.output

            result = runner.invoke(cli, ["system", "config", "get", __project_name__ + "_LOGFIRE_ENABLED"])
            assert result.exit_code == 0
            assert "1" in result.output

            # Disable
            result = runner.invoke(cli, ["system", "config", "remote-diagnostics-disable"])

            result = runner.invoke(cli, ["system", "config", "get", __project_name__ + "_SENTRY_ENABLED"])
            assert result.exit_code == 0
            assert "None" in result.output

            result = runner.invoke(cli, ["system", "config", "get", __project_name__ + "_LOGFIRE_ENABLED"])
            assert result.exit_code == 0
            assert "None" in result.output


@pytest.mark.sequential
def test_cli_http_proxy(runner: CliRunner, silent_logging, tmp_path: Path) -> None:  # noqa: PLR0915
    """Check disable/enable remote diagnostics."""
    with patch("aignostics.system.Service._get_env_files_paths", return_value=[tmp_path / ".env"]):
        # Set up a mock .env file
        (tmp_path / ".env").touch()

        # Set up a mock cert file
        cert_file = tmp_path / "cert"
        cert_file.touch()

        result = runner.invoke(cli, ["system", "config", "http-proxy-disable"])

        # Check not set
        result = runner.invoke(cli, ["system", "config", "get", "HTTP_PROXY"])
        assert result.exit_code == 0
        assert "None" in result.output

        # Enable
        result = runner.invoke(cli, ["system", "config", "http-proxy-enable"])
        assert result.exit_code == 0
        assert "HTTP proxy enabled." in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTP_PROXY"])
        assert result.exit_code == 0
        assert "http://proxy.charite.de:8080" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTPS_PROXY"])
        assert result.exit_code == 0
        assert "http://proxy.charite.de:8080" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_NO_VERIFY"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_CERT_FILE"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "REQUESTS_CA_BUNDLE"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "CURL_CA_BUNDLE"])
        assert result.exit_code == 0
        assert "None" in result.output

        # Enable with SSL cert file

        result = runner.invoke(cli, ["system", "config", "http-proxy-enable", "--ssl-cert-file", str(cert_file)])
        assert result.exit_code == 0
        assert "HTTP proxy enabled." in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTP_PROXY"])
        assert result.exit_code == 0
        assert "http://proxy.charite.de:8080" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTPS_PROXY"])
        assert result.exit_code == 0
        assert "http://proxy.charite.de:8080" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_NO_VERIFY"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_CERT_FILE"])
        assert result.exit_code == 0
        assert str(cert_file.resolve()) in result.output.replace("\n", "")

        result = runner.invoke(cli, ["system", "config", "get", "REQUESTS_CA_BUNDLE"])
        assert result.exit_code == 0
        assert str(cert_file.resolve()) in result.output.replace("\n", "")

        result = runner.invoke(cli, ["system", "config", "get", "CURL_CA_BUNDLE"])
        assert result.exit_code == 0
        assert str(cert_file.resolve()) in result.output.replace("\n", "")

        # Enable with no verify

        result = runner.invoke(cli, ["system", "config", "http-proxy-enable", "--no-ssl-verify"])
        assert result.exit_code == 0
        assert "HTTP proxy enabled." in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTP_PROXY"])
        assert result.exit_code == 0
        assert "http://proxy.charite.de:8080" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTPS_PROXY"])
        assert result.exit_code == 0
        assert "http://proxy.charite.de:8080" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_NO_VERIFY"])
        assert result.exit_code == 0
        assert "1" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_CERT_FILE"])
        assert result.exit_code == 0
        assert result.output == "\n"

        result = runner.invoke(cli, ["system", "config", "get", "REQUESTS_CA_BUNDLE"])
        assert result.exit_code == 0
        assert result.output == "\n"

        result = runner.invoke(cli, ["system", "config", "get", "CURL_CA_BUNDLE"])
        assert result.exit_code == 0
        assert result.output == "\n"

        # Enable with no verify and ssl cert file conclicts

        result = runner.invoke(
            cli, ["system", "config", "http-proxy-enable", "--no-ssl-verify", "--ssl-cert-file", str(cert_file)]
        )
        assert result.exit_code == 2
        assert "Cannot set both 'ssl_cert_file' and 'ssl_disable_verify'. Please choose one." in result.output

        # Disable
        result = runner.invoke(cli, ["system", "config", "http-proxy-disable"])
        assert result.exit_code == 0
        assert "HTTP proxy disabled." in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTP_PROXY"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "HTTPS_PROXY"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_NO_VERIFY"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "SSL_CERT_FILE"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "REQUESTS_CA_BUNDLE"])
        assert result.exit_code == 0
        assert "None" in result.output

        result = runner.invoke(cli, ["system", "config", "get", "CURL_CA_BUNDLE"])
        assert result.exit_code == 0
        assert "None" in result.output
