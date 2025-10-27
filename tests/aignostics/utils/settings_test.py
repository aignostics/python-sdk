"""Tests for the settings."""

import os
from typing import Any, ClassVar
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from aignostics.utils._settings import (
    UNHIDE_SENSITIVE_INFO,
    OpaqueSettings,
    load_settings,
    strip_to_none_before_validator,
)


@pytest.mark.unit
def test_strip_to_none_before_validator_with_none(record_property) -> None:
    """Test that None is returned when None is passed."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    assert strip_to_none_before_validator(None) is None


@pytest.mark.unit
def test_strip_to_none_before_validator_with_empty_string(record_property) -> None:
    """Test that None is returned when an empty string is passed."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    assert strip_to_none_before_validator("") is None


@pytest.mark.unit
def test_strip_to_none_before_validator_with_whitespace_string(record_property) -> None:
    """Test that None is returned when a whitespace string is passed."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    assert strip_to_none_before_validator("  \t\n  ") is None


@pytest.mark.unit
def test_strip_to_none_before_validator_with_valid_string(record_property) -> None:
    """Test that a stripped string is returned when a valid string is passed."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    assert strip_to_none_before_validator("  test  ") == "test"


class TheTestSettings(OpaqueSettings):
    """Test settings class."""

    test_value: str = "default"
    secret_value: SecretStr | None = None
    required_value: str


@pytest.mark.unit
def test_opaque_settings_serialize_sensitive_info_with_unhide(record_property) -> None:
    """Test that sensitive info is revealed when unhide_sensitive_info is True."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    secret = SecretStr("sensitive")
    context = {UNHIDE_SENSITIVE_INFO: True}

    result = OpaqueSettings.serialize_sensitive_info(secret, type("FieldSerializationInfo", (), {"context": context}))

    assert result == "sensitive"


@pytest.mark.unit
def test_opaque_settings_serialize_sensitive_info_without_unhide(record_property) -> None:
    """Test that sensitive info is hidden when unhide_sensitive_info is False."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    secret = SecretStr("sensitive")
    context = {UNHIDE_SENSITIVE_INFO: False}

    result = OpaqueSettings.serialize_sensitive_info(secret, type("FieldSerializationInfo", (), {"context": context}))

    assert result == "**********"


@pytest.mark.unit
def test_opaque_settings_serialize_sensitive_info_empty(record_property) -> None:
    """Test that None is returned when the SecretStr is empty."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    secret = SecretStr("")
    context = {}

    result = OpaqueSettings.serialize_sensitive_info(secret, type("FieldSerializationInfo", (), {"context": context}))

    assert result is None


@pytest.mark.unit
@patch.dict(os.environ, {"REQUIRED_VALUE": "test_value"})
def test_load_settings_success(record_property) -> None:
    """Test successful settings loading."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    settings = load_settings(TheTestSettings)
    assert settings.test_value == "default"
    assert settings.required_value == "test_value"


@pytest.mark.unit
@patch("sys.exit")
@patch("rich.console.Console.print")
def test_load_settings_validation_error(mock_console_print, mock_exit, record_property) -> None:
    """Test that validation error is handled properly."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # The settings class requires required_value, but we're not providing it
    # This will trigger a validation error
    load_settings(TheTestSettings)

    mock_exit.assert_called_once_with(78)

    assert mock_console_print.call_count == 1, (
        "Expected console.print to be called exactly once, but was called "
        f"{mock_console_print.call_count} times. If this test fails with a higher call count, "
        "you likely have AIGNOSTICS_LOG_CONSOLE_ENABLE=true in your .env file. "
        "Disable console logging to make this test pass."
    )


class TheTestSettingsWithEnvPrefix(OpaqueSettings):
    """Test settings class with an environment prefix."""

    model_config: ClassVar[dict[str, Any]] = {"env_prefix": "TEST_"}

    value: str


@pytest.mark.unit
@patch.dict(os.environ, {"TEST_VALUE": "prefixed_value"})
def test_settings_with_env_prefix(record_property) -> None:
    """Test that settings with environment prefix work correctly."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    settings = load_settings(TheTestSettingsWithEnvPrefix)
    assert settings.value == "prefixed_value"


class TheTestSettingsWithEnvFile(OpaqueSettings):
    """Test settings class with a custom env file."""

    model_config: ClassVar[dict[str, Any]] = {"env_file": "custom.env"}

    value: str = "default"
