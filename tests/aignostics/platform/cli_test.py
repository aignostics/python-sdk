"""Tests to verify the CLI functionality of the platform module."""

from unittest.mock import patch

from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.platform._service import TokenInfo, UserInfo
from tests.conftest import normalize_output


class TestPlatformCLI:
    """Test cases for platform CLI commands."""

    @staticmethod
    def test_login_out_info_e2e(runner: CliRunner) -> None:
        """Test successful logout command."""
        with patch("aignostics.platform._service.Service.logout", return_value=True):
            result = runner.invoke(cli, ["platform", "login", "--relogin"])
            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)
            result = runner.invoke(cli, ["platform", "logout"])
            assert result.exit_code == 0
            assert "Successfully logged out." in normalize_output(result.output)
            result = runner.invoke(cli, ["platform", "whoami"])
            assert result.exit_code == 0
            assert "https://aignostics-platform.eu.auth0.com/" in normalize_output(result.output)

    @staticmethod
    def test_logout_success(runner: CliRunner) -> None:
        """Test successful logout command."""
        with patch("aignostics.platform._service.Service.logout", return_value=True):
            result = runner.invoke(cli, ["platform", "logout"])

            assert result.exit_code == 0
            assert "Successfully logged out." in normalize_output(result.output)

    @staticmethod
    def test_logout_not_logged_in(runner: CliRunner) -> None:
        """Test logout command when not logged in."""
        with patch("aignostics.platform._service.Service.logout", return_value=False):
            result = runner.invoke(cli, ["platform", "logout"])

            assert result.exit_code == 2
            assert "Was not logged in." in normalize_output(result.output)

    @staticmethod
    def test_logout_error(runner: CliRunner) -> None:
        """Test logout command when an error occurs."""
        with patch("aignostics.platform._service.Service.logout", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["platform", "logout"])

            assert result.exit_code == 1
            assert "Error during logout: Test error" in normalize_output(result.output)

    @staticmethod
    def test_login_success(runner: CliRunner) -> None:
        """Test successful login command."""
        with patch("aignostics.platform._service.Service.login", return_value=True):
            result = runner.invoke(cli, ["platform", "login"])

            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)

    @staticmethod
    def test_login_with_relogin_flag(runner: CliRunner) -> None:
        """Test login command with relogin flag."""
        with patch("aignostics.platform._service.Service.login", return_value=True) as mock_login:
            result = runner.invoke(cli, ["platform", "login", "--relogin"])

            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)
            mock_login.assert_called_once_with(relogin=True)

    @staticmethod
    def test_login_failure(runner: CliRunner) -> None:
        """Test login command when login fails."""
        with patch("aignostics.platform._service.Service.login", return_value=False):
            result = runner.invoke(cli, ["platform", "login"])

            assert result.exit_code == 1
            assert "Failed to log in" in normalize_output(result.output)

    @staticmethod
    def test_login_error(runner: CliRunner) -> None:
        """Test login command when an error occurs."""
        with patch("aignostics.platform._service.Service.login", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["platform", "login"])

            assert result.exit_code == 1
            assert "Error during login: Test error" in normalize_output(result.output)

    @staticmethod
    def test_whoami_success(runner: CliRunner) -> None:
        """Test successful whoami command."""
        # Create mock user info
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope="openid profile",
            audience="test-audience",
            authorized_party="test-client-id",
        )
        mock_user_info = UserInfo(
            id="user123",
            org_id="org456",
            role="admin",
            token=mock_token_info,
        )

        with patch("aignostics.platform._service.Service.get_user_info", return_value=mock_user_info):
            result = runner.invoke(cli, ["platform", "whoami"])

            assert result.exit_code == 0
            # Check that JSON output contains expected fields
            output = normalize_output(result.output)
            assert "user123" in output
            assert "org456" in output
            assert "admin" in output

    @staticmethod
    def test_whoami_with_relogin_flag(runner: CliRunner) -> None:
        """Test whoami command with relogin flag."""
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope="openid profile",
            audience="test-audience",
            authorized_party="test-client-id",
        )
        mock_user_info = UserInfo(
            id="user123",
            org_id="org456",
            role="admin",
            token=mock_token_info,
        )

        with patch(
            "aignostics.platform._service.Service.get_user_info", return_value=mock_user_info
        ) as mock_get_user_info:
            result = runner.invoke(cli, ["platform", "whoami", "--relogin"])

            assert result.exit_code == 0
            mock_get_user_info.assert_called_once_with(relogin=True)

    @staticmethod
    def test_whoami_not_logged_in(runner: CliRunner) -> None:
        """Test whoami command when not logged in."""
        with patch("aignostics.platform._service.Service.get_user_info", return_value=None):
            result = runner.invoke(cli, ["platform", "whoami"])

            assert result.exit_code == 1
            assert "You are not logged in." in normalize_output(result.output)

    @staticmethod
    def test_whoami_error(runner: CliRunner) -> None:
        """Test whoami command when an error occurs."""
        with patch("aignostics.platform._service.Service.get_user_info", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["platform", "whoami"])

            assert result.exit_code == 1
            assert "Error while determining who you are: Test error" in normalize_output(result.output)
