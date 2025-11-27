"""Tests for authentication settings module."""

import os
from pathlib import Path
from unittest import mock

import pytest
from pydantic import SecretStr
from pydantic import ValidationError as PydanticValidationError

from aignostics.platform import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    AUDIENCE_DEV,
    AUDIENCE_PRODUCTION,
    AUDIENCE_STAGING,
    AUTHORIZATION_BASE_URL_DEV,
    AUTHORIZATION_BASE_URL_PRODUCTION,
    AUTHORIZATION_BASE_URL_STAGING,
    CLIENT_ID_INTERACTIVE_DEV,
    CLIENT_ID_INTERACTIVE_PRODUCTION,
    CLIENT_ID_INTERACTIVE_STAGING,
    DEVICE_URL_DEV,
    DEVICE_URL_PRODUCTION,
    DEVICE_URL_STAGING,
    JWS_JSON_URL_DEV,
    JWS_JSON_URL_PRODUCTION,
    JWS_JSON_URL_STAGING,
    REDIRECT_URI_DEV,
    REDIRECT_URI_PRODUCTION,
    REDIRECT_URI_STAGING,
    TOKEN_URL_DEV,
    TOKEN_URL_PRODUCTION,
    TOKEN_URL_STAGING,
    UNKNOWN_ENDPOINT_URL,
    Settings,
    settings,
)
from aignostics.utils import __project_name__


@pytest.fixture
def mock_env_vars():  # noqa: ANN201
    """Mock environment variable for testing of settings."""
    with mock.patch.dict(
        os.environ,
        {
            f"{__project_name__.upper()}_CLIENT_ID_DEVICE": "test-client-id-device",
        },
    ):
        yield


@pytest.fixture
def reset_cached_settings():  # noqa: ANN201
    """Reset the cached authentication settings."""
    from aignostics.platform._settings import __cached_settings

    # Store original
    original = __cached_settings

    settings.__cached_settings = None

    yield

    # Restore original
    settings.__cached_settings = original


@pytest.mark.unit
def test_authentication_settings_production(record_property) -> None:
    """Test authentication settings with production API root."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    # Create settings with production API root
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root=API_ROOT_PRODUCTION,
    )

    # Validate production-specific settings
    assert settings.api_root == API_ROOT_PRODUCTION
    assert settings.client_id_interactive == CLIENT_ID_INTERACTIVE_PRODUCTION
    assert settings.client_id_device.get_secret_value() == "test-client-id-device"
    assert settings.audience == AUDIENCE_PRODUCTION
    assert settings.authorization_base_url == AUTHORIZATION_BASE_URL_PRODUCTION
    assert settings.token_url == TOKEN_URL_PRODUCTION
    assert settings.redirect_uri == REDIRECT_URI_PRODUCTION
    assert settings.device_url == DEVICE_URL_PRODUCTION
    assert settings.jws_json_url == JWS_JSON_URL_PRODUCTION


@pytest.mark.unit
def test_authentication_settings_staging(record_property, mock_env_vars) -> None:
    """Test authentication settings with staging API root."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root=API_ROOT_STAGING,
    )

    assert settings.api_root == API_ROOT_STAGING
    assert settings.client_id_interactive == CLIENT_ID_INTERACTIVE_STAGING
    assert settings.client_id_device.get_secret_value() == "test-client-id-device"
    assert settings.audience == AUDIENCE_STAGING
    assert settings.authorization_base_url == AUTHORIZATION_BASE_URL_STAGING
    assert settings.token_url == TOKEN_URL_STAGING
    assert settings.redirect_uri == REDIRECT_URI_STAGING
    assert settings.device_url == DEVICE_URL_STAGING
    assert settings.jws_json_url == JWS_JSON_URL_STAGING


@pytest.mark.unit
def test_authentication_settings_dev(record_property, mock_env_vars) -> None:
    """Test authentication settings with dev API root."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root=API_ROOT_DEV,
    )

    assert settings.api_root == API_ROOT_DEV
    assert settings.client_id_interactive == CLIENT_ID_INTERACTIVE_DEV
    assert settings.client_id_device.get_secret_value() == "test-client-id-device"
    assert settings.audience == AUDIENCE_DEV
    assert settings.authorization_base_url == AUTHORIZATION_BASE_URL_DEV
    assert settings.token_url == TOKEN_URL_DEV
    assert settings.redirect_uri == REDIRECT_URI_DEV
    assert settings.device_url == DEVICE_URL_DEV
    assert settings.jws_json_url == JWS_JSON_URL_DEV


@pytest.mark.unit
def test_authentication_settings_unknown_api_root(record_property, mock_env_vars) -> None:
    """Test authentication settings with unknown API root raises ValueError."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    with pytest.raises(ValueError, match=UNKNOWN_ENDPOINT_URL):
        Settings(
            api_root="https://unknown.example.com",
        )


@pytest.mark.unit
def test_scope_elements_empty_fails_validation(record_property) -> None:
    """Test scope_elements property with empty scope fails validation."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    with pytest.raises(PydanticValidationError, match="String should have at least 3 characters"):
        Settings(
            scope="",
            api_root=API_ROOT_PRODUCTION,
        )


@pytest.mark.unit
def test_scope_elements_multiple(record_property) -> None:
    """Test scope_elements property with multiple scopes."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        scope="offline_access, profile, email",
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.scope_elements == ["offline_access", "profile", "email"]


@pytest.mark.unit
def test_authentication_settings_with_refresh_token(record_property, mock_env_vars) -> None:
    """Test authentication settings with refresh token."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        refresh_token=SecretStr("test-refresh-token"),
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.refresh_token == SecretStr("test-refresh-token")


@pytest.mark.unit
def test_lazy_authentication_settings(record_property, mock_env_vars, reset_cached_settings) -> None:
    """Test lazy loading of authentication settings."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    # First call should create the settings
    settings1 = settings()
    assert settings1 is not None

    # Second call should return the same instance
    settings2 = settings()
    assert settings2 is settings1


@pytest.mark.unit
@pytest.mark.sequential
def test_authentication_settings_with_env_vars(record_property, mock_env_vars, reset_cached_settings) -> None:
    """Test authentication settings from environment variables."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings1 = settings()
    assert settings1.client_id_device.get_secret_value() == "test-client-id-device"


@pytest.mark.unit
def test_custom_env_file_location(reset_cached_settings, record_property) -> None:
    """Test custom env file location.

    This test verifies that a custom env file can be specified via the AIGNOSTICS_ENV_FILE
    environment variable and that Settings will load from that file. The test uses a context
    manager to ensure proper cleanup of the temporary env file.

    Note: This test uses health_timeout instead of client_id_device because in CI environments,
    the AIGNOSTICS_CLIENT_ID_DEVICE environment variable takes precedence over env file values
    (as per pydantic-settings priority). The health_timeout field is less likely to be set
    in CI environments.
    """
    import sys
    import tempfile
    from contextlib import contextmanager

    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")

    settings_module = "aignostics.platform._settings"

    @contextmanager
    def temp_env_file(content: str):  # type: ignore[misc]
        """Context manager for creating a temporary env file that's cleaned up automatically.

        Args:
            content: The content to write to the temporary env file.

        Yields:
            str: The path to the temporary env file.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name
        try:
            yield temp_path
        finally:
            Path(temp_path).unlink(missing_ok=True)

    # Create a temporary env file with test settings
    with temp_env_file("AIGNOSTICS_HEALTH_TIMEOUT=42.5\n") as custom_env_file:
        # Set the custom env file location BEFORE importing Settings
        # This requires reimporting the module to pick up the new env var
        # Clear ALL AIGNOSTICS_ environment variables to ensure clean state
        env_patch = {k: v for k, v in os.environ.items() if not k.startswith(f"{__project_name__.upper()}_")}

        # Now set only the variables we want for this test
        env_patch[f"{__project_name__.upper()}_ENV_FILE"] = custom_env_file

        try:
            with mock.patch.dict(os.environ, env_patch, clear=True):
                # Remove the module from sys.modules to force reimport
                if settings_module in sys.modules:
                    del sys.modules[settings_module]

                # Now import Settings fresh - it should read from the custom env file
                from aignostics.platform._settings import Settings

                assert custom_env_file in Settings.model_config["env_file"]
                test_settings = Settings()
                assert test_settings.health_timeout == pytest.approx(42.5)
        finally:
            # Restore the original module state by deleting it so it gets reimported fresh next time
            if settings_module in sys.modules:
                del sys.modules[settings_module]


@pytest.mark.unit
def test_custom_cache_dir(record_property, mock_env_vars) -> None:
    """Test custom cache directory."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    custom_cache_dir = "/home/dummy/test_cache_dir"
    settings = Settings(
        cache_dir=custom_cache_dir,
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.cache_dir == custom_cache_dir
    assert settings.token_file == Path(custom_cache_dir) / ".token"


@pytest.mark.unit
def test_issuer_computed_field_production(record_property, mock_env_vars) -> None:
    """Test issuer computed field with production authorization base URL."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        api_root=API_ROOT_PRODUCTION,
    )
    # Production authorization_base_url is https://aignostics-platform.eu.auth0.com/authorize
    # So issuer should be https://aignostics-platform.eu.auth0.com/
    expected_issuer = "https://aignostics-platform.eu.auth0.com/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_staging(record_property, mock_env_vars) -> None:
    """Test issuer computed field with staging authorization base URL."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        api_root=API_ROOT_STAGING,
    )
    # Staging authorization_base_url is https://todo (placeholder)
    # So issuer should be https://todo/
    expected_issuer = "https://aignostics-platform-staging.eu.auth0.com/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_dev(record_property, mock_env_vars) -> None:
    """Test issuer computed field with dev authorization base URL."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        api_root=API_ROOT_DEV,
    )
    # Dev authorization_base_url is https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize
    # So issuer should be https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/
    expected_issuer = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_profile_edit_url_computed_field_production(record_property, mock_env_vars) -> None:
    """Test profile_edit_url computed field with production API root."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        api_root=API_ROOT_PRODUCTION,
    )
    expected_url = f"{API_ROOT_PRODUCTION}/dashboard/account/profile"
    assert settings.profile_edit_url == expected_url


@pytest.mark.unit
def test_profile_edit_url_computed_field_staging(record_property, mock_env_vars) -> None:
    """Test profile_edit_url computed field with staging API root."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        api_root=API_ROOT_STAGING,
    )
    expected_url = f"{API_ROOT_STAGING}/dashboard/account/profile"
    assert settings.profile_edit_url == expected_url


@pytest.mark.unit
def test_profile_edit_url_computed_field_dev(record_property, mock_env_vars) -> None:
    """Test profile_edit_url computed field with dev API root."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        api_root=API_ROOT_DEV,
    )
    expected_url = f"{API_ROOT_DEV}/dashboard/account/profile"
    assert settings.profile_edit_url == expected_url


@pytest.mark.unit
def test_issuer_computed_field_custom_url(record_property, mock_env_vars) -> None:
    """Test issuer computed field with custom authorization base URL."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    # Avoid triggering api_root-based validator by setting all required fields manually
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        client_id_interactive="test-client-id-interactive",
        authorization_base_url="https://custom.example.com/auth/oauth2/authorize",
        audience="test-audience",
        token_url="https://custom.example.com/auth/oauth2/token",  # noqa: S106
        redirect_uri="https://custom.example.com/callback",
        device_url="https://custom.example.com/auth/oauth2/device",
        jws_json_url="https://custom.example.com/auth/.well-known/jwks.json",
    )
    expected_issuer = "https://custom.example.com/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_malformed_url_no_scheme(record_property, mock_env_vars) -> None:
    """Test issuer computed field with malformed URL (no scheme) falls back gracefully."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        client_id_interactive="test-client-id-interactive",
        authorization_base_url="example.com/oauth2/auth",
        audience="test-audience",
        token_url="https://example.com/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/oauth2/device",
        jws_json_url="https://example.com/.well-known/jwks.json",
    )
    # Should fall back to rsplit logic which removes the last path segment
    expected_issuer = "example.com/oauth2/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_malformed_url_no_domain(record_property, mock_env_vars) -> None:
    """Test issuer computed field with malformed URL (no domain) falls back gracefully."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        client_id_interactive="test-client-id-interactive",
        authorization_base_url="https:///oauth2/auth",
        audience="test-audience",
        token_url="https://example.com/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/oauth2/device",
        jws_json_url="https://example.com/.well-known/jwks.json",
    )
    # Should fall back to rsplit logic which removes the last path segment
    expected_issuer = "https:///oauth2/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_url_with_port(record_property, mock_env_vars) -> None:
    """Test issuer computed field with URL containing port number."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        client_id_interactive="test-client-id-interactive",
        authorization_base_url="https://localhost:8080/oauth2/auth",
        audience="test-audience",
        token_url="https://localhost:8080/oauth2/token",  # noqa: S106
        redirect_uri="https://localhost:8080/callback",
        device_url="https://localhost:8080/oauth2/device",
        jws_json_url="https://localhost:8080/.well-known/jwks.json",
    )
    expected_issuer = "https://localhost:8080/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_url_with_subdirectory(record_property, mock_env_vars) -> None:
    """Test issuer computed field with URL containing multiple path segments."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        client_id_interactive="test-client-id-interactive",
        authorization_base_url="https://example.com/auth/v1/oauth2/authorize",
        audience="test-audience",
        token_url="https://example.com/auth/v1/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/auth/v1/oauth2/device",
        jws_json_url="https://example.com/auth/v1/.well-known/jwks.json",
    )
    expected_issuer = "https://example.com/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_issuer_computed_field_url_with_query_params(record_property, mock_env_vars) -> None:
    """Test issuer computed field with URL containing query parameters."""
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        client_id_interactive="test-client-id-interactive",
        authorization_base_url="https://example.com/oauth2/auth?param=value",
        audience="test-audience",
        token_url="https://example.com/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/oauth2/device",
        jws_json_url="https://example.com/.well-known/jwks.json",
    )
    expected_issuer = "https://example.com/"
    assert settings.issuer == expected_issuer


@pytest.mark.unit
def test_validate_retry_wait_times_valid(mock_env_vars) -> None:
    """Test that valid retry wait times pass validation."""
    settings = Settings(
        api_root=API_ROOT_PRODUCTION,
        auth_retry_wait_min=0.1,
        auth_retry_wait_max=5.0,
    )
    assert settings.auth_retry_wait_min == 0.1
    assert settings.auth_retry_wait_max == 5.0


@pytest.mark.unit
def test_validate_retry_wait_times_min_equals_max(mock_env_vars) -> None:
    """Test that retry wait min equal to max passes validation."""
    settings = Settings(
        api_root=API_ROOT_PRODUCTION,
        auth_retry_wait_min=3.0,
        auth_retry_wait_max=3.0,
    )
    assert settings.auth_retry_wait_min == 3.0
    assert settings.auth_retry_wait_max == 3.0


@pytest.mark.unit
def test_validate_retry_wait_times_min_greater_than_max(mock_env_vars) -> None:
    """Test that retry wait min greater than max fails validation."""
    with pytest.raises(
        PydanticValidationError,
        match=r"auth_retry_wait_min \(10\.0\) must be less or equal than auth_retry_wait_max \(5.0\)",
    ):
        Settings(
            api_root=API_ROOT_PRODUCTION,
            auth_retry_wait_min=10.0,
            auth_retry_wait_max=5.0,
        )
