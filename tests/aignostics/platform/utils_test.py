"""Tests for the platform utility functions."""

import math
import tempfile
from pathlib import Path

import pytest

from aignostics.platform import mime_type_to_file_ending
from aignostics.platform._utils import calculate_file_crc32c, convert_to_json_serializable


class TestConvertToJsonSerializable:
    """Tests for the convert_to_json_serializable function."""

    @pytest.mark.unit
    @staticmethod
    def test_convert_simple_set_to_list() -> None:
        """Test that a set is converted to a sorted list.

        This test verifies that the convert_to_json_serializable function correctly
        converts a set to a sorted list for JSON serialization.
        """
        result = convert_to_json_serializable({"a", "c", "b"})
        assert result == ["a", "b", "c"]

    @pytest.mark.unit
    @staticmethod
    def test_convert_numeric_set_to_list() -> None:
        """Test that a numeric set is converted to a sorted list.

        This test verifies that the convert_to_json_serializable function correctly
        converts a numeric set to a sorted list for JSON serialization.
        """
        result = convert_to_json_serializable({3, 1, 2})
        assert result == [1, 2, 3]

    @pytest.mark.unit
    @staticmethod
    def test_convert_dict_with_set_values() -> None:
        """Test that a dictionary with set values has them converted to lists.

        This test verifies that the convert_to_json_serializable function recursively
        converts set values within dictionaries to sorted lists.
        """
        result = convert_to_json_serializable({"tags": {"test", "prod", "dev"}})
        assert result == {"tags": ["dev", "prod", "test"]}

    @pytest.mark.unit
    @staticmethod
    def test_convert_nested_dict_with_sets() -> None:
        """Test that nested dictionaries with sets are fully converted.

        This test verifies that the convert_to_json_serializable function recursively
        processes nested structures containing sets.
        """
        input_data = {
            "outer": {
                "inner": {"items": {5, 3, 1}},
                "tags": {"z", "a"},
            }
        }
        expected = {
            "outer": {
                "inner": {"items": [1, 3, 5]},
                "tags": ["a", "z"],
            }
        }
        result = convert_to_json_serializable(input_data)
        assert result == expected

    @pytest.mark.unit
    @staticmethod
    def test_convert_list_with_sets() -> None:
        """Test that lists containing sets have them converted to lists.

        This test verifies that the convert_to_json_serializable function recursively
        processes lists containing sets.
        """
        result = convert_to_json_serializable([{"a", "b"}, {"c", "d"}])
        assert result == [["a", "b"], ["c", "d"]]

    @pytest.mark.unit
    @staticmethod
    def test_convert_tuple_with_sets() -> None:
        """Test that tuples containing sets have them converted to lists.

        This test verifies that the convert_to_json_serializable function recursively
        processes tuples containing sets and converts the tuple itself to a list.
        """
        result = convert_to_json_serializable(({"x", "y"}, {"z"}))
        assert result == [["x", "y"], ["z"]]

    @pytest.mark.unit
    @staticmethod
    def test_convert_mixed_types_unchanged() -> None:
        """Test that JSON-serializable types remain unchanged.

        This test verifies that the convert_to_json_serializable function does not
        modify types that are already JSON-serializable (str, int, bool, None).
        """
        input_data = {
            "string": "test",
            "number": 42,
            "float": math.pi,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
        }
        result = convert_to_json_serializable(input_data)
        assert result == input_data

    @pytest.mark.unit
    @staticmethod
    def test_convert_empty_set() -> None:
        """Test that an empty set is converted to an empty list.

        This test verifies that the convert_to_json_serializable function correctly
        handles empty sets.
        """
        result = convert_to_json_serializable(set())
        assert result == []

    @pytest.mark.unit
    @staticmethod
    def test_convert_complex_nested_structure() -> None:
        """Test conversion of a complex nested structure with multiple sets.

        This test verifies that the convert_to_json_serializable function can handle
        deeply nested structures with sets at various levels.
        """
        input_data = {
            "sdk": {
                "tags": {"test_1", "test_2"},
                "metadata": {
                    "nested": [
                        {"items": {1, 2}},
                        {"values": {"a", "b"}},
                    ]
                },
            },
            "user": {
                "groups": {"admin", "user"},
            },
        }
        expected = {
            "sdk": {
                "tags": ["test_1", "test_2"],
                "metadata": {
                    "nested": [
                        {"items": [1, 2]},
                        {"values": ["a", "b"]},
                    ]
                },
            },
            "user": {
                "groups": ["admin", "user"],
            },
        }
        result = convert_to_json_serializable(input_data)
        assert result == expected


class TestMimeTypeToFileEnding:
    """Tests for the mime_type_to_file_ending function."""

    @pytest.mark.unit
    @staticmethod
    def test_png_mime_type(record_property) -> None:
        """Test that image/png MIME type returns .png extension.

        This test verifies that the mime_type_to_file_ending function correctly
        maps the image/png MIME type to the .png file extension.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        assert mime_type_to_file_ending("image/png") == ".png"

    @pytest.mark.unit
    @staticmethod
    def test_tiff_mime_type(record_property) -> None:
        """Test that image/tiff MIME type returns .tiff extension.

        This test verifies that the mime_type_to_file_ending function correctly
        maps the image/tiff MIME type to the .tiff file extension.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        assert mime_type_to_file_ending("image/tiff") == ".tiff"

    @pytest.mark.unit
    @staticmethod
    def test_parquet_mime_type(record_property) -> None:
        """Test that application/vnd.apache.parquet MIME type returns .parquet extension.

        This test verifies that the mime_type_to_file_ending function correctly
        maps the application/vnd.apache.parquet MIME type to the .parquet file extension.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        assert mime_type_to_file_ending("application/vnd.apache.parquet") == ".parquet"

    @pytest.mark.unit
    @staticmethod
    def test_json_mime_type(record_property) -> None:
        """Test that application/json MIME type returns .json extension.

        This test verifies that the mime_type_to_file_ending function correctly
        maps the application/json MIME type to the .json file extension.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        assert mime_type_to_file_ending("application/json") == ".json"

    @pytest.mark.unit
    @staticmethod
    def test_geojson_mime_type(record_property) -> None:
        """Test that application/geo+json MIME type returns .json extension.

        This test verifies that the mime_type_to_file_ending function correctly
        maps the application/geo+json MIME type to the .json file extension.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        assert mime_type_to_file_ending("application/geo+json") == ".json"

    @pytest.mark.unit
    @staticmethod
    def test_csv_mime_type(record_property) -> None:
        """Test that text/csv MIME type returns .csv extension.

        This test verifies that the mime_type_to_file_ending function correctly
        maps the text/csv MIME type to the .csv file extension.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        assert mime_type_to_file_ending("text/csv") == ".csv"

    @pytest.mark.unit
    @staticmethod
    def test_unknown_mime_type_raises_error(record_property) -> None:
        """Test that an unknown MIME type raises a ValueError.

        This test verifies that the mime_type_to_file_ending function correctly
        raises a ValueError when given an unrecognized MIME type.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with pytest.raises(ValueError, match="Unknown mime type: application/unknown"):
            mime_type_to_file_ending("application/unknown")


class TestCalculateFileCrc32c:
    """Tests for the calculate_file_crc32c function."""

    @pytest.mark.unit
    @staticmethod
    def test_calculate_crc32c_small_file(record_property) -> None:
        """Test CRC32C calculation for a small file.

        This test verifies that the calculate_file_crc32c function correctly
        calculates the CRC32C checksum for a small file that fits in a single chunk.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(b"Hello, World!")

        try:
            checksum = calculate_file_crc32c(temp_path)
            # Verify it returns a base64-encoded string
            assert isinstance(checksum, str)
            assert len(checksum) > 0
            # The checksum for "Hello, World!" should be consistent
            assert checksum == "TVUQaA=="
        finally:
            temp_path.unlink()

    @pytest.mark.unit
    @staticmethod
    def test_calculate_crc32c_large_file(record_property) -> None:
        """Test CRC32C calculation for a large file with multiple chunks.

        This test verifies that the calculate_file_crc32c function correctly
        calculates the CRC32C checksum for a file larger than 8MB, ensuring
        the continue statement (line 187) is executed multiple times.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        # Create a file larger than EIGHT_MB (8,388,608 bytes)
        # Use 10MB to ensure multiple chunks
        file_size = 10 * 1024 * 1024  # 10 MB
        chunk_data = b"A" * (1024 * 1024)  # 1 MB chunks

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            for _ in range(10):  # Write 10 chunks of 1MB each
                temp_file.write(chunk_data)

        try:
            checksum = calculate_file_crc32c(temp_path)
            # Verify it returns a base64-encoded string
            assert isinstance(checksum, str)
            assert len(checksum) > 0
            # Verify file size is as expected
            assert temp_path.stat().st_size == file_size
        finally:
            temp_path.unlink()

    @pytest.mark.unit
    @staticmethod
    def test_calculate_crc32c_empty_file(record_property) -> None:
        """Test CRC32C calculation for an empty file.

        This test verifies that the calculate_file_crc32c function correctly
        handles empty files.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            # Don't write anything, leave file empty

        try:
            checksum = calculate_file_crc32c(temp_path)
            # Verify it returns a base64-encoded string
            assert isinstance(checksum, str)
            assert len(checksum) > 0
            # Empty file CRC32C checksum
            assert checksum == "AAAAAA=="
        finally:
            temp_path.unlink()

    @pytest.mark.unit
    @staticmethod
    def test_calculate_crc32c_deterministic(record_property) -> None:
        """Test that CRC32C calculation is deterministic.

        This test verifies that calculating the checksum multiple times for
        the same file produces the same result.
        """
        record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
        test_data = b"Test data for deterministic checksum verification"

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(test_data)

        try:
            checksum1 = calculate_file_crc32c(temp_path)
            checksum2 = calculate_file_crc32c(temp_path)
            assert checksum1 == checksum2
        finally:
            temp_path.unlink()
