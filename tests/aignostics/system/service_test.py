"""Tests of the system service."""

import os
from unittest import mock

import pytest

from aignostics.system._service import Service


@pytest.mark.timeout(15)
def test_is_token_valid() -> None:
    """Test that is_token_valid works correctly with environment variable."""
    # Set the environment variable for the test
    the_value = "the_value"
    with mock.patch.dict(os.environ, {"AIGNOSTICS_SYSTEM_TOKEN": the_value}):
        # Create a new service instance to pick up the environment variable
        service = Service()

        # Test with matching token
        assert service.is_token_valid(the_value) is True

        # Test with non-matching token
        assert service.is_token_valid("wrong-value") is False

        # Test with empty token
        assert service.is_token_valid("") is False


def test_is_token_valid_when_not_set() -> None:
    """Test that is_token_valid handles the case when no token is set."""
    # Ensure the environment variable is not set
    with mock.patch.dict(os.environ, {"AIGNOSTICS_SYSTEM_TOKEN": ""}, clear=True):
        # Create a new service instance with no token set
        service = Service()

        # Should return False for any token when no token is set
        assert service.is_token_valid("any-token") is False
        assert service.is_token_valid("") is False


def test_is_secret_key_word_boundary_matching_positive_cases() -> None:
    """Test that word boundary terms are correctly identified as secrets."""
    # Test cases where "id" appears as a whole word - should be detected
    secret_keys = [
        "id",  # Exact match
        "ID",  # Case insensitive
        "user_id",  # With underscore boundary
        "client-id",  # With hyphen boundary
        "session.id",  # With dot boundary
        "api id",  # With space boundary
        "id_token",  # At beginning with boundary
        "my_id",  # At end with boundary
        "test-id-value",  # In middle with boundaries
    ]

    for key in secret_keys:
        assert Service._is_secret_key(key), f"Expected '{key}' to be identified as a secret key"


def test_is_secret_key_word_boundary_matching_negative_cases() -> None:
    """Test that word boundary terms do not match partial words."""
    # Test cases where "id" appears as part of a larger word - should NOT be detected
    non_secret_keys = [
        "valid",  # Contains "id" but not as whole word
        "middle",  # Contains "id" but not as whole word
        "consideration",  # Contains "id" but not as whole word
        "video",  # Contains "id" but not as whole word
        "liquid",  # Contains "id" but not as whole word
        "hidden",  # Contains "id" but not as whole word
        "building",  # Contains "id" but not as whole word
        "provider",  # Contains "id" but not as whole word
    ]

    for key in non_secret_keys:
        assert not Service._is_secret_key(key), f"Expected '{key}' to NOT be identified as a secret key"


def test_is_secret_key_string_match_terms_positive_cases() -> None:
    """Test that string match terms are correctly identified as secrets."""
    # Test all string match terms in various forms
    secret_keys = [
        # Direct matches
        "auth",
        "bearer",
        "cert",
        "credential",
        "hash",
        "jwt",
        "key",
        "nonce",
        "oauth",
        "password",
        "private",
        "salt",
        "secret",
        "seed",
        "session",
        "signature",
        "token",
        # Case variations
        "AUTH",
        "Bearer",
        "CERT",
        "PASSWORD",
        "SECRET",
        "TOKEN",
        # As part of larger keys
        "api_key",
        "auth_token",
        "bearer_token",
        "client_secret",
        "jwt_token",
        "oauth_client",
        "password_hash",
        "private_key",
        "session_id",
        "signature_method",
        "salt_value",
        "credential_store",
        "nonce_value",
        "certificate_path",
        "seed_data",
        # With prefixes/suffixes
        "my_password",
        "user_secret",
        "app_token",
        "service_key",
        "auth_header",
        "token_expires",
        "secret_config",
        "key_store",
        "private_data",
        # Mixed case and separators
        "API-KEY",
        "Auth_Token",
        "client.secret",
        "JWT-TOKEN",
        "oauth.client",
        "Password_Hash",
        "Private-Key",
        "session.token",
        "signature_key",
    ]

    for key in secret_keys:
        assert Service._is_secret_key(key), f"Expected '{key}' to be identified as a secret key"


def test_is_secret_key_string_match_terms_edge_cases() -> None:
    """Test edge cases for string matching."""
    # Test that partial matches work correctly
    edge_cases = [
        "keychain",  # Contains "key"
        "authentication",  # Contains "auth"
        "tokensystem",  # Contains "token"
        "secretive",  # Contains "secret"
        "passwords",  # Contains "password"
        "authorization",  # Contains "auth"
        "tokenize",  # Contains "token"
    ]

    for key in edge_cases:
        assert Service._is_secret_key(key), f"Expected '{key}' to be identified as a secret key"


def test_is_secret_key_non_secret_keys() -> None:
    """Test that non-secret keys are correctly identified as non-secrets."""
    non_secret_keys = [
        # Regular configuration keys
        "database_host",
        "database_port",
        "debug_mode",
        "log_level",
        "timeout",
        "max_connections",
        "cache_size",
        "version",
        # Common non-secret environment variables
        "PATH",
        "HOME",
        "USER",
        "SHELL",
        "TERM",
        "LANG",
        "TZ",
        # Application configuration
        "app_name",
        "app_version",
        "environment",
        "region",
        "zone",
        "feature_flags",
        "maintenance_mode",
        "backup_enabled",
        # Empty and special characters
        "",
        "   ",
        "123",
        "test",
        "config",
        "setting",
        # Common non-secret keys
        "description",
        "title",
        "name",
        "value",
        "data",
        "public_url",
        "base_url",
        "static_path",
        "upload_path",
    ]

    for key in non_secret_keys:
        assert not Service._is_secret_key(key), f"Expected '{key}' to NOT be identified as a secret key"


def test_is_secret_key_case_insensitivity() -> None:
    """Test that the method is case insensitive."""
    test_cases = [
        ("PASSWORD", True),
        ("password", True),
        ("Password", True),
        ("PaSsWoRd", True),
        ("SECRET", True),
        ("secret", True),
        ("Secret", True),
        ("SeCrEt", True),
        ("ID", True),
        ("id", True),
        ("Id", True),
        ("iD", True),
    ]

    for key, expected in test_cases:
        result = Service._is_secret_key(key)
        assert result == expected, f"Expected _is_secret_key('{key}') to return {expected}, got {result}"


def test_is_secret_key_special_characters_and_boundaries() -> None:
    """Test handling of special characters and word boundaries."""
    test_cases = [
        # Word boundary cases for "id"
        ("_id_", True),  # Surrounded by underscores
        ("-id-", True),  # Surrounded by hyphens
        (".id.", True),  # Surrounded by dots
        (" id ", True),  # Surrounded by spaces
        ("(id)", True),  # Surrounded by parentheses
        ("[id]", True),  # Surrounded by brackets
        ("{id}", True),  # Surrounded by braces
        # Non-boundary cases for "id"
        ("abidcd", False),  # Embedded in letters
        ("123id456", True),  # Numbers are word boundaries
        # String match terms with special characters
        ("api-key-value", True),  # Contains "key"
        ("user@password", True),  # Contains "password"
        ("jwt#token", True),  # Contains "token"
        ("secret$value", True),  # Contains "secret"
    ]

    for key, expected in test_cases:
        result = Service._is_secret_key(key)
        assert result == expected, f"Expected _is_secret_key('{key}') to return {expected}, got {result}"


def test_is_secret_key_empty_and_none_like_inputs() -> None:
    """Test edge cases with empty or minimal inputs."""
    test_cases = [
        ("", False),  # Empty string
        ("   ", False),  # Whitespace only
        ("a", False),  # Single character
        ("ab", False),  # Two characters
    ]

    for key, expected in test_cases:
        result = Service._is_secret_key(key)
        assert result == expected, f"Expected _is_secret_key('{key}') to return {expected}, got {result}"


def test_is_secret_key_real_world_examples() -> None:
    """Test with real-world examples of environment variable names."""
    # Common secret environment variables (should return True)
    secret_examples = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "DATABASE_PASSWORD",
        "REDIS_PASSWORD",
        "JWT_SECRET",
        "API_KEY",
        "OAUTH_CLIENT_SECRET",
        "STRIPE_SECRET_KEY",
        "GITHUB_TOKEN",
        "DOCKER_HUB_PASSWORD",
        "SSL_PRIVATE_KEY",
        "ENCRYPTION_KEY",
        "SESSION_SECRET",
        "WEBHOOK_SIGNATURE_SECRET",
        "BASIC_AUTH_PASSWORD",
        "CERTIFICATE_KEY",
        "SIGNING_KEY",
        "MASTER_KEY",
        "CLIENT_CREDENTIALS",
        "BEARER_TOKEN",
        "ACCESS_TOKEN",
    ]

    # Common non-secret environment variables (should return False)
    non_secret_examples = [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "REDIS_HOST",
        "REDIS_PORT",
        "LOG_LEVEL",
        "DEBUG",
        "ENVIRONMENT",
        "NODE_ENV",
        "PORT",
        "TIMEOUT",
        "MAX_CONNECTIONS",
        "CACHE_TTL",
        "RETRY_COUNT",
        "BASE_URL",
        "PUBLIC_URL",
        "STATIC_PATH",
        "UPLOAD_PATH",
        "DEFAULT_LOCALE",
        "TIMEZONE",
        "VERSION",
        "BUILD_NUMBER",
        "FEATURE_FLAG_X",
        "MAINTENANCE_MODE",
        "BACKUP_ENABLED",
    ]

    for key in secret_examples:
        assert Service._is_secret_key(key), f"Expected '{key}' to be identified as a secret key"

    for key in non_secret_examples:
        assert not Service._is_secret_key(key), f"Expected '{key}' to NOT be identified as a secret key"
