"""Tests to verify the CLI functionality of the system module."""

import logging
import re

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

THE_VALUE = "THE_VALUE"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


@pytest.mark.scheduled
def test_cli_columns(runner: CliRunner) -> None:
    """Check expected column returned."""
    result = runner.invoke(cli, ["idc", "columns"])
    assert result.exit_code == 0
    assert "Modality" in result.output


@pytest.mark.scheduled
def test_cli_query(runner: CliRunner) -> None:
    """Check query returns expected results."""
    result = runner.invoke(cli, ["idc", "query"])
    assert result.exit_code == 0
    assert "rows x 1 columns" in result.output
    # Verify the number of rows is greater than 100000
    match = re.search(r"\[(\d+) rows x", result.output)
    assert match is not None, f"Could not find row count in output: {result.output}"
    num_rows = int(match.group(1))
    assert num_rows > 100000, f"Expected more than 100000 rows, but got {num_rows}"


# @pytest.mark.scheduled
def test_cli_download(runner: CliRunner, caplog, tmp_path) -> None:
    """Check download functionality with dry-run option."""
    caplog.set_level(logging.INFO)
    result = runner.invoke(
        cli,
        ["idc", "download", "1.3.6.1.4.1.5962.99.1.1042652702.25371455.1637425225246.2.0", str(tmp_path), "--dry-run"],
    )
    assert result.exit_code == 0
    for record in caplog.records:
        assert record.levelname != "ERROR"  # if id would not be found, error would be logged
