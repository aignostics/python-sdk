"""Tests to verify the CLI functionality of the platform module."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics_sdk.platform import Me
from aignostics_sdk.platform._service import Organization, TokenInfo, User, UserInfo
from tests.conftest import normalize_output


class TestTokenInfo:
    """Test cases for TokenInfo model."""

    @pytest.mark.unit
    @staticmethod
    def test_token_info_from_claims(record_property) -> None:
        """Test TokenInfo creation from JWT claims."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        claims = {
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile email",
            "aud": "https://test-audience",
            "azp": "test-client-id",
            "org_id": "org123",
            "https://test-audience/role": "member",
        }

        token_info = TokenInfo.from_claims(claims)

        assert token_info.issuer == "https://test.auth0.com/"
        assert token_info.issued_at == 1609459200
        assert token_info.expires_at == 1609462800
        assert token_info.scope == ["openid", "profile", "email"]
        assert token_info.audience == ["https://test-audience"]
        assert token_info.authorized_party == "test-client-id"
        assert token_info.org_id == "org123"
        assert token_info.role == "member"

    @pytest.mark.unit
    @staticmethod
    def test_token_info_from_claims_with_audience_list(record_property) -> None:
        """Test TokenInfo creation from JWT claims with audience as list."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        claims = {
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile",
            "aud": ["https://test-audience1", "test-audience2"],
            "azp": "test-client-id",
            "org_id": "org123",
            "https://test-audience1": "member",
        }

        token_info = TokenInfo.from_claims(claims)

        assert token_info.audience == ["https://test-audience1", "test-audience2"]
        assert token_info.role == "member"

    @pytest.mark.unit
    @staticmethod
    def test_token_info_from_claims_without_role(record_property) -> None:
        """Test TokenInfo creation from JWT claims with role missing."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        claims = {
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile",
            "aud": ["https://test-audience1"],
            "azp": "test-client-id",
            "org_id": "org123",
        }

        token_info = TokenInfo.from_claims(claims)

        assert token_info.audience == ["https://test-audience1"]
        assert token_info.role == "member"


class TestUserInfo:
    """Test cases for UserInfo model."""

    @pytest.mark.unit
    @staticmethod
    def test_user_info_from_claims_and_userinfo_with_profile(record_property) -> None:
        """Test UserInfo creation with both claims and userinfo."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        claims = {
            "sub": "user123",
            "org_id": "org456",
            "org_name": "Test Organization",
            "https://aignostics-platform-samia/role": "admin",
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid profile",
            "aud": "https://test-audience1",
            "azp": "test-client-id",
        }
        me = Me(
            user=User(
                id="user123",
                name="John Doe",
                email="john.doe@example.com",
                email_verified=True,
            ),
            organization=Organization(
                id="org456",
                name="Test Organization",
                aignostics_bucket_hmac_access_key_id="secret_access_key_id",
                aignostics_bucket_hmac_secret_access_key="secret_access_key",  # noqa: S106
                aignostics_bucket_name="test-bucket",
                aignostics_bucket_protocol="gs",
                aignostics_logfire_token="logfire_token",  # noqa: S106
                aignostics_sentry_dsn="sentry_dsn",
            ),
        )

        user_info = UserInfo.from_claims_and_me(claims, me)

        assert user_info.user.id == "user123"
        assert user_info.user.name == "John Doe"
        assert user_info.user.email == "john.doe@example.com"
        assert user_info.user.email_verified is True
        assert user_info.organization.id == "org456"
        assert user_info.organization.name == "Test Organization"
        assert user_info.role == "member"
        assert user_info.token.issuer == "https://test.auth0.com/"

    @pytest.mark.unit
    @staticmethod
    def test_user_info_from_claims_and_userinfo_no_org_name(record_property) -> None:
        """Test UserInfo creation when org_name is not provided in claims."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        claims = {
            "sub": "user789",
            "org_id": "org999",
            "https://test-audience1/role": "viewer",
            "iss": "https://test.auth0.com/",
            "iat": 1609459200,
            "exp": 1609462800,
            "scope": "openid",
            "aud": "https://test-audience1",
            "azp": "test-client-id",
        }

        me = Me(
            user=User(
                id="user123",
                name="John Doe",
                email="john.doe@example.com",
                email_verified=True,
            ),
            organization=Organization(
                id="org456",
                aignostics_bucket_hmac_access_key_id="secret_access_key_id",
                aignostics_bucket_hmac_secret_access_key="secret_access_key",  # noqa: S106
                aignostics_bucket_name="test-bucket",
                aignostics_bucket_protocol="gs",
                aignostics_logfire_token="logfire_token",  # noqa: S106
                aignostics_sentry_dsn="sentry_dsn",
            ),
        )

        user_info = UserInfo.from_claims_and_me(claims, me)

        assert user_info.user.id == "user123"
        assert user_info.user.name == "John Doe"
        assert user_info.user.email == "john.doe@example.com"
        assert user_info.user.email_verified is True
        assert user_info.organization.id == "org456"
        assert user_info.organization.name is None
        assert user_info.role == "viewer"
        assert user_info.token.issuer == "https://test.auth0.com/"


class TestPlatformCLI:
    """Test cases for platform CLI commands."""

    @pytest.mark.e2e
    @staticmethod
    def test_login_out_info_e2e(record_property, runner: CliRunner) -> None:
        """Test successful logout command."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with (
            patch("aignostics.platform._service.Service.logout", return_value=True),
        ):
            result = runner.invoke(cli, ["user", "login", "--relogin"])
            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)
            result = runner.invoke(cli, ["user", "logout"])
            assert result.exit_code == 0
            assert "Successfully logged out." in normalize_output(result.output)
            result = runner.invoke(cli, ["user", "whoami"])
            assert result.exit_code == 0
            assert any(
                url in normalize_output(result.output)
                for url in [
                    "https://aignostics-platform.eu.auth0.com/",
                    "https://aignostics-platform-staging.eu.auth0.com/",
                    "dev-8ouohmmrbuh2h4vu.eu.auth0.com",
                ]
            )

    @pytest.mark.integration
    @staticmethod
    def test_logout_success(record_property, runner: CliRunner) -> None:
        """Test successful logout command."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.logout", return_value=True):
            result = runner.invoke(cli, ["user", "logout"])

            assert result.exit_code == 0
            assert "Successfully logged out." in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_logout_not_logged_in(record_property, runner: CliRunner) -> None:
        """Test logout command when not logged in."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.logout", return_value=False):
            result = runner.invoke(cli, ["user", "logout"])

            assert result.exit_code == 2
            assert "Was not logged in." in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_logout_error(record_property, runner: CliRunner) -> None:
        """Test logout command when an error occurs."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.logout", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["user", "logout"])

            assert result.exit_code == 1
            assert "Error during logout: Test error" in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_login_success(record_property, runner: CliRunner) -> None:
        """Test successful login command."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.login", return_value=True):
            result = runner.invoke(cli, ["user", "login"])

            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_login_with_relogin_flag(record_property, runner: CliRunner) -> None:
        """Test login command with relogin flag."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.login", return_value=True) as mock_login:
            result = runner.invoke(cli, ["user", "login", "--relogin"])

            assert result.exit_code == 0
            assert "Successfully logged in." in normalize_output(result.output)
            mock_login.assert_called_once_with(relogin=True)

    @pytest.mark.integration
    @staticmethod
    def test_login_failure(record_property, runner: CliRunner) -> None:
        """Test login command when login fails."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.login", return_value=False):
            result = runner.invoke(cli, ["user", "login"])

            assert result.exit_code == 1
            assert "Failed to log you in" in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_login_error(record_property, runner: CliRunner) -> None:
        """Test login command when an error occurs."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.login", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["user", "login"])

            assert result.exit_code == 1
            assert "Error during login: Test error" in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_whoami_success(record_property, runner: CliRunner) -> None:
        """Test successful whoami command."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        # Create mock user info
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["https://test-audience"],
            authorized_party="test-client-id",
            org_id="org456",
            role="admin",
        )
        mock_user = User(
            id="user123",
        )
        mock_organization = Organization(
            id="org456",
            name="Test Organization",
            aignostics_bucket_hmac_access_key_id="secret_access_key_id",
            aignostics_bucket_hmac_secret_access_key="secret_access_key",  # noqa: S106
            aignostics_bucket_name="test-bucket",
            aignostics_bucket_protocol="gs",
            aignostics_logfire_token="logfire_token",  # noqa: S106
            aignostics_sentry_dsn="sentry_dsn",
        )
        mock_user_info = UserInfo(
            role="admin",
            token=mock_token_info,
            user=mock_user,
            organization=mock_organization,
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

    @pytest.mark.integration
    @staticmethod
    def test_whoami_with_relogin_flag(record_property, runner: CliRunner) -> None:
        """Test whoami command with relogin flag."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
            org_id="org456",
            role="admin",
        )
        mock_user = User(
            id="user123",
        )
        mock_organization = Organization(
            id="org456",
            name="Test Organization",
            aignostics_bucket_hmac_access_key_id="secret_access_key_id",
            aignostics_bucket_hmac_secret_access_key="secret_access_key",  # noqa: S106
            aignostics_bucket_name="test-bucket",
            aignostics_bucket_protocol="gs",
            aignostics_logfire_token="logfire_token",  # noqa: S106
            aignostics_sentry_dsn="sentry_dsn",
        )
        mock_user_info = UserInfo(
            role="admin",
            token=mock_token_info,
            user=mock_user,
            organization=mock_organization,
        )

        with patch(
            "aignostics.platform._service.Service.get_user_info", return_value=mock_user_info
        ) as mock_get_user_info:
            result = runner.invoke(cli, ["user", "whoami", "--relogin"])

            assert result.exit_code == 0
            mock_get_user_info.assert_called_once_with(relogin=True)

    @pytest.mark.integration
    @staticmethod
    def test_whoami_not_logged_in(record_property, runner: CliRunner) -> None:
        """Test whoami command when not logged in."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch(
            "aignostics.platform._service.Service.get_user_info",
            side_effect=RuntimeError("Could not retrieve user info"),
        ):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 1
            assert "Error while getting user info: Could not retrieve user info" in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_whoami_error(record_property, runner: CliRunner) -> None:
        """Test whoami command when an error occurs."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with patch("aignostics.platform._service.Service.get_user_info", side_effect=RuntimeError("Test error")):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 1
            assert "Error while getting user info: Test error" in normalize_output(result.output)

    @pytest.mark.integration
    @staticmethod
    def test_whoami_success_with_no_org_name(record_property, runner: CliRunner) -> None:
        """Test successful whoami command when org_name is None."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        # Create mock token info
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
            org_id="org999",
            role="viewer",
        )
        mock_user = User(
            id="user789",
        )
        mock_organization = Organization(
            id="org999",
            name=None,
            aignostics_bucket_hmac_access_key_id="secret_access_key_id",
            aignostics_bucket_hmac_secret_access_key="secret_access_key",  # noqa: S106
            aignostics_bucket_name="test-bucket",
            aignostics_bucket_protocol="gs",
            aignostics_logfire_token="logfire_token",  # noqa: S106
            aignostics_sentry_dsn="sentry_dsn",
        )
        mock_user_info = UserInfo(
            role="viewer",
            token=mock_token_info,
            user=mock_user,
            organization=mock_organization,
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
            assert '"name": null' in output or '"name":null' in output

    @pytest.mark.integration
    @staticmethod
    def test_whoami_masks_secrets_by_default(record_property, runner: CliRunner) -> None:
        """Test that whoami masks secrets by default."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
            org_id="org456",
            role="admin",
        )
        mock_user = User(id="user123", email="nospam@aignostics.com")
        mock_organization = Organization(
            id="org456",
            name="Test Organization",
            aignostics_bucket_hmac_access_key_id="secret_access_key_id_123",
            aignostics_bucket_hmac_secret_access_key="very_secret_access_key_456",  # noqa: S106
            aignostics_bucket_name="test-bucket",
            aignostics_bucket_protocol="gs",
            aignostics_logfire_token="the_logfire_token",  # noqa: S106
            aignostics_sentry_dsn="sentry_dsn",
        )
        mock_user_info = UserInfo(
            role="admin",
            token=mock_token_info,
            user=mock_user,
            organization=mock_organization,
        )

        with patch("aignostics.platform._service.Service.get_user_info", return_value=mock_user_info):
            result = runner.invoke(cli, ["user", "whoami"])

            assert result.exit_code == 0
            output = normalize_output(result.output)
            # Check that secrets are masked with length
            assert "***MASKED(10)***" in output
            assert "***MASKED(17)***" in output
            assert "***MASKED(26)***" in output
            # Check that original secrets are not in output
            assert "nospam@aignostics.com" not in output
            assert "the_logfire_token" not in output
            assert "very_secret_access_key_456" not in output

    @pytest.mark.integration
    @staticmethod
    def test_whoami_shows_secrets_with_no_mask_flag(record_property, runner: CliRunner) -> None:
        """Test that whoami shows secrets when --no-mask-secrets flag is used."""
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        mock_token_info = TokenInfo(
            issuer="https://test.auth0.com/",
            issued_at=1609459200,
            expires_at=1609462800,
            scope=["openid", "profile"],
            audience=["test-audience"],
            authorized_party="test-client-id",
            org_id="org456",
            role="admin",
        )
        mock_user = User(id="user123")
        mock_organization = Organization(
            id="org456",
            name="Test Organization",
            aignostics_bucket_hmac_access_key_id="secret_access_key_id_123",
            aignostics_bucket_hmac_secret_access_key="very_secret_access_key_456",  # noqa: S106
            aignostics_bucket_name="test-bucket",
            aignostics_bucket_protocol="gs",
            aignostics_logfire_token="logfire_token",  # noqa: S106
            aignostics_sentry_dsn="sentry_dsn",
        )
        mock_user_info = UserInfo(
            role="admin",
            token=mock_token_info,
            user=mock_user,
            organization=mock_organization,
        )

        with patch("aignostics.platform._service.Service.get_user_info", return_value=mock_user_info):
            result = runner.invoke(cli, ["user", "whoami", "--no-mask-secrets"])

            assert result.exit_code == 0
            output = normalize_output(result.output)
            # Check that original secrets are shown
            assert "secret_access_key_id_123" in output
            assert "very_secret_access_key_456" in output
            # Check that masked values are not in output
            assert "***MASKED" not in output

    @pytest.mark.integration
    @staticmethod
    def test_sdk_run_metadata_schema_pretty(runner: CliRunner) -> None:
        """Test run-metadata-schema command with pretty output (default)."""
        result = runner.invoke(cli, ["sdk", "run-metadata-schema"])

        assert result.exit_code == 0
        output = normalize_output(result.output)
        # Check that schema contains expected top-level properties
        assert "schema_version" in output
        assert "submission" in output
        assert "user_agent" in output
        assert "SubmissionMetadata" in output
        assert "WorkflowMetadata" in output
        assert "SchedulingMetadata" in output

    @pytest.mark.integration
    @staticmethod
    def test_sdk_run_metadata_schema_no_pretty(runner: CliRunner) -> None:
        """Test run-metadata-schema command with --no-pretty flag."""
        result = runner.invoke(cli, ["sdk", "run-metadata-schema", "--no-pretty"])

        assert result.exit_code == 0
        # Don't normalize output for JSON parsing
        output = result.output
        # Check that schema contains expected top-level properties
        assert "schema_version" in output
        assert "submission" in output
        assert "user_agent" in output
        # In non-pretty mode, output should still be valid JSON
        import json

        # Try to parse the output as JSON (should not raise an error)
        try:
            # Find JSON in output (skip boot messages)
            json_start = output.find("{")
            if json_start >= 0:
                json.loads(output[json_start:])
            else:
                pytest.fail("No JSON found in output")
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    @pytest.mark.integration
    @staticmethod
    def test_sdk_item_metadata_schema_pretty(runner: CliRunner) -> None:
        """Test item-metadata-schema command with pretty output (default)."""
        result = runner.invoke(cli, ["sdk", "item-metadata-schema"])

        assert result.exit_code == 0
        output = normalize_output(result.output)
        # Check that schema contains expected top-level properties
        assert "schema_version" in output
        assert "platform_bucket" in output
        assert "PlatformBucketMetadata" in output
        assert "ItemSdkMetadata" in output

    @pytest.mark.integration
    @staticmethod
    def test_sdk_item_metadata_schema_no_pretty(runner: CliRunner) -> None:
        """Test item-metadata-schema command with --no-pretty flag."""
        result = runner.invoke(cli, ["sdk", "item-metadata-schema", "--no-pretty"])

        assert result.exit_code == 0
        # Don't normalize output for JSON parsing
        output = result.output
        # Check that schema contains expected top-level properties
        assert "schema_version" in output
        assert "platform_bucket" in output
        # In non-pretty mode, output should still be valid JSON
        import json

        # Try to parse the output as JSON (should not raise an error)
        try:
            # Find JSON in output (skip boot messages)
            json_start = output.find("{")
            if json_start >= 0:
                json.loads(output[json_start:])
            else:
                pytest.fail("No JSON found in output")
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
