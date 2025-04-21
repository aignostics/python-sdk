"""Tests to verify the CLI functionality of OE Python Template."""

import os
import subprocess
import sys
from importlib.util import find_spec

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import (
    __version__,
)

BUILT_WITH_LOVE = "built with love in Berlin"
THE_VALUE = "THE_VALUE"


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


def test_cli_fails_on_invalid_setting_with_env_arg() -> None:
    """Check system fails on boot with invalid setting using subprocess."""
    # Run the CLI as a subprocess with environment variable
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aignostics.cli",
            "system",
            "info",
            "--env",
            "AIGNOSTICS_LOG_LEVEL=FAIL",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # Check the return code (78 indicates validation failed)
    assert result.returncode == 78
    # Check that the error message is in the stderr
    assert "Input should be 'CRITICAL'" in result.stdout


def test_cli_fails_on_invalid_setting_with_environ(runner) -> None:
    """Check system fails on boot with invalid setting using CliRunner and environment variables."""
    # Set the environment variable directly
    with runner.isolated_filesystem():
        # Set environment variable for the test
        env = os.environ.copy()
        env["AIGNOSTICS_LOG_LEVEL"] = "DEBUG"

        # custom
        env["AIGNOSTICS_CLIENT_ID_DEVICE"] = THE_VALUE
        env["AIGNOSTICS_CLIENT_ID_INTERACTIVE"] = THE_VALUE
        # end custon

        # Run the CLI with the runner
        result = runner.invoke(cli, ["system", "info"], env=env)

        # Check the exit code (0 indicates all good)
        assert result.exit_code == 0

        # Set environment variable for the test
        env = os.environ.copy()
        env["AIGNOSTICS_LOG_LEVEL"] = "FAIL"

        # custom
        env["AIGNOSTICS_CLIENT_ID_DEVICE"] = THE_VALUE
        env["AIGNOSTICS_CLIENT_ID_INTERACTIVE"] = THE_VALUE
        # end custon

        # Run the CLI with the runner
        result = runner.invoke(cli, ["system", "info"], env=env)

        # Check the exit code (78 indicates validation failed)
        assert result.exit_code == 78
        # Check that the error message is in the output
        assert "Input should be 'CRITICAL'" in result.output


if find_spec("nicegui"):

    def test_cli_gui_help(runner: CliRunner) -> None:
        """Check gui help works."""
        result = runner.invoke(cli, ["gui", "--help"])
        assert result.exit_code == 0

    def test_cli_gui_run(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        """Check gui_run called with expected parameters on gui start."""
        # Create a mock for gui_run
        mock_called = False
        mock_args = {}

        def mock_gui_run(  # noqa: PLR0913, PLR0917
            native=False, show=False, host=None, port=None, title="", icon="", watch=False, with_api=False
        ):
            nonlocal mock_called, mock_args
            mock_called = True
            mock_args = {
                "native": native,
                "show": show,
                "host": host,
                "port": port,
                "title": title,
                "icon": icon,
                "watch": watch,
                "with_api": with_api,
            }

        # Apply the mock to the gui_run function
        monkeypatch.setattr("aignostics.utils.gui_run", mock_gui_run)

        # Run the CLI command
        result = runner.invoke(cli, ["gui"])

        # Check that the command executed successfully
        assert result.exit_code == 0

        # Check that gui_run was called
        assert mock_called, "gui_run was not called"

        # Check that gui_run was called with the expected arguments
        assert mock_args["native"] is True, "native parameter should be True"
        assert mock_args["with_api"] is False, "with_api parameter should be False"
        assert mock_args["title"] == "Aignostics Python SDK", "title parameter is incorrect"
        assert mock_args["icon"] == "🔬", "icon parameter is incorrect"


if find_spec("marimo"):
    from fastapi import FastAPI

    def test_cli_notebook_help(runner: CliRunner) -> None:
        """Check notebook help works."""
        result = runner.invoke(cli, ["notebook", "--help"])
        assert result.exit_code == 0

    def test_cli_notebook_run(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        """Check uvicorn.run is called with FastAPI app from the notebook service."""
        # Create a mock for uvicorn.run to capture the app instance
        mock_called = False
        mock_args = {}

        def mock_uvicorn_run(app, host=None, port=None):
            """Mock uvicorn.run function that captures the arguments."""
            nonlocal mock_called, mock_args
            mock_called = True
            mock_args = {
                "app": app,
                "host": host,
                "port": port,
            }

        # Apply the mock to uvicorn.run
        monkeypatch.setattr("uvicorn.run", mock_uvicorn_run)

        # Create a mock for the Service._settings.directory.is_dir to avoid errors
        monkeypatch.setattr("pathlib.Path.is_dir", lambda _: True)

        # Run the CLI command
        result = runner.invoke(cli, ["notebook"])

        # Check that the command executed successfully
        assert result.exit_code == 0

        # Check that uvicorn.run was called
        assert mock_called, "uvicorn.run was not called"

        # Check that uvicorn.run was called with the expected arguments
        assert isinstance(mock_args["app"], FastAPI), "uvicorn.run was not called with a FastAPI app"
        assert mock_args["host"] == "127.0.0.1", "host parameter is incorrect"
        assert mock_args["port"] == 8001, "port parameter is incorrect"
