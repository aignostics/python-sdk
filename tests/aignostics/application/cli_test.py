"""Tests to verify the CLI functionality of the appliction module."""

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"
MESSAGE_RUN_NOT_FOUND = "Warning: Run with ID '4711' not found"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_application_list(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list"])
    assert result.exit_code == 0
    assert "he-tme" in result.output
    assert "test-app" in result.output


def test_cli_application_list_verbose(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list", "--verbose"])
    assert result.exit_code == 0
    assert "he-tme" in result.output
    assert "Artifacts: 1 input(s), 6 output(s)" in result.output
    assert "test-app" in result.output


def test_cli_application_describe(runner: CliRunner) -> None:
    """Check application describe command runs successfully."""
    result = runner.invoke(cli, ["application", "describe", "--application-id", "he-tme"])
    assert result.exit_code == 0
    assert "tissue_qc:geojson_polygons" in result.output


def test_cli_application_metadata_generate(runner: CliRunner) -> None:
    """Check application metadata generate command runs successfully."""
    result = runner.invoke(cli, ["application", "metadata", "generate"])
    assert result.exit_code == 0
    assert MESSAGE_NOT_YET_IMPLEMENTED in result.output


def test_cli_run_submit(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command runs successfully."""
    csv_content = "source;checksum_crc32c;base_mpp;width;height;cancer.type;cancer.tissue\n"
    csv_content += "gs://bucket/test;5onqtA==;0.26268186053789266;7447;7196;lung;lung"
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli, ["application", "run", "submit", "--application-version-id", "he-tme:v0.45.0", "--source", str(csv_path)]
    )

    assert result.exit_code == 0
    assert re.search(
        r"submitted run with id 'Application run `[0-9a-f-]+`:\s+running, 1 items - \(1/0/0\)", result.output
    ), f"Output '{result.output}' doesn't match expected pattern"


def test_cli_run_list_limit_10(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list", "--limit", "10"])
    assert result.exit_code == 0
    assert "Application Run IDs:" in result.output


def test_cli_run_list_verbose_limit_1(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list", "--verbose", "--limit", "1"])
    assert result.exit_code == 0
    assert "Application Runs:" in result.output
    assert "Item Status Counts:" in result.output
    assert "Displayed 1 application runs." in result.output


def test_cli_run_describe_not_found(runner: CliRunner) -> None:
    """Check run describe command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "describe", "--run-id", "4711"])
    assert result.exit_code == 0
    assert "Failed to retrieve run details for ID '4711'" in result.output


def test_cli_run_cancel_not_found(runner: CliRunner) -> None:
    """Check run cancel command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "cancel", "--run-id", "4711"])
    assert result.exit_code == 0
    assert "Failed to cancel run with ID '4711'" in result.output


def test_cli_run_result_describe(runner: CliRunner) -> None:
    """Check run result describe command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "describe"])
    assert result.exit_code == 0
    assert MESSAGE_NOT_YET_IMPLEMENTED in result.output


def test_cli_run_result_download_not_found(runner: CliRunner, tmp_path: Path) -> None:
    """Check run result download command runs successfully."""
    result = runner.invoke(
        cli, ["application", "run", "result", "download", "--run-id", "4711", "--destination", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "Failed to download results for run with ID '4711'" in result.output


def test_cli_run_result_delete(runner: CliRunner) -> None:
    """Check run result delete command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "delete"])
    assert result.exit_code == 0
    assert MESSAGE_NOT_YET_IMPLEMENTED in result.output
