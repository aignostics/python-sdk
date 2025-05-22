"""Tests for logging configuration and utilities."""

import tempfile
from pathlib import Path
from unittest import mock

import pytest

from aignostics.utils import get_logger
from aignostics.utils._log import _validate_file_name, logging_initialize

log = get_logger(__name__)


def test_validate_file_name_none() -> None:
    """Test that None file name is returned unchanged."""
    assert _validate_file_name(None) is None


def test_validate_file_name_nonexistent() -> None:
    """Test validation of a non-existent file that can be created."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test_log.log"
        assert _validate_file_name(str(test_file)) == str(test_file)
        # Verify the file was not actually created
        assert not test_file.exists()


def test_validate_file_name_existing() -> None:
    """Test validation of an existing writable file."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as temp_file:
        temp_file_path = Path(temp_file.name)

    try:
        # File exists and is writable
        assert _validate_file_name(str(temp_file_path)) == str(temp_file_path)
    finally:
        # Clean up
        temp_file_path.unlink(missing_ok=True)


def test_validate_file_name_existing_readonly() -> None:
    """Test validation of an existing read-only file."""
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


def test_validate_file_name_directory() -> None:
    """Test validation of a path that points to a directory."""
    with tempfile.TemporaryDirectory() as temp_dir, pytest.raises(ValueError, match=r"is not a file"):
        _validate_file_name(temp_dir)


def test_validate_file_name_cannot_create() -> None:
    """Test validation of a file that cannot be created due to permissions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        # Make temp dir read-only
        temp_dir_path.chmod(0o555)

        try:
            test_file = temp_dir_path / "test_log.log"
            with pytest.raises(ValueError, match=r"cannot be created"):
                _validate_file_name(str(test_file))
        finally:
            # Need to make it writable again to allow cleanup
            temp_dir_path.chmod(0o755)


def test_validate_file_name_invalid_path() -> None:
    """Test validation of a file with an invalid path."""
    # Testing with a path that should always be invalid
    invalid_path = Path("/nonexistent/directory/that/definitely/should/not/exist") / "file.log"
    with pytest.raises(ValueError, match=r"cannot be created"):
        _validate_file_name(str(invalid_path))


def test_get_logger_with_name() -> None:
    """Test get_logger with a specific name."""
    logger = get_logger("test_module")
    assert logger.name == "aignostics.test_module"


def test_get_logger_none() -> None:
    """Test get_logger with None name."""
    logger = get_logger(None)
    assert logger.name == "aignostics"


def test_get_logger_project_name() -> None:
    """Test get_logger with the project name."""
    logger = get_logger("aignostics")
    assert logger.name == "aignostics"


def test_logging_initialize_with_defaults() -> None:
    """Test logging_initialize with default settings."""
    with (
        mock.patch("aignostics.utils._log.load_settings") as mock_load_settings,
        mock.patch("logging.basicConfig") as mock_basic_config,
    ):
        # Mock settings with defaults
        mock_settings = mock.MagicMock()
        mock_settings.file_enabled = False
        mock_settings.console_enabled = False
        mock_settings.level = "INFO"
        mock_load_settings.return_value = mock_settings

        # Call the function
        logging_initialize()

        # Verify basicConfig was called with empty handlers list
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args.kwargs
        assert call_kwargs["level"] == "INFO"
        assert call_kwargs["handlers"] == []
