"""Tests to verify the CLI functionality of Aignostics Python SDK."""

import pytest
from typer.testing import CliRunner

from aignostics import (
    __version__,
)
from aignostics.cli import cli

BUILT_WITH_LOVE = "built with love in Berlin"


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


def test_cli_built_with_love(runner) -> None:
    """Check epilog shown."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert BUILT_WITH_LOVE in result.output
    assert __version__ in result.output


@pytest.mark.scheduled
def test_cli_health(runner: CliRunner) -> None:
    """Check health is true."""
    result = runner.invoke(cli, ["platform", "health"])
    assert result.exit_code == 0
    assert "True" in result.output


def test_cli_info(runner: CliRunner) -> None:
    """Check info command returns system information."""
    result = runner.invoke(cli, ["platform", "info"])
    assert result.exit_code == 0
    assert "CPython" in result.output


def test_cli_info_full(runner: CliRunner) -> None:
    """Check info command returns system information."""
    result = runner.invoke(cli, ["platform", "info", "--env", "--no-filter-secrets"])
    assert result.exit_code == 0
    assert "HOME" in result.output


def test_cli_openapi_yaml(runner: CliRunner) -> None:
    """Check openapi command outputs YAML schema."""
    result = runner.invoke(cli, ["platform", "openapi"])
    assert result.exit_code == 0
    # Check for common OpenAPI YAML elements
    assert "openapi:" in result.output
    assert "info:" in result.output
    assert "paths:" in result.output


def test_cli_openapi_json(runner: CliRunner) -> None:
    """Check openapi command outputs JSON schema."""
    result = runner.invoke(cli, ["platform", "openapi", "--output-format", "json"])
    assert result.exit_code == 0
    # Check for common OpenAPI JSON elements
    assert '"openapi":' in result.output
    assert '"info":' in result.output
    assert '"paths":' in result.output


def test_cli_install(runner: CliRunner) -> None:
    """Check install command runs successfully."""
    result = runner.invoke(cli, ["platform", "install"])
    assert result.exit_code == 0


def test_cli_bucket_ls(runner: CliRunner) -> None:
    """Check bucket ls command runs successfully."""
    result = runner.invoke(cli, ["platform", "bucket", "ls"])
    assert result.exit_code == 0
    assert "bucket ls" in result.output


def test_cli_bucket_purge(runner: CliRunner) -> None:
    """Check bucket purge command runs successfully."""
    result = runner.invoke(cli, ["platform", "bucket", "purge"])
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
