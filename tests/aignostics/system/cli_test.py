"""Tests to verify the CLI functionality of the system module."""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import __project_name__
from tests.conftest import normalize_output

THE_VALUE = "test_secret_value_not_real_for_testing_only"


@pytest.mark.unit
@patch("aignostics.system._cli._service")
def test_cli_health_json_format(mock_service: MagicMock, runner: CliRunner, record_property) -> None:
    """Check health CLI renders UP status correctly as JSON."""
    record_property("tested-item-id", "TEST-SYSTEM-CLI-HEALTH-JSON")
    from aignostics.utils import Health

    mock_service.health = AsyncMock(return_value=Health(status=Health.Code.UP))
    result = runner.invoke(cli, ["system", "health"])
    assert result.exit_code == 0
    assert normalize_output(result.stdout).startswith('{  "status": "UP"')


@pytest.mark.unit
@patch("aignostics.system._cli._service")
def test_cli_health_yaml_format(mock_service: MagicMock, runner: CliRunner, record_property) -> None:
    """Check health CLI renders UP status correctly as YAML."""
    record_property("tested-item-id", "TEST-SYSTEM-CLI-HEALTH-YAML")
    from aignostics.utils import Health

    mock_service.health = AsyncMock(return_value=Health(status=Health.Code.UP))
    result = runner.invoke(cli, ["system", "health", "--output-format", "yaml"])
    assert result.exit_code == 0
    assert "status: UP" in result.stdout


@pytest.mark.e2e
@pytest.mark.scheduled
@pytest.mark.platform_api
@pytest.mark.timeout(timeout=60)
def test_cli_health_json(runner: CliRunner) -> None:
    """Check health CLI returns valid JSON with a valid status value."""
    import json

    result = runner.invoke(cli, ["system", "health"])
    data = json.loads(result.stdout)
    assert data["status"] in {"UP", "DEGRADED", "DOWN"}


@pytest.mark.e2e
@pytest.mark.timeout(timeout=30)
def test_cli_health_yaml(runner: CliRunner) -> None:
    """Check health CLI returns valid YAML with a valid status value."""
    import yaml

    result = runner.invoke(cli, ["system", "health", "--output-format", "yaml"])
    data = yaml.safe_load(result.stdout)
    assert data["status"] in {"UP", "DEGRADED", "DOWN"}


@pytest.mark.e2e
@pytest.mark.timeout(timeout=30)
def test_cli_info(runner: CliRunner, record_property) -> None:
    """Check aignostics.log in outpu of system info."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    result = runner.invoke(cli, ["system", "info"])
    assert result.exit_code == 0
    assert "aignostics.log" in result.output


@pytest.mark.e2e
@pytest.mark.timeout(timeout=30)
@pytest.mark.sequential
def test_cli_info_secrets(runner: CliRunner, caplog: pytest.LogCaptureFixture, record_property) -> None:
    """Check secrets only shown if requested.

    This test verifies that secrets are properly masked by default and only shown
    when explicitly requested. We use safe assertion patterns to avoid exposing
    secret values in test failure output and disable logging to prevent secret
    exposure in logs.
    """
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    # Disable all logging to prevent secrets from appearing in logs

    # Set environment variable for the test
    env = os.environ.copy()
    env["AIGNOSTICS_SYSTEM_TOKEN"] = THE_VALUE

    # custom
    env["AIGNOSTICS_CLIENT_ID_DEVICE"] = THE_VALUE
    env["AIGNOSTICS_CLIENT_ID_INTERACTIVE"] = THE_VALUE
    # end custon

    # Run the CLI with the runner - secrets should be masked by default
    result = runner.invoke(cli, ["system", "info"], env=env)
    assert result.exit_code == 0
    # Verify secrets are properly masked (safe assertion - no secret exposure)
    secret_is_masked = THE_VALUE not in result.output
    assert secret_is_masked, "Secret value found in masked output - this is a security issue"

    # Run the CLI with --no-mask-secrets flag - secrets should be visible
    result = runner.invoke(cli, ["system", "info", "--no-mask-secrets"], env=env)
    assert result.exit_code == 0
    # Check for secrets presence without exposing them in assertion failures
    secret_found = THE_VALUE in result.output
    assert secret_found, "Expected secret value to be present in unmasked output, but it was not found"


@pytest.mark.unit
@patch("aignostics.system._cli._service")
def test_cli_health_up_exits_zero(mock_service: MagicMock, runner: CliRunner) -> None:
    """Check health command exits with code 0 when status is UP."""
    from aignostics.utils import Health

    mock_service.health = AsyncMock(return_value=Health(status=Health.Code.UP))
    result = runner.invoke(cli, ["system", "health"])
    assert result.exit_code == 0


@pytest.mark.unit
@patch("aignostics.system._cli._service")
def test_cli_health_degraded_exits_zero(mock_service: MagicMock, runner: CliRunner) -> None:
    """Check health command exits with code 0 when status is DEGRADED."""
    from aignostics.utils import Health

    mock_service.health = AsyncMock(return_value=Health(status=Health.Code.DEGRADED, reason="some component degraded"))
    result = runner.invoke(cli, ["system", "health"])
    assert result.exit_code == 0


@pytest.mark.unit
@patch("aignostics.system._cli._service")
def test_cli_health_down_exits_one(mock_service: MagicMock, runner: CliRunner) -> None:
    """Check health command exits with code 1 when status is DOWN."""
    from aignostics.utils import Health

    mock_service.health = AsyncMock(return_value=Health(status=Health.Code.DOWN, reason="service unavailable"))
    result = runner.invoke(cli, ["system", "health"])
    assert result.exit_code == 1


@pytest.mark.integration
@patch("aignostics.utils._gui.gui_register_pages")
@patch("nicegui.ui.run")
def test_cli_serve_api_and_app(mock_ui_run, mock_register_pages, runner: CliRunner, record_property) -> None:
    """Check serve command starts the server with API and GUI app."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")

    # Create mocks for components needed in gui_run
    mock_app = MagicMock()

    # Patch nicegui imports inside gui_run function
    with patch("nicegui.native.find_open_port", return_value=8123), patch("nicegui.app", mock_app):
        result = runner.invoke(cli, ["system", "serve", "--host", "127.0.0.1", "--port", "8000"])

        assert result.exit_code == 0
        assert "Starting web application server" in result.output
        assert "http://127.0.0.1:8000" in result.output

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
            reconnect_timeout=60 * 60 * 24 * 7,
        )


@pytest.mark.integration
def test_cli_openapi_yaml(runner: CliRunner, record_property) -> None:
    """Check openapi command outputs YAML schema."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    result = runner.invoke(cli, ["system", "openapi", "--output-format", "yaml"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output

    result = runner.invoke(cli, ["system", "openapi", "--api-version", "v3", "--output-format", "yaml"])
    assert result.exit_code == 1
    assert "Error: Invalid API version 'v3'. Available versions: v1" in result.output


@pytest.mark.integration
def test_cli_openapi_json(runner: CliRunner, record_property) -> None:
    """Check openapi command outputs JSON schema."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    result = runner.invoke(cli, ["system", "openapi"])
    assert result.exit_code == 0
    # Check for common OpenAPI JSON elements
    assert '"openapi":' in result.output
    assert '"info":' in result.output
    assert '"paths":' in result.output


@pytest.mark.integration
def test_cli_install(runner: CliRunner, record_property) -> None:
    """Check install command runs successfully."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    result = runner.invoke(cli, ["system", "install"])
    assert result.exit_code == 0


@pytest.mark.integration
@pytest.mark.sequential
def test_cli_set_unset_get(runner: CliRunner, silent_logging, tmp_path, record_property) -> None:
    """Check set, unset, and get commands."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.integration
@pytest.mark.sequential
def test_cli_remote_diagnostics(runner: CliRunner, silent_logging, tmp_path: Path, record_property) -> None:
    """Check disable/enable remote diagnostics."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.integration
@pytest.mark.sequential
@pytest.mark.timeout(timeout=60)
def test_cli_http_proxy(runner: CliRunner, silent_logging, tmp_path: Path, record_property) -> None:  # noqa: PLR0915
    """Check disable/enable remote diagnostics."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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
        assert str(cert_file.resolve()) in normalize_output(result.stdout)

        result = runner.invoke(cli, ["system", "config", "get", "REQUESTS_CA_BUNDLE"])
        assert result.exit_code == 0
        assert str(cert_file.resolve()) in normalize_output(result.stdout)

        result = runner.invoke(cli, ["system", "config", "get", "CURL_CA_BUNDLE"])
        assert result.exit_code == 0
        assert str(cert_file.resolve()) in normalize_output(result.stdout)

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
        assert "Cannot set both 'ssl_cert_file' and 'ssl_disable_verify'. Please choose one." in result.output.replace(
            "\n", ""
        )

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


@pytest.mark.integration
def test_cli_dump_dot_env_file(runner: CliRunner, silent_logging, tmp_path: Path) -> None:
    """Check dump-dot-env-file command creates a file with all settings."""
    with patch("aignostics.system.Service._get_env_files_paths", return_value=[tmp_path / ".env"]):
        # Create the .env file that the system expects to exist
        (tmp_path / ".env").touch()

        # Set some test environment variables to verify they appear in the dump
        env = os.environ.copy()
        env["AIGNOSTICS_SYSTEM_TOKEN"] = "test_token_value"  # noqa: S105 # Test data, not a real password
        env["AIGNOSTICS_PLATFORM_BASE_URL"] = "https://test.example.com"

        # Create a destination file path
        destination = tmp_path / ".env.test"

        # Run the dump-dot-env-file command
        result = runner.invoke(cli, ["system", "dump-dot-env-file", "--destination", str(destination)], env=env)

        # Check the command succeeded
        assert result.exit_code == 0
        assert f"Settings dumped to {destination}" in normalize_output(result.output)

        # Verify the file was created
        assert destination.exists()
        assert destination.is_file()

        # Read and verify the content
        content = destination.read_text()

        # Check that the file is not empty
        assert len(content) > 0

        # Check that it contains some expected settings keys (should be in uppercase with prefix)
        lines = content.strip().split("\n")
        assert len(lines) > 0

        # Verify format: each line should be KEY=VALUE
        for line in lines:
            if line.strip():  # Skip empty lines
                assert "=" in line, f"Line '{line}' does not have KEY=VALUE format"

        # Check for specific settings that should be present
        # The settings should be in the format ENV_PREFIX + KEY in uppercase
        settings_keys = [key.split("=")[0] for key in lines if "=" in key]

        # Should contain system settings
        assert any("AIGNOSTICS_SYSTEM" in key for key in settings_keys), "Should contain AIGNOSTICS_SYSTEM settings"

        # Verify that the token value is present (unmasked in dump)
        assert "AIGNOSTICS_SYSTEM_TOKEN=test_token_value" in content or "AIGNOSTICS_SYSTEM_TOKEN=None" in content
