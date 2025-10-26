"""Tests to verify the CLI functionality of the dataset module."""

import logging
import re
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from tests.conftest import normalize_output

SERIES_UID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"
THUMBNAIL_UID = "1.3.6.1.4.1.5962.99.1.1038911754.1238045814.1637421484298.15.0"

# Don't use tmp_path with flaky, see https://github.com/str0zzapreti/pytest-retry/issues/46


@pytest.mark.integration
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 2)
def test_cli_idc_indices(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["dataset", "idc", "indices"])
    assert result.exit_code == 0
    assert all(
        index in result.output
        for index in ["index", "prior_versions_index", "sm_index", "sm_instance_index", "clinical_index"]
    )


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 2)
def test_cli_idc_columns_default_index(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["dataset", "idc", "columns"])
    assert result.exit_code == 0
    assert "SOPInstanceUID" in result.output


@pytest.mark.integration
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60)
def test_cli_columns_special_index(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["dataset", "idc", "columns", "--index", "index"])
    assert result.exit_code == 0
    assert "series_aws_url" in result.output


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 2)
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


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 2)
def test_cli_idc_download_series_dry(runner: CliRunner, caplog) -> None:
    """Check download functionality with dry-run option."""
    caplog.set_level(logging.INFO)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(
            cli,
            [
                "dataset",
                "idc",
                "download",
                SERIES_UID,
                tmpdir,
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        for record in caplog.records:
            assert record.levelname != "ERROR"  # if id would not be found, error would be logged


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 2)
def test_cli_idc_download_instance_thumbnail(runner: CliRunner, caplog) -> None:
    """Check download functionality with dry-run option."""
    caplog.set_level(logging.INFO)
    with tempfile.TemporaryDirectory() as tmpdir:
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


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60 * 2)
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


@pytest.mark.integration
def test_idc_indices_error_handling(runner: CliRunner) -> None:
    """Test that idc indices command properly displays error messages."""
    error_message = "Mock error: Failed to connect to IDC"

    with patch("aignostics.third_party.idc_index.IDCClient.client") as mock_client:
        mock_client.side_effect = RuntimeError(error_message)
        result = runner.invoke(cli, ["dataset", "idc", "indices"])

        assert result.exit_code == 1
        # Check that key parts of the error message appear in output
        assert "Mock error" in normalize_output(result.output)
        assert "Failed to connect to IDC" in normalize_output(result.output)


@pytest.mark.integration
def test_idc_columns_error_handling(runner: CliRunner) -> None:
    """Test that idc columns command properly displays error messages."""
    error_message = "Mock error: Invalid index name"

    with patch("aignostics.third_party.idc_index.IDCClient.client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.fetch_index.side_effect = ValueError(error_message)
        mock_client.return_value = mock_instance

        result = runner.invoke(cli, ["dataset", "idc", "columns", "--index", "invalid_index"])

        assert result.exit_code == 1
        # Check that key parts of the error message appear in output
        assert "Mock error" in normalize_output(result.output)
        assert "Invalid index name" in normalize_output(result.output)
        assert "invalid_index" in normalize_output(result.output)


@pytest.mark.integration
def test_idc_query_error_handling(runner: CliRunner) -> None:
    """Test that idc query command properly displays error messages."""
    error_message = "Mock error: SQL query failed"
    test_query = "SELECT * FROM invalid_table"

    with patch("aignostics.third_party.idc_index.IDCClient.client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.sql_query.side_effect = RuntimeError(error_message)
        mock_client.return_value = mock_instance

        result = runner.invoke(cli, ["dataset", "idc", "query", test_query])

        assert result.exit_code == 1
        # Check that key parts of the error message appear in output
        assert "Mock error" in normalize_output(result.output)
        # "SQL query failed" may be split across lines by rich console formatting
        assert "SQL query failed" in normalize_output(result.output)


@pytest.mark.integration
def test_idc_download_error_handling(runner: CliRunner, tmp_path: Path) -> None:
    """Test that idc download command properly displays error messages."""
    error_message = "Mock error: Download failed"
    test_id = "test-series-id"

    with patch("aignostics.third_party.idc_index.IDCClient.client") as mock_client:
        mock_client.side_effect = RuntimeError(error_message)

        result = runner.invoke(
            cli,
            [
                "dataset",
                "idc",
                "download",
                test_id,
                str(tmp_path),
            ],
        )

        assert result.exit_code == 1
        # Check that key parts of the error message appear in output
        assert "Mock error" in normalize_output(result.output)
        assert "Download failed" in normalize_output(result.output)
        assert test_id in normalize_output(result.output)


@pytest.mark.integration
def test_aignostics_download_error_handling(runner: CliRunner, tmp_path: Path) -> None:
    """Test that aignostics download command properly displays error messages."""
    error_message = "Mock error: Failed to download from bucket"
    test_url = "gs://test-bucket/test-file.tiff"

    with patch("aignostics.dataset._service.platform_generate_signed_url") as mock_generate_url:
        mock_generate_url.side_effect = RuntimeError(error_message)

        result = runner.invoke(
            cli,
            [
                "dataset",
                "aignostics",
                "download",
                test_url,
                str(tmp_path),
            ],
        )

        assert result.exit_code == 1
        # Check that key parts of the error message appear in output
        assert "Mock error" in normalize_output(result.output)
        assert "Failed to download from bucket" in normalize_output(result.output)
        assert test_url in normalize_output(result.output)
