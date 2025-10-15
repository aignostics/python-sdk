"""Tests for the platform utility functions."""

import pytest

from aignostics.platform import mime_type_to_file_ending


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
