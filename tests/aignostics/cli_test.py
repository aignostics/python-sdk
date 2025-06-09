"""Tests to verify the CLI functionality of OE Python Template."""

import os
import platform
import subprocess
import sys
from importlib.util import find_spec

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from aignostics.utils import (
    __version__,
)
from tests.conftest import normalize_output

BUILT_WITH_LOVE = "built with love in Berlin"
THE_VALUE = "THE_VALUE"


def test_cli_built_with_love(runner) -> None:
    """Check epilog shown."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert BUILT_WITH_LOVE in result.output
    assert __version__ in result.output


def test_cli_fails_on_invalid_setting_with_env_arg() -> None:
    """Check system fails on boot with invalid setting using subprocess."""
    # Run the CLI as a subprocess with environment variable
    cmd = [
        sys.executable,
        "-m",
        "aignostics.cli",
        "system",
        "info",
        "--env",
        "AIGNOSTICS_LOG_LEVEL=FAIL",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        encoding="utf-8",
    )

    # Debug output for Windows issues
    print(f"DEBUG: Command: {cmd}")
    print(f"DEBUG: sys.executable: {sys.executable}")
    print(f"DEBUG: Return code: {result.returncode}")

    # Check the return code (78 indicates validation failed)
    assert result.returncode == 78
    # Check that the error message is in the stdout or stderr (handle None case for Windows)
    stdout_text = normalize_output(result.stdout or "")
    stderr_text = normalize_output(result.stderr or "")
    assert "Input should be 'CRITICAL'" in stdout_text or "Input should be 'CRITICAL'" in stderr_text


@pytest.mark.sequential
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
        result = runner.invoke(cli, ["launchpad", "--help"])
        assert result.exit_code == 0

    def test_cli_gui_run(runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        """Check gui component behaviors when launchpad command is executed."""
        # Create mocks
        mock_ui_run_called = False
        mock_ui_run_args = {}
        mock_register_pages_called = False
        mock_app_mount_called = False

        def mock_ui_run(  # noqa: PLR0913, PLR0917
            title="",
            favicon="",
            native=False,
            reload=False,
            dark=False,
            host=None,
            port=None,
            frameless=False,
            show_welcome_message=False,
            show=False,
            window_size=None,
        ):
            nonlocal mock_ui_run_called, mock_ui_run_args
            mock_ui_run_called = True
            mock_ui_run_args = {
                "title": title,
                "favicon": favicon,
                "native": native,
                "reload": reload,
                "dark": dark,
                "host": host,
                "port": port,
                "frameless": frameless,
                "show_welcome_message": show_welcome_message,
                "show": show,
                "window_size": window_size,
            }

        def mock_gui_register_pages():
            nonlocal mock_register_pages_called
            mock_register_pages_called = True

        def mock_app_mount(path, app_instance):
            nonlocal mock_app_mount_called
            mock_app_mount_called = True

        # Apply the mocks
        monkeypatch.setattr("nicegui.ui.run", mock_ui_run)
        monkeypatch.setattr("aignostics.utils._gui.gui_register_pages", mock_gui_register_pages)
        monkeypatch.setattr("nicegui.app.mount", mock_app_mount)

        # Create a mock for native_app.find_open_port()
        monkeypatch.setattr("nicegui.native.find_open_port", lambda: 8080)

        # Run the CLI command
        result = runner.invoke(cli, ["launchpad"])

        # Check that the command executed successfully
        assert result.exit_code == 0

        # Verify gui_register_pages was called
        assert mock_register_pages_called, "gui_register_pages was not called"

        # Verify that app.mount was not called (with_api is False)
        assert not mock_app_mount_called, "app.mount should not be called when with_api is False"

        # Check that ui.run was called with the expected parameters
        assert mock_ui_run_called, "ui.run was not called"
        assert mock_ui_run_args["title"] == "Aignostics Launchpad", "title parameter is incorrect"
        assert mock_ui_run_args["favicon"] == "🔬", "favicon parameter is incorrect"
        if platform.system() == "Linux":
            assert mock_ui_run_args["native"] is False, "native parameter should be False on Linux"
            assert mock_ui_run_args["show_welcome_message"] is True, (
                "show_welcome_message parameter should be True when native is False"
            )
            assert mock_ui_run_args["show"] is True, "show parameter should be True when native is False"
        else:
            assert mock_ui_run_args["native"] is True, "native parameter should be True on platforms other than Linux"
            assert mock_ui_run_args["show_welcome_message"] is False, (
                "show_welcome_message parameter should be False when native is True"
            )
            assert mock_ui_run_args["show"] is False, "show parameter should be False when native is True"
        assert mock_ui_run_args["reload"] is False, "reload parameter is incorrect"
        assert not mock_ui_run_args["dark"], "dark parameter should be False"
        if platform.system() == "Darwin":
            assert mock_ui_run_args["frameless"] is True, "frameless parameter should be True"
        else:
            assert mock_ui_run_args["frameless"] is False, "frameless parameter should be False"


if find_spec("marimo") and find_spec("fastapi"):
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
