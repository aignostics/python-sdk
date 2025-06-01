"""Tests of the notebook service and it's endpoint."""

import contextlib
import logging
import re
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from nicegui import app
from nicegui.testing import User

from aignostics.notebook._service import Service, _get_runner, _Runner
from aignostics.utils import gui_register_pages


def test_start_and_stop(caplog: pytest.LogCaptureFixture) -> None:
    """Test the server can be started and stopped with real process.

    This test actually starts and stops a real Marimo server process
    (not mocked) and verifies the log messages.

    Verifies that:
    1. The Marimo server starts successfully (URL is logged)
    2. The Marimo server is stopped correctly
    3. The service is properly shut down
    4. Attempting to start an already running server logs a warning

    Args:
        caplog: Fixture to capture log messages.
    """
    # Set log level to INFO to capture the relevant messages
    caplog.set_level(logging.INFO)
    service = None

    try:
        # Create the service
        service = Service()

        # Start the actual server (no mocking)
        server_url = service.start()

        # Verify the URL is valid
        assert server_url.startswith("http://"), f"Invalid server URL: {server_url}"

        # Stop the server
        service.stop()

        # Verify that expected log messages were captured
        log_messages = [record.message for record in caplog.records]

        # Check for server start message
        start_messages = [msg for msg in log_messages if "Marimo server started at URL" in msg]
        assert len(start_messages) > 0, "Missing log message about server starting"
        assert server_url in start_messages[0], f"Server URL {server_url} not found in log message {start_messages[0]}"

        # Check for server stop messages
        assert any("Marimo server stopped" in msg for msg in log_messages), (
            "Missing log message about Marimo server stopping"
        )
        assert any("Service stopped" in msg for msg in log_messages), "Missing log message about service stopping"

        # Clear the log records for the next part of the test
        caplog.clear()

        # Start and stop again to test restart scenarios
        service.start()
        service.stop()

        # Clear the log records for the next part of the test
        caplog.clear()

        # Start twice to check for "already running" warning
        url1 = service.start()

        # Capture warning level logs
        caplog.set_level(logging.WARNING)
        url2 = service.start()

        # Verify URLs are the same
        assert url1 == url2, "URLs from consecutive starts should be identical"

        # Check for "already running" warning
        assert any(
            "Marimo server is already running" in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        ), "Missing warning about server already running"

    finally:
        # Ensure server is stopped even if test fails
        if service is not None:
            with contextlib.suppress(ConnectionError, TimeoutError):
                service.stop()


def test_serve_notebook(user: User) -> None:
    """Test notebook serving."""
    gui_register_pages()
    client = TestClient(app)

    response = client.get("/notebook/4711?results_folder=/tmp")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "iframe" in content
    assert "iframe src" in content
    # Look for the encoded iframe in the innerHTML property
    iframe_html = re.search(r'innerHTML":"&lt;iframe src=\\"([^"]+)\\"', content)
    assert iframe_html is not None, f"iframe src not found in response: {content}"

    # Extract the URL from the iframe src attribute
    notebook_url = iframe_html.group(1)
    assert "localhost" in notebook_url, f"localhost not found in iframe src: {notebook_url}"
    assert "application_run_id=4711" in notebook_url, f"run_id not found in iframe src: {notebook_url}"


def test_startup_timeout() -> None:
    """Test handling of timeout during server startup.

    This test mocks the _server_ready.wait() method to simulate a timeout
    during server startup and verifies that an exception is raised.
    """
    runner = _Runner()

    # Ensure server is not running at start
    runner._marimo_server = None

    # Mock the server ready event to simulate timeout
    runner._server_ready = MagicMock()
    runner._server_ready.wait.return_value = False

    # Mock the stop method to verify it's called and mock other dependencies
    with (
        patch.object(runner, "stop") as mock_stop,
        patch("subprocess.Popen") as mock_popen,
        patch("pathlib.Path.is_file", return_value=True),
    ):
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        # We DON'T set runner._marimo_server = mock_process here
        # because start() will set it internally

        # Verify that a timeout raises RuntimeError
        with pytest.raises(RuntimeError, match="didn't start within 10 seconds"):
            runner.start()

        # Verify that stop was called to kill the server after timeout
        mock_stop.assert_called_once()


def test_missing_url() -> None:
    """Test handling of missing URL after server ready event is triggered.

    This test mocks the _server_ready event to return True (server ready)
    but doesn't set the _server_url, simulating a rare race condition.
    """
    runner = _Runner()

    # Mock the server ready event to return True but don't set URL
    runner._server_ready = MagicMock()
    runner._server_ready.wait.return_value = True
    runner._server_url = None

    # Mock the subprocess to avoid actually starting a server
    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # Verify that missing URL raises RuntimeError
        with pytest.raises(RuntimeError, match="URL was not set despite server ready"):
            runner.start()


def test_stop_nonrunning_server() -> None:
    """Test stopping a server that isn't running.

    Verifies that stopping a non-running server doesn't cause errors
    and logs the appropriate messages.
    """
    with patch("aignostics.notebook._service.logger") as mock_logger:
        runner = _Runner()
        runner._marimo_server = None
        runner._monitor_thread = None

        # This should not raise any exceptions
        runner.stop()

        # Verify that appropriate log messages were produced
        mock_logger.debug.assert_any_call("Marimo server is not running")
        mock_logger.debug.assert_any_call("Monitor thread is not running")
        mock_logger.info.assert_called_with("Service stopped")


def test_capture_output_no_stdout() -> None:
    """Test _capture_output method with None stdout.

    This tests the case where process.stdout is None, which should
    log a warning and return early.
    """
    with patch("aignostics.notebook._service.logger") as mock_logger:
        runner = _Runner()
        process = MagicMock()
        process.stdout = None

        # This should not raise any exceptions
        runner._capture_output(process)

        # Verify that a warning was logged
        mock_logger.warning.assert_called_once_with("Cannot capture stdout")


def test_server_url_detection() -> None:
    """Test server URL detection from output.

    This test verifies that the URL detection regex works correctly
    with different URL formats that Marimo might output.
    """
    sample_outputs = [
        "➜ URL: http://localhost:8000/app",
        "  ➜  URL: http://127.0.0.1:3000/notebook",
        "\t➜\tURL:\thttps://0.0.0.0:5000",
    ]

    url_pattern = re.compile(r"\s*➜\s+URL:\s+(https?://\S+)")

    for output in sample_outputs:
        match = url_pattern.search(output)
        assert match is not None, f"URL pattern failed to match: {output}"
        assert match.group(1).startswith("http"), f"Extracted invalid URL from: {output}"


def test_singleton_runner() -> None:
    """Test that _get_runner returns a singleton instance."""
    # Reset the singleton for testing
    import aignostics.notebook._service

    aignostics.notebook._service.runner = None

    # Get the runner twice
    runner1 = _get_runner()
    runner2 = _get_runner()

    # Verify that both variables point to the same object
    assert runner1 is runner2, "Runner is not a singleton"

    # Reset the singleton again for other tests
    aignostics.notebook._service.runner = None
