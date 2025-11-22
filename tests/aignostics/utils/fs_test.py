"""Tests for fs utilities."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aignostics.utils._fs import (
    get_user_data_directory,
    open_user_data_directory,
    sanitize_path,
    sanitize_path_component,
)


@pytest.mark.unit
def test_string_input_returns_string(record_property) -> None:
    """Test that string input returns string output."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    result = sanitize_path("test/path")
    assert isinstance(result, str)
    assert result == "test/path"


@pytest.mark.unit
def test_path_input_returns_path(record_property) -> None:
    """Test that Path input returns Path output."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    input_path = Path("test/path")
    result = sanitize_path(input_path)
    assert isinstance(result, Path)
    assert str(result) == str(Path("test/path"))


@pytest.mark.unit
def test_colon_replacement_on_all_platforms(record_property) -> None:
    """Test that colons are replaced on all platforms."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Linux"):
        result = sanitize_path("test:path:with:colons")
        assert result == "test_path_with_colons"


@pytest.mark.unit
def test_windows_colon_replacement_enabled(record_property) -> None:
    """Test colon replacement on Windows when enabled."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("test:path:with:colons")
        assert result == "test_path_with_colons"
    with patch("platform.system", return_value="Linux"):
        result = sanitize_path("test:path:with:colons")
        assert result == "test_path_with_colons"


@pytest.mark.unit
def test_windows_drive_letter_preserved(record_property) -> None:
    """Test that Windows drive letters are preserved when replacing colons."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("C:/test:path")
        assert result == "C:/test_path"


@pytest.mark.unit
def test_windows_drive_letter_with_multiple_colons(record_property) -> None:
    """Test drive letter preservation with multiple colons."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("D:/folder:name:with:colons")
        assert result == "D:/folder_name_with_colons"


@pytest.mark.unit
def test_windows_no_drive_letter_all_colons_replaced(record_property) -> None:
    """Test that all colons are replaced when no drive letter is present."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("folder:name:with:colons")
        assert result == "folder_name_with_colons"


@pytest.mark.unit
def test_windows_single_char_with_colon_is_drive(record_property) -> None:
    """Test that single character with colon IS treated as drive letter."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        # "a:test" has colon in position 1 and 'a' is alphabetic, so it IS treated as a drive letter
        # Only the part after the drive letter should have colons replaced
        result = sanitize_path("a:test")
        assert result == "a:test"  # Drive letter preserved, no additional colons to replace


@pytest.mark.unit
def test_windows_numeric_with_colon_not_drive(record_property) -> None:
    """Test that numeric character with colon is not treated as drive letter."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("1:test")
        assert result == "1_test"  # All colons replaced since '1' is not alphabetic
        result = sanitize_path("1:/test")
        assert result == "1_/test"


@pytest.mark.unit
def test_windows_reserved_path_raises_error(record_property) -> None:
    """Test that reserved Windows paths raise ValueError."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
        pytest.raises(ValueError, match="The path 'CON' is reserved on Windows"),
    ):
        sanitize_path("CON")


@pytest.mark.unit
def test_windows_non_reserved_path_succeeds(record_property) -> None:
    """Test that non-reserved Windows paths succeed."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=False),
    ):
        result = sanitize_path("valid_path")
        assert result == "valid_path"


@pytest.mark.unit
def test_windows_reserved_path_with_path_object(record_property) -> None:
    """Test that reserved Windows paths raise ValueError with Path input."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
        pytest.raises(ValueError, match="The path 'PRN' is reserved on Windows"),
    ):
        sanitize_path(Path("PRN"))


@pytest.mark.unit
def test_windows_reserved_path_after_colon_replacement(record_property) -> None:
    """Test reserved path check happens after colon replacement."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
        pytest.raises(ValueError, match="The path 'test_AUX' is reserved on Windows"),
    ):
        sanitize_path("test:AUX")


@pytest.mark.unit
def test_non_windows_reserved_check_skipped(record_property) -> None:
    """Test that reserved path check is skipped on non-Windows systems."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("platform.system", return_value="Linux"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
    ):
        # This should not raise an error even if PureWindowsPath.is_reserved returns True
        result = sanitize_path("CON")
        assert result == "CON"


@pytest.mark.unit
def test_windows_empty_string(record_property) -> None:
    """Test handling of empty string on Windows."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("")
        assert not result


@pytest.mark.unit
def test_windows_path_object_preserves_type(record_property) -> None:
    """Test that Path object input returns Path object with colon replacement."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        input_path = Path("test:path")
        result = sanitize_path(input_path)
        assert isinstance(result, Path)
        assert str(result) == "test_path"


@pytest.mark.unit
def test_windows_complex_path_with_drive(record_property) -> None:
    """Test complex Windows path with drive letter and multiple colons."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("C:/Users/test:user/Documents/file:name.txt")
        assert result == "C:/Users/test_user/Documents/file_name.txt"


# Tests for sanitize_path_component function
@pytest.mark.unit
def test_sanitize_path_component_all_platforms(record_property) -> None:
    """Test that sanitize_path_component replaces colons on all platforms."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Linux"):
        result = sanitize_path_component("test:component:with:colons")
        assert result == "test_component_with_colons"


@pytest.mark.unit
def test_sanitize_path_component_windows_replaces_all_colons(record_property) -> None:
    """Test that sanitize_path_component replaces all colons on Windows."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("test:component:with:colons")
        assert result == "test_component_with_colons"


@pytest.mark.unit
def test_sanitize_path_component_windows_drive_like_pattern(record_property) -> None:
    """Test that sanitize_path_component replaces colons even for drive-like patterns."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("a:whatever")
        assert result == "a_whatever"
        result = sanitize_path_component("C:filename")
        assert result == "C_filename"


@pytest.mark.unit
def test_sanitize_path_component_windows_empty_string(record_property) -> None:
    """Test that sanitize_path_component handles empty string."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("")
        assert not result


@pytest.mark.unit
def test_sanitize_path_component_windows_no_colons(record_property) -> None:
    """Test that sanitize_path_component returns unchanged when no colons."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("normal_filename.txt")
        assert result == "normal_filename.txt"


@pytest.mark.unit
def test_sanitize_path_component_multiple_consecutive_colons(record_property) -> None:
    """Test that sanitize_path_component handles multiple consecutive colons."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("file:::name")
        assert result == "file___name"


# Tests for integration between sanitize_path and sanitize_path_component
@pytest.mark.unit
def test_sanitize_path_uses_sanitize_path_component_for_drive_path(record_property) -> None:
    """Test that sanitize_path uses sanitize_path_component for the non-drive part."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        # Drive letter should be preserved, but rest should be sanitized using sanitize_path_component
        result = sanitize_path("C:/folder:name:with:colons")
        assert result == "C:/folder_name_with_colons"


@pytest.mark.unit
def test_sanitize_path_uses_sanitize_path_component_for_non_drive_path(record_property) -> None:
    """Test that sanitize_path uses sanitize_path_component for paths without drive letters."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("folder:name:with:colons")
        assert result == "folder_name_with_colons"


# Tests for get_user_data_directory function
@pytest.mark.integration
def test_get_user_data_directory_without_scope(record_property, tmp_path) -> None:
    """Test get_user_data_directory returns correct path without scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory()

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@pytest.mark.integration
def test_get_user_data_directory_with_scope(record_property, tmp_path) -> None:
    """Test get_user_data_directory returns correct path with scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("models")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "models")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@pytest.mark.integration
def test_get_user_data_directory_with_nested_scope(record_property, tmp_path) -> None:
    """Test get_user_data_directory returns correct path with nested scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("cache/models")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "cache" / "models")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@pytest.mark.integration
def test_get_user_data_directory_read_only_environment_no_mkdir(record_property, tmp_path) -> None:
    """Test get_user_data_directory doesn't create directory in read-only environment."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", True),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("cache")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "cache")
        mock_mkdir.assert_not_called()


@pytest.mark.integration
def test_get_user_data_directory_empty_scope(record_property, tmp_path) -> None:
    """Test get_user_data_directory handles empty scope string."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@pytest.mark.integration
def test_get_user_data_directory_none_scope(record_property, tmp_path) -> None:
    """Test get_user_data_directory handles None scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory(None)

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# Tests for open_user_data_directory function
@pytest.mark.integration
def test_open_user_data_directory_without_scope(record_property, tmp_path) -> None:
    """Test open_user_data_directory opens correct directory without scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory()

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project"))


@pytest.mark.integration
def test_open_user_data_directory_with_scope(record_property, tmp_path) -> None:
    """Test open_user_data_directory opens correct directory with scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory("logs")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "logs")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project" / "logs"))


@pytest.mark.integration
def test_open_user_data_directory_with_nested_scope(record_property, tmp_path) -> None:
    """Test open_user_data_directory opens correct directory with nested scope."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory("cache/models")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "cache" / "models")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project" / "cache" / "models"))


@pytest.mark.integration
def test_open_user_data_directory_read_only_environment(record_property, tmp_path) -> None:
    """Test open_user_data_directory works in read-only environment."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", True),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory("data")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "data")
        mock_mkdir.assert_not_called()  # Should not create directory in read-only environment
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project" / "data"))


@pytest.mark.integration
def test_open_user_data_directory_show_in_file_manager_exception(record_property, tmp_path) -> None:
    """Test open_user_data_directory handles show_in_file_manager exceptions gracefully."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with (
        patch("aignostics.utils._fs.platformdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as _mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")
        mock_show_in_file_manager.side_effect = Exception("File manager not available")

        # The function should still return the path even if file manager fails
        result = open_user_data_directory()

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
