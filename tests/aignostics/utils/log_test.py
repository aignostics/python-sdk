"""Tests for logging configuration and utilities."""

import platform
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from aignostics_sdk.utils._log import _validate_file_name, logging_initialize


@pytest.mark.unit
def test_validate_file_name_none(record_property) -> None:
    """Test that None file name is returned unchanged."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    assert _validate_file_name(None) is None


@pytest.mark.integration
def test_validate_file_name_nonexistent(record_property) -> None:
    """Test validation of a non-existent file that can be created."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test_log.log"
        assert _validate_file_name(str(test_file)) == str(test_file)
        # Verify the file was not actually created
        assert not test_file.exists()


@pytest.mark.integration
def test_validate_file_name_existing(record_property) -> None:
    """Test validation of an existing writable file."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as temp_file:
        temp_file_path = Path(temp_file.name)

    try:
        # File exists and is writable
        assert _validate_file_name(str(temp_file_path)) == str(temp_file_path)
    finally:
        # Clean up
        temp_file_path.unlink(missing_ok=True)


@pytest.mark.integration
def test_validate_file_name_existing_readonly(record_property) -> None:
    """Test validation of an existing read-only file."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as temp_file:
        temp_file_path = Path(temp_file.name)

    try:
        # Make file read-only
        temp_file_path.chmod(0o444)

        # File exists but is not writable
        with pytest.raises(ValueError, match=r"is not writable"):
            _validate_file_name(str(temp_file_path))
    finally:
        # Need to make it writable again to delete it
        temp_file_path.chmod(0o644)
        temp_file_path.unlink(missing_ok=True)


@pytest.mark.integration
def test_validate_file_name_directory(record_property) -> None:
    """Test validation of a path that points to a directory."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with tempfile.TemporaryDirectory() as temp_dir, pytest.raises(ValueError, match=r"exists but is a directory"):
        _validate_file_name(temp_dir)


@pytest.mark.integration
@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="This test is designed for Unix-like systems where permissions can be set to non-writable.",
)
def test_validate_file_name_cannot_create(record_property) -> None:
    """Test validation of a file that cannot be created due to permissions."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_dir_path.chmod(0o555)
        try:
            test_file = temp_dir_path / "test_log.log"
            with pytest.raises(ValueError, match=r"cannot be created"):
                _validate_file_name(str(test_file))
        finally:
            # Need to make it writable again to allow cleanup
            temp_dir_path.chmod(0o755)


@pytest.mark.unit
def test_validate_file_name_invalid_path(record_property) -> None:
    """Test validation of a file with an invalid path."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Testing with a path that should always be invalid
    invalid_path = Path("/nonexistent/directory/that/definitely/should/not/exist") / "file.log"
    with pytest.raises(ValueError, match=r"cannot be created"):
        _validate_file_name(str(invalid_path))


@pytest.mark.unit
def test_logging_initialize_with_defaults(record_property, caplog: pytest.LogCaptureFixture) -> None:
    """Test logging_initialize with default settings."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    from aignostics_sdk.utils._log import logger

    with (
        mock.patch("aignostics.utils._log.load_settings") as mock_load_settings,
        mock.patch.object(logger, "remove") as mock_remove,
        mock.patch.object(logger, "configure") as mock_configure,
        mock.patch.object(logger, "add") as mock_add,
        mock.patch("logging.basicConfig") as mock_basic_config,
    ):
        # Mock settings with defaults (stderr_enabled=True, file_enabled=False, redirect_logging=True)
        mock_settings = mock.MagicMock()
        mock_settings.stderr_enabled = True
        mock_settings.file_enabled = False
        mock_settings.redirect_logging = True
        mock_settings.level = "INFO"
        mock_load_settings.return_value = mock_settings

        # Call the function
        logging_initialize()

        # Verify logger was reset and configured
        mock_remove.assert_called_once()
        mock_configure.assert_called_once()

        # Verify logger.add was called for stderr (since stderr_enabled=True by default)
        assert mock_add.call_count == 1

        # Verify logging.basicConfig was called (since redirect_logging=True)
        mock_basic_config.assert_called_once()
