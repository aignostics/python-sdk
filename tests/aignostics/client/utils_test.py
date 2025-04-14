"""Tests for the client utility functions."""

import pytest

from aignostics.client import mime_type_to_file_ending


class TestMimeTypeToFileEnding:
    """Tests for the mime_type_to_file_ending function."""

    @staticmethod
    def test_png_mime_type() -> None:
        """Test that image/png MIME type returns .png extension."""
        assert mime_type_to_file_ending("image/png") == ".png"

    @staticmethod
    def test_tiff_mime_type() -> None:
        """Test that image/tiff MIME type returns .tiff extension."""
        assert mime_type_to_file_ending("image/tiff") == ".tiff"

    @staticmethod
    def test_parquet_mime_type() -> None:
        """Test that application/vnd.apache.parquet MIME type returns .parquet extension."""
        assert mime_type_to_file_ending("application/vnd.apache.parquet") == ".parquet"

    @staticmethod
    def test_json_mime_type() -> None:
        """Test that application/json MIME type returns .json extension."""
        assert mime_type_to_file_ending("application/json") == ".json"

    @staticmethod
    def test_geojson_mime_type() -> None:
        """Test that application/geo+json MIME type returns .json extension."""
        assert mime_type_to_file_ending("application/geo+json") == ".json"

    @staticmethod
    def test_csv_mime_type() -> None:
        """Test that text/csv MIME type returns .csv extension."""
        assert mime_type_to_file_ending("text/csv") == ".csv"

    @staticmethod
    def test_unknown_mime_type_raises_error() -> None:
        """Test that an unknown MIME type raises a ValueError."""
        with pytest.raises(ValueError, match="Unknown mime type: application/unknown"):
            mime_type_to_file_ending("application/unknown")
