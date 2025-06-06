"""Tests to verify the CLI functionality of the dataset module."""

import logging
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

SERIES_UID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"
THUMBNAIL_UID = "1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_idc_indices(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["dataset", "idc", "indices"])
    assert result.exit_code == 0
    assert all(
        index in result.output
        for index in ["index", "prior_versions_index", "sm_index", "sm_instance_index", "clinical_index"]
    )


def test_cli_idc_columns_default_index(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["dataset", "idc", "columns"])
    assert result.exit_code == 0
    assert "SOPInstanceUID" in result.output


def test_cli_columns_special_index(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["dataset", "idc", "columns", "--index", "index"])
    assert result.exit_code == 0
    assert "series_aws_url" in result.output


def test_cli_idc_query(runner: CliRunner) -> None:
    """Check query returns expected results."""
    result = runner.invoke(cli, ["dataset", "idc", "query"])
    assert result.exit_code == 0
    assert "rows x 6 columns" in result.output
    # Verify the number of rows is greater than 100000
    match = re.search(r"\[(\d+) rows x", result.output)
    assert match is not None, f"Could not find row count in output: {result.output}"
    num_rows = int(match.group(1))
    assert num_rows >= 50421, f"Expected equal or more than 50421 rows, but got {num_rows}"


def test_cli_idc_download_series_dry(runner: CliRunner, caplog, tmp_path) -> None:
    """Check download functionality with dry-run option."""
    caplog.set_level(logging.INFO)
    result = runner.invoke(
        cli,
        [
            "dataset",
            "idc",
            "download",
            SERIES_UID,
            str(tmp_path),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    for record in caplog.records:
        assert record.levelname != "ERROR"  # if id would not be found, error would be logged


def test_cli_idc_download_instance_thumbnail(runner: CliRunner, caplog, tmpdir) -> None:
    """Check download functionality with dry-run option."""
    caplog.set_level(logging.INFO)
    result = runner.invoke(
        cli,
        [
            "dataset",
            "idc",
            "download",
            THUMBNAIL_UID,
            str(tmpdir),
        ],
    )
    assert result.exit_code == 0
    for record in caplog.records:
        assert record.levelname != "ERROR"  # if id would not be found, error would be logged

    expected_file = (
        Path(tmpdir)
        / "tcga_luad"
        / "TCGA-91-6830"
        / "2.25.5646130214350101265514421836879989792"
        / "SM_1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.2.0"
        / "975bc2fa-d403-4c4c-affa-0fbb08475651.dcm"
    )

    assert expected_file.exists(), f"Expected file {expected_file} not found"
    assert expected_file.stat().st_size == 1369290, (
        f"File size {expected_file.stat().st_size} doesn't match expected 1369290 bytes"
    )


def test_cli_aignostics_download_sample(runner: CliRunner, tmp_path: Path) -> None:
    """Check download functionality with dry-run option."""
    result = runner.invoke(
        cli,
        [
            "dataset",
            "aignostics",
            "download",
            "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    # Check that the output contains the successful download message
    # Use a simpler pattern that just checks for the key phrase and filename, regardless of formatting
    assert "Successfully downloaded" in result.stdout
    assert "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff" in result.stdout

    # Verify the file exists in the tmpdir
    expected_file = tmp_path / "9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
    assert expected_file.exists(), f"Expected file {expected_file} not found"
    assert expected_file.stat().st_size == 14681750
