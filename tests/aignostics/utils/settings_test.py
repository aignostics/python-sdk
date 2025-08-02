"""Tests for the settings."""

import os
from typing import Any, ClassVar
from unittest.mock import patch

from pydantic import SecretStr

from aignostics.utils._settings import (
    UNHIDE_SENSITIVE_INFO,
    OpaqueSettings,
    load_settings,
    strip_to_none_before_validator,
)


def test_strip_to_none_before_validator_with_none(record_property) -> None:
    """Test that None is returned when None is passed."""
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    assert strip_to_none_before_validator(None) is None


def test_strip_to_none_before_validator_with_empty_string(record_property) -> None:
    """Test that None is returned when an empty string is passed."""
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    assert strip_to_none_before_validator("") is None


def test_strip_to_none_before_validator_with_whitespace_string(record_property) -> None:
    """Test that None is returned when a whitespace string is passed."""
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    assert strip_to_none_before_validator("  \t\n  ") is None


def test_strip_to_none_before_validator_with_valid_string(record_property) -> None:
    """Test that a stripped string is returned when a valid string is passed."""
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    assert strip_to_none_before_validator("  test  ") == "test"


class TheTestSettings(OpaqueSettings):
    """Test settings class."""

    test_value: str = "default"
    secret_value: SecretStr | None = None
    required_value: str


def test_opaque_settings_serialize_sensitive_info_with_unhide(record_property) -> None:
    """Test that sensitive info is revealed when unhide_sensitive_info is True."""
    record_property("tested-item-id", "ADR-23-SYSTEM-SETTINGS-WEB-INTERFACE")
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    secret = SecretStr("sensitive")
    context = {UNHIDE_SENSITIVE_INFO: True}

    result = OpaqueSettings.serialize_sensitive_info(secret, type("FieldSerializationInfo", (), {"context": context}))

    assert result == "sensitive"


def test_opaque_settings_serialize_sensitive_info_without_unhide(record_property) -> None:
    """Test that sensitive info is hidden when unhide_sensitive_info is False."""
    record_property("tested-item-id", "ADR-23-SYSTEM-SETTINGS-WEB-INTERFACE")
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    secret = SecretStr("sensitive")
    context = {UNHIDE_SENSITIVE_INFO: False}

    result = OpaqueSettings.serialize_sensitive_info(secret, type("FieldSerializationInfo", (), {"context": context}))

    assert result == "**********"


def test_opaque_settings_serialize_sensitive_info_empty(record_property) -> None:
    """Test that None is returned when the SecretStr is empty."""
    record_property("tested-item-id", "ADR-23-SYSTEM-SETTINGS-WEB-INTERFACE")
    secret = SecretStr("")
    context = {}

    result = OpaqueSettings.serialize_sensitive_info(secret, type("FieldSerializationInfo", (), {"context": context}))

    assert result is None


@patch.dict(os.environ, {"REQUIRED_VALUE": "test_value"})
def test_load_settings_success(record_property) -> None:
    """Test successful settings loading."""
    record_property("tested-item-id", "ADR-6-CLOUD-STORAGE-INFRASTRUCTURE")
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    settings = load_settings(TheTestSettings)
    assert settings.test_value == "default"
    assert settings.required_value == "test_value"


@patch("sys.exit")
@patch("rich.console.Console.print")
def test_load_settings_validation_error(mock_console_print, mock_exit, record_property) -> None:
    """Test that validation error is handled properly."""
    record_property("tested-item-id", "ADR-6-CLOUD-STORAGE-INFRASTRUCTURE")
    record_property("tested-item-id", "API-DATASET-MANAGEMENT")
    # The settings class requires required_value, but we're not providing it
    # This will trigger a validation error
    load_settings(TheTestSettings)

    # Verify that sys.exit was called with the correct code
    mock_exit.assert_called_once_with(78)

    # Verify that console.print was called (with a panel showing the error)
    mock_console_print.assert_called_once()


class TheTestSettingsWithEnvPrefix(OpaqueSettings):
    """Test settings class with an environment prefix."""

    model_config: ClassVar[dict[str, Any]] = {"env_prefix": "TEST_"}

    value: str


@patch.dict(os.environ, {"TEST_VALUE": "prefixed_value"})
def test_settings_with_env_prefix(record_property) -> None:
    """Test that settings with environment prefix work correctly."""
    record_property("tested-item-id", "ADR-6-CLOUD-STORAGE-INFRASTRUCTURE")
    settings = load_settings(TheTestSettingsWithEnvPrefix)
    assert settings.value == "prefixed_value"


class TheTestSettingsWithEnvFile(OpaqueSettings):
    """Test settings class with a custom env file."""

    model_config: ClassVar[dict[str, Any]] = {"env_file": "custom.env"}

    value: str = "default"
