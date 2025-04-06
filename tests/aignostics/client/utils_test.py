"""Tests for the client utility functions."""

import pytest

from aignostics.client.utils import mime_type_to_file_ending


class TestMimeTypeToFileEnding:
    """Tests for the mime_type_to_file_ending function."""

    def test_png_mime_type(self) -> None:
        """Test that image/png MIME type returns .png extension."""
        assert mime_type_to_file_ending("image/png") == ".png"

    def test_tiff_mime_type(self) -> None:
        """Test that image/tiff MIME type returns .tiff extension."""
        assert mime_type_to_file_ending("image/tiff") == ".tiff"

    def test_parquet_mime_type(self) -> None:
        """Test that application/vnd.apache.parquet MIME type returns .parquet extension."""
        assert mime_type_to_file_ending("application/vnd.apache.parquet") == ".parquet"

    def test_json_mime_type(self) -> None:
        """Test that application/json MIME type returns .json extension."""
        assert mime_type_to_file_ending("application/json") == ".json"

    def test_geojson_mime_type(self) -> None:
        """Test that application/geo+json MIME type returns .json extension."""
        assert mime_type_to_file_ending("application/geo+json") == ".json"

    def test_csv_mime_type(self) -> None:
        """Test that text/csv MIME type returns .csv extension."""
        assert mime_type_to_file_ending("text/csv") == ".csv"

    def test_unknown_mime_type_raises_error(self) -> None:
        """Test that an unknown MIME type raises a ValueError."""
        with pytest.raises(ValueError, match="Unknown mime type: application/unknown"):
            mime_type_to_file_ending("application/unknown")