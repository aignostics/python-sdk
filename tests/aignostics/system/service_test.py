"""Tests of the system service."""

import os
from typing import Any
from unittest import mock

import pytest

from aignostics.system._service import Service

# ---------------------------------------------------------------------------
# Helpers shared by uptime tests
# ---------------------------------------------------------------------------

FIXED_BOOT_TIME = 1_000_000.0  # arbitrary fixed epoch seconds


def _make_mock_process() -> mock.MagicMock:
    proc = mock.MagicMock()
    proc.username.return_value = "testuser"
    return proc


def _patch_info_dependencies(boot_time: float = FIXED_BOOT_TIME):
    """Return a context manager stack that patches all external I/O for Service.info()."""
    import contextlib

    now = boot_time + 3600.0  # pretend system has been up 1 hour

    vmem = mock.MagicMock()
    vmem.percent = 50.0
    vmem.total = 8_000_000_000
    vmem.available = 4_000_000_000
    vmem.used = 3_500_000_000
    vmem.free = 500_000_000

    swap = mock.MagicMock()
    swap.percent = 10.0
    swap.total = 2_000_000_000
    swap.used = 200_000_000
    swap.free = 1_800_000_000

    cpu_times = mock.MagicMock()
    cpu_times.user = 20.0
    cpu_times.system = 10.0
    cpu_times.idle = 70.0

    from aignostics.utils._process import ParentProcessInfo, ProcessInfo

    mock_process_info = ProcessInfo(
        project_root="/fake/root",
        pid=1234,
        parent=ParentProcessInfo(name="pytest", pid=1),
    )

    @contextlib.contextmanager
    def _ctx():
        with (
            mock.patch("psutil.boot_time", return_value=boot_time),
            mock.patch("psutil.virtual_memory", return_value=vmem),
            mock.patch("psutil.swap_memory", return_value=swap),
            mock.patch("psutil.cpu_percent", return_value=15.0),
            mock.patch("psutil.cpu_times_percent", return_value=cpu_times),
            mock.patch("psutil.getloadavg", return_value=(1.0, 1.0, 1.0)),
            mock.patch("psutil.Process", return_value=_make_mock_process()),
            mock.patch("aignostics.system._service.get_process_info", return_value=mock_process_info),
            mock.patch("asyncio.sleep"),
            mock.patch.object(Service, "_get_public_ipv4", return_value=None),
            mock.patch.object(Service, "_collect_all_settings", return_value={}),
            mock.patch("aignostics.system._service.locate_subclasses", return_value=[]),
            mock.patch("time.time", return_value=now),
        ):
            yield

    return _ctx()


@pytest.mark.unit
def test_get_cpu_freq_info_returns_dict_with_expected_keys() -> None:
    """Test that _get_cpu_freq_info returns a dict with exactly the keys current, min, max."""
    result = Service._get_cpu_freq_info()
    assert set(result.keys()) == {"current", "min", "max"}


@pytest.mark.unit
def test_get_cpu_freq_info_handles_runtime_error() -> None:
    """Test that a RuntimeError from psutil.cpu_freq is caught and all values are None."""
    import psutil

    with mock.patch.object(psutil, "cpu_freq", create=True, side_effect=RuntimeError("unavailable")):
        result = Service._get_cpu_freq_info()

    assert result == {"current": None, "min": None, "max": None}


@pytest.mark.unit
def test_get_cpu_freq_info_handles_missing_cpu_freq() -> None:
    """Test that a missing cpu_freq attribute on psutil is handled and all values are None."""
    import psutil

    had_cpu_freq = hasattr(psutil, "cpu_freq")
    original: Any = getattr(psutil, "cpu_freq", None)
    if had_cpu_freq:
        del psutil.cpu_freq
    try:
        result = Service._get_cpu_freq_info()
    finally:
        if had_cpu_freq:
            psutil.cpu_freq = original  # type: ignore[attr-defined]

    assert result == {"current": None, "min": None, "max": None}


@pytest.mark.unit
@pytest.mark.timeout(15)
def test_is_token_valid(record_property) -> None:
    """Test that is_token_valid works correctly with environment variable."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_token_valid_when_not_set(record_property) -> None:
    """Test that is_token_valid handles the case when no token is set."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    # Ensure the environment variable is not set
    with mock.patch.dict(os.environ, {"AIGNOSTICS_SYSTEM_TOKEN": ""}, clear=True):
        # Create a new service instance with no token set
        service = Service()

        # Should return False for any token when no token is set
        assert service.is_token_valid("any-token") is False
        assert service.is_token_valid("") is False


@pytest.mark.unit
def test_is_secret_key_word_boundary_matching_positive_cases(record_property) -> None:
    """Test that word boundary terms are correctly identified as secrets."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_word_boundary_matching_negative_cases(record_property) -> None:
    """Test that word boundary terms do not match partial words."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_string_match_terms_positive_cases(record_property) -> None:
    """Test that string match terms are correctly identified as secrets."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_string_match_terms_edge_cases(record_property) -> None:
    """Test edge cases for string matching."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_non_secret_keys(record_property) -> None:
    """Test that non-secret keys are correctly identified as non-secrets."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_case_insensitivity(record_property) -> None:
    """Test that the method is case insensitive."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_special_characters_and_boundaries(record_property) -> None:
    """Test handling of special characters and word boundaries."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


@pytest.mark.unit
def test_is_secret_key_empty_and_none_like_inputs(record_property) -> None:
    """Test edge cases with empty or minimal inputs."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
    test_cases = [
        ("", False),  # Empty string
        ("   ", False),  # Whitespace only
        ("a", False),  # Single character
        ("ab", False),  # Two characters
    ]

    for key, expected in test_cases:
        result = Service._is_secret_key(key)
        assert result == expected, f"Expected _is_secret_key('{key}') to return {expected}, got {result}"


@pytest.mark.unit
def test_is_secret_key_real_world_examples(record_property) -> None:
    """Test with real-world examples of environment variable names."""
    record_property("tested-item-id", "SPEC-SYSTEM-SERVICE")
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


# ---------------------------------------------------------------------------
# Uptime tests — verify psutil-based implementation
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_info_uptime_keys_present() -> None:
    """info() uptime dict contains both 'seconds' and 'boottime' keys with non-None values."""
    with _patch_info_dependencies():
        result = await Service.info()

    uptime = result["runtime"]["host"]["uptime"]
    assert "seconds" in uptime
    assert "boottime" in uptime
    assert uptime["seconds"] is not None
    assert uptime["boottime"] is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_info_uptime_seconds_positive() -> None:
    """info() uptime seconds is a positive number (time since boot)."""
    with _patch_info_dependencies():
        result = await Service.info()

    seconds = result["runtime"]["host"]["uptime"]["seconds"]
    assert isinstance(seconds, float)
    assert seconds > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_info_uptime_boottime_is_iso_string() -> None:
    """info() uptime boottime is a non-empty ISO 8601 string."""
    import datetime

    with _patch_info_dependencies():
        result = await Service.info()

    boottime_str = result["runtime"]["host"]["uptime"]["boottime"]
    assert isinstance(boottime_str, str)
    assert len(boottime_str) > 0
    # Must be parseable as an ISO 8601 datetime
    parsed = datetime.datetime.fromisoformat(boottime_str)
    assert parsed.tzinfo is not None  # timezone-aware (UTC)
