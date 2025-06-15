"""Tests to verify the CLI functionality of the platform module."""

from datetime import UTC, datetime
from unittest.mock import patch

from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.platform._service import TokenInfo, UserInfo, UserProfile
from tests.conftest import normalize_output


class TestUserProfile:
    """Test cases for UserProfile model."""

    @staticmethod
    def test_user_profile_from_userinfo_full_data() -> None:
        """Test UserProfile creation from complete userinfo."""
        userinfo = {
            "name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "nickname": "johnny",
            "email": "john.doe@example.com",
            "email_verified": True,
            "picture": "https://example.com/avatar.jpg",
            "updated_at": "2024-01-15T10:30:00Z",
        }

        profile = UserProfile.from_userinfo(userinfo)

        assert profile.name == "John Doe"
        assert profile.given_name == "John"
        assert profile.family_name == "Doe"
        assert profile.nickname == "johnny"
        assert profile.email == "john.doe@example.com"
        assert profile.email_verified is True
        assert profile.picture == "https://example.com/avatar.jpg"
        # Pydantic automatically converts the ISO string to a datetime object
        assert profile.updated_at == datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

    @staticmethod
    def test_user_profile_from_userinfo_partial_data() -> None:
        """Test UserProfile creation from partial userinfo."""
        userinfo = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "email_verified": False,
        }

        profile = UserProfile.from_userinfo(userinfo)

        assert profile.name == "Jane Smith"
        assert profile.given_name is None
        assert profile.family_name is None
        assert profile.nickname is None
        assert profile.email == "jane.smith@example.com"
        assert profile.email_verified is False
        assert profile.picture is None
        assert profile.updated_at is None

    @staticmethod
    def test_user_profile_from_userinfo_empty_data() -> None:
        """Test UserProfile creation from empty userinfo."""
        userinfo = {}

        profile = UserProfile.from_userinfo(userinfo)

        assert profile.name is None
        assert profile.given_name is None
        assert profile.family_name is None
        assert profile.nickname is None
        assert profile.email is None
        assert profile.email_verified is None
        assert profile.picture is None
        assert profile.updated_at is None


class TestTokenInfo:
    """Test cases for TokenInfo model."""

    @staticmethod
    def test_token_info_from_claims() -> None:
        """Test TokenInfo creation from JWT claims."""
        claims = {
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile email",
            "aud": "test-audience",
            "azp": "test-client-id",
        }

        token_info = TokenInfo.from_claims(claims)

        assert token_info.issuer == "https://test.auth0.com/"
        assert token_info.issued_at == 1609459200
        assert token_info.expires_at == 1609462800
        assert token_info.scope == ["openid", "profile", "email"]
        assert token_info.audience == ["test-audience"]
        assert token_info.authorized_party == "test-client-id"

    @staticmethod
    def test_token_info_from_claims_with_audience_list() -> None:
        """Test TokenInfo creation from JWT claims with audience as list."""
        claims = {
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile",
            "aud": ["audience1", "audience2"],
            "azp": "test-client-id",
        }

        token_info = TokenInfo.from_claims(claims)

        assert token_info.audience == ["audience1", "audience2"]


class TestUserInfo:
    """Test cases for UserInfo model."""

    @staticmethod
    def test_user_info_from_claims_and_userinfo_with_profile() -> None:
        """Test UserInfo creation with both claims and userinfo."""
        claims = {
            "sub": "user123",
            "org_id": "org456",
            "org_name": "Test Organization",
            "https://aignostics-platform-samia/role": "admin",
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile",
            "aud": "test-audience",
            "azp": "test-client-id",
        }
        userinfo = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "email_verified": True,
        }

        user_info = UserInfo.from_claims_and_userinfo(claims, userinfo)

        assert user_info.id == "user123"
        assert user_info.org_id == "org456"
        assert user_info.org_name == "Test Organization"
        assert user_info.role == "admin"
        assert user_info.token.issuer == "https://test.auth0.com/"
        assert user_info.profile is not None
        assert user_info.profile.name == "John Doe"
        assert user_info.profile.email == "john.doe@example.com"
        assert user_info.profile.email_verified is True

    @staticmethod
    def test_user_info_from_claims_and_userinfo_without_profile() -> None:
        """Test UserInfo creation with only claims, no userinfo."""
        claims = {
            "sub": "user456",
            "org_id": "org789",
            "org_name": "Another Organization",
            "https://aignostics-platform-samia/role": "user",
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid",
            "aud": "test-audience",
            "azp": "test-client-id",
        }

        user_info = UserInfo.from_claims_and_userinfo(claims, None)

        assert user_info.id == "user456"
        assert user_info.org_id == "org789"
        assert user_info.org_name == "Another Organization"
        assert user_info.role == "user"
        assert user_info.token.issuer == "https://test.auth0.com/"
        assert user_info.profile is None

    @staticmethod
    def test_user_info_from_claims_and_userinfo_no_org_name() -> None:
        """Test UserInfo creation when org_name is not provided in claims."""
        claims = {
            "sub": "user789",
            "org_id": "org999",
            "https://aignostics-platform-samia/role": "viewer",
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid",
            "aud": "test-audience",
            "azp": "test-client-id",
        }

        user_info = UserInfo.from_claims_and_userinfo(claims, None)

        assert user_info.id == "user789"
        assert user_info.org_id == "org999"
        assert user_info.org_name is None
        assert user_info.role == "viewer"
        assert user_info.token.issuer == "https://test.auth0.com/"
        assert user_info.profile is None


class TestPlatformCLI:
    """Test cases for platform CLI commands."""

    @staticmethod
    def test_login_out_info_e2e(runner: CliRunner) -> None:
        """Test successful logout command."""
        with patch("aignostics.platform._service.Service.logout", return_value=True):
            result = runner.invoke(cli, ["user", "login", "--relogin"])
            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)
            result = runner.invoke(cli, ["user", "logout"])
            assert result.exit_code == 0
            assert "Successfully logged out." in normalize_output(result.output)
            result = runner.invoke(cli, ["user", "whoami"])
            assert result.exit_code == 0
            assert "https://aignostics-platform.eu.auth0.com/" in normalize_output(result.output)

    @staticmethod
    def test_logout_success(runner: CliRunner) -> None:
        """Test successful logout command."""
        with patch("aignostics.platform._service.Service.logout", return_value=True):
            result = runner.invoke(cli, ["user", "logout"])

            assert result.exit_code == 0
            assert "Successfully logged out." in normalize_output(result.output)

    @staticmethod
    def test_logout_not_logged_in(runner: CliRunner) -> None:
        """Test logout command when not logged in."""
        with patch("aignostics.platform._service.Service.logout", return_value=False):
            result = runner.invoke(cli, ["user", "logout"])

            assert result.exit_code == 2
            assert "Was not logged in." in normalize_output(result.output)

    @staticmethod
    def test_logout_error(runner: CliRunner) -> None:
        """Test logout command when an error occurs."""
        with patch("aignostics.platform._service.Service.logout", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["user", "logout"])

            assert result.exit_code == 1
            assert "Error during logout: Test error" in normalize_output(result.output)

    @staticmethod
    def test_login_success(runner: CliRunner) -> None:
        """Test successful login command."""
        with patch("aignostics.platform._service.Service.login", return_value=True):
            result = runner.invoke(cli, ["user", "login"])

            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)

    @staticmethod
    def test_login_with_relogin_flag(runner: CliRunner) -> None:
        """Test login command with relogin flag."""
        with patch("aignostics.platform._service.Service.login", return_value=True) as mock_login:
            result = runner.invoke(cli, ["user", "login", "--relogin"])

            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)
            mock_login.assert_called_once_with(relogin=True)

    @staticmethod
    def test_login_failure(runner: CliRunner) -> None:
        """Test login command when login fails."""
        with patch("aignostics.platform._service.Service.login", return_value=False):
            result = runner.invoke(cli, ["user", "login"])

            assert result.exit_code == 1
            assert "Failed to log you in" in normalize_output(result.output)

    @staticmethod
    def test_login_error(runner: CliRunner) -> None:
        """Test login command when an error occurs."""
        with patch("aignostics.platform._service.Service.login", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["user", "login"])

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
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
        )
        mock_user_info = UserInfo(
            id="user123",
            org_id="org456",
            org_name="Test Organization",
            role="admin",
            token=mock_token_info,
        )

        with patch("aignostics.platform._service.Service.get_user_info", return_value=mock_user_info):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 0
            # Check that JSON output contains expected fields
            output = normalize_output(result.output)
            assert "user123" in output
            assert "org456" in output
            assert "Test Organization" in output
            assert "admin" in output

    @staticmethod
    def test_whoami_with_relogin_flag(runner: CliRunner) -> None:
        """Test whoami command with relogin flag."""
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
        )
        mock_user_info = UserInfo(
            id="user123",
            org_id="org456",
            org_name="Test Organization",
            role="admin",
            token=mock_token_info,
        )

        with patch(
            "aignostics.platform._service.Service.get_user_info", return_value=mock_user_info
        ) as mock_get_user_info:
            result = runner.invoke(cli, ["user", "whoami", "--relogin"])

            assert result.exit_code == 0
            mock_get_user_info.assert_called_once_with(relogin=True)

    @staticmethod
    def test_whoami_not_logged_in(runner: CliRunner) -> None:
        """Test whoami command when not logged in."""
        with patch("aignostics.platform._service.Service.get_user_info", return_value=None):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 1
            assert "Failed to log you in." in normalize_output(result.output)

    @staticmethod
    def test_whoami_error(runner: CliRunner) -> None:
        """Test whoami command when an error occurs."""
        with patch("aignostics.platform._service.Service.get_user_info", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 1
            assert "Error while getting user info: Test error" in normalize_output(result.output)

    @staticmethod
    def test_whoami_success_with_user_profile(runner: CliRunner) -> None:
        """Test successful whoami command with complete user profile."""
        # Create mock token info
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile", "email"],
            audience=["test-audience"],
            authorized_party="test-client-id",
        )

        # Create mock user profile
        mock_user_profile = UserProfile(
            name="John Doe",
            given_name="John",
            family_name="Doe",
            nickname="johnny",
            email="john.doe@example.com",
            email_verified=True,
            picture="https://example.com/avatar.jpg",
            updated_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        )

        # Create mock user info with profile
        mock_user_info = UserInfo(
            id="user123",
            org_id="org456",
            org_name="Test Organization",
            role="admin",
            token=mock_token_info,
            profile=mock_user_profile,
        )

        with patch("aignostics.platform._service.Service.get_user_info", return_value=mock_user_info):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 0
            # Check that JSON output contains expected fields from both user info and profile
            output = normalize_output(result.output)
            assert "user123" in output
            assert "org456" in output
            assert "Test Organization" in output
            assert "admin" in output
            assert "John Doe" in output
            assert "john.doe@example.com" in output
            assert "johnny" in output

    @staticmethod
    def test_whoami_success_with_no_org_name(runner: CliRunner) -> None:
        """Test successful whoami command when org_name is None."""
        # Create mock token info
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
        )
        mock_user_info = UserInfo(
            id="user789",
            org_id="org999",
            org_name=None,
            role="viewer",
            token=mock_token_info,
        )

        with patch("aignostics.platform._service.Service.get_user_info", return_value=mock_user_info):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 0
            # Check that JSON output contains expected fields, org_name should be null
            output = normalize_output(result.output)
            assert "user789" in output
            assert "org999" in output
            assert "viewer" in output
            # org_name should be null in JSON output
            assert '"org_name": null' in output or '"org_name":null' in output
