"""Tests to verify the CLI functionality of Aignostics Python SDK."""

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_bucket_ls(runner: CliRunner) -> None:
    """Check bucket ls command runs successfully."""
    result = runner.invoke(cli, ["application", "bucket", "ls"])
    assert result.exit_code == 0
    assert "bucket ls" in result.output


def test_cli_bucket_purge(runner: CliRunner) -> None:
    """Check bucket purge command runs successfully."""
    result = runner.invoke(cli, ["application", "bucket", "purge"])
    assert result.exit_code == 0
    assert "bucket purged" in result.output


def test_cli_application_list(runner: CliRunner) -> None:
    """Check application list command runs successfully."""
    result = runner.invoke(cli, ["application", "list"])
    assert result.exit_code == 0


def test_cli_application_describe(runner: CliRunner) -> None:
    """Check application describe command runs successfully."""
    result = runner.invoke(cli, ["application", "describe"])
    assert result.exit_code == 0


def test_cli_dataset_download(runner: CliRunner) -> None:
    """Check dataset download command runs successfully."""
    result = runner.invoke(cli, ["application", "dataset", "download"])
    assert result.exit_code == 0
    assert "dataset download" in result.output


def test_cli_metadata_generate(runner: CliRunner) -> None:
    """Check metadata generate command runs successfully."""
    result = runner.invoke(cli, ["application", "metadata", "generate"])
    assert result.exit_code == 0
    assert "generate metadata" in result.output


def test_cli_run_submit(runner: CliRunner) -> None:
    """Check run submit command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "submit"])
    assert result.exit_code == 0
    assert "submit run" in result.output


# TODO(Andreas): Check, just call uv run aignostics application run list
@pytest.mark.skip(reason="This test is skipped because it fails with inconsistent auth stated.")
def test_cli_run_list(runner: CliRunner) -> None:
    """Check run list command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "list"])
    assert result.exit_code == 0


def test_cli_run_describe(runner: CliRunner) -> None:
    """Check run describe command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "describe"])
    assert result.exit_code == 0
    assert "The run" in result.output


def test_cli_run_cancel(runner: CliRunner) -> None:
    """Check run cancel command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "cancel"])
    assert result.exit_code == 0
    assert "canceled run" in result.output


def test_cli_run_result_describe(runner: CliRunner) -> None:
    """Check run result describe command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "describe"])
    assert result.exit_code == 0
    assert "describe result" in result.output


def test_cli_run_result_download(runner: CliRunner) -> None:
    """Check run result download command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "download"])
    assert result.exit_code == 0
    assert "download result" in result.output


def test_cli_run_result_delete(runner: CliRunner) -> None:
    """Check run result delete command runs successfully."""
    result = runner.invoke(cli, ["application", "run", "result", "delete"])
    assert result.exit_code == 0
    assert "delete resuilt" in result.output
