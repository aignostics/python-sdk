"""Tests to verify the CLI functionality of the wsi module."""

import platform
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

SERIES_UID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"
THUMBNAIL_UID = "1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0"


@pytest.mark.integration
@pytest.mark.timeout(timeout=60 * 3)
def test_inspect_openslide_dicom(runner: CliRunner) -> None:
    """Check expected column returned."""
    file_path = Path(__file__).parent.parent.parent / "resources" / "run" / "small-pyramidal.dcm"
    result = runner.invoke(cli, ["wsi", "inspect", str(file_path)])
    assert result.exit_code == 0
    assert all(
        index in result.output
        for index in [
            "Format: dicom",
            "MPP (x): 8.065226874391001",
            "MPP (y): 8.065226874391001",
            "Dimensions: 2054 x 1529 pixels",
            "Tile size: 256 x 256 pixels",
        ]
    )


@pytest.mark.skipif(
    sys.platform == "win32" and platform.machine().lower() == "arm64" and sys.version_info[:2] == (3, 12),
    reason="Skipping on Windows ARM with Python 3.12.x",
)
@pytest.mark.integration
@pytest.mark.timeout(timeout=60 * 3)
def test_inspect_pydicom_directory_non_verbose(runner: CliRunner) -> None:
    """Check expected column returned."""
    file_path = Path(__file__).parent.parent.parent / "resources"
    result = runner.invoke(cli, ["wsi", "dicom", "inspect", str(file_path)])
    assert result.exit_code == 0
    assert all(
        index in result.output
        for index in [
            "Study: 2.25.150973379448125660359643882019624926008",
            "Study: 2.25.5646130214350101265514421836879989792",
        ]
    )


@pytest.mark.skipif(
    platform.system() == "Windows" and platform.machine().lower() == "arm64" and sys.version_info[:2] == (3, 12),
    reason="Skipping on Windows ARM with Python 3.12.x given instability of pydicom on this platform",
)
@pytest.mark.integration
@pytest.mark.timeout(timeout=60 * 3)
def test_inspect_pydicom_directory_verbose(runner: CliRunner) -> None:
    """Check expected column returned."""
    file_path = Path(__file__).parent.parent.parent / "resources"
    result = runner.invoke(cli, ["wsi", "dicom", "inspect", "--verbose", str(file_path)])
    assert result.exit_code == 0
    assert all(
        index in result.output
        for index in [
            "Study: 2.25.150973379448125660359643882019624926008",
            "Path: small-pyramidal.dcm",
            "Size: 1.6 MB",
            "Study: 2.25.5646130214350101265514421836879989792",
            "Path: sm-thumbnail.dcm",
            "Size: 1.4 MB",
        ]
    )


@pytest.mark.skipif(
    platform.system() == "Windows" and platform.machine().lower() == "arm64" and sys.version_info[:2] == (3, 12),
    reason="Skipping on Windows ARM with Python 3.12.x given instability of pydicom on this platform",
)
@pytest.mark.integration
@pytest.mark.timeout(timeout=60 * 3)
def test_inspect_pydicom_geojson_import(runner: CliRunner) -> None:
    """Check expected column returned."""
    dicom_path = Path(__file__).parent.parent.parent / "resources" / "run" / "small-pyramidal.dcm"
    geojson_path = Path(__file__).parent.parent.parent / "resources" / "cells.json"
    result = runner.invoke(cli, ["wsi", "dicom", "geojson_import", str(dicom_path), str(geojson_path)])
    assert result.exit_code == 0
    assert all(
        index in result.output
        for index in [
            "Failed to import GeoJSON: Expecting value: line 1 column 1 (char 0)",
        ]
    )
