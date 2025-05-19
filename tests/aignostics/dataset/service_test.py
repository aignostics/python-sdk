"""Tests of the idc service."""

import subprocess
from unittest import mock

from aignostics.dataset._service import _active_processes, _cleanup_processes, _terminate_process


@mock.patch("aignostics.dataset._service._terminate_process")
def test_cleanup_processes_terminates_running_processes(mock_terminate_process: mock.MagicMock) -> None:
    """Test that _cleanup_processes terminates all running processes."""
    # Create mock processes
    mock_running_process = mock.MagicMock(spec=subprocess.Popen)
    mock_running_process.poll.return_value = None  # Process is still running

    mock_finished_process = mock.MagicMock(spec=subprocess.Popen)
    mock_finished_process.poll.return_value = 0  # Process has completed

    # Add processes to the global list
    _active_processes.clear()  # Ensure we start with an empty list
    _active_processes.extend([mock_running_process, mock_finished_process])

    # Run the cleanup function
    _cleanup_processes()

    # Verify that terminate was called only for the running process
    mock_terminate_process.assert_called_once_with(mock_running_process)
    assert mock_terminate_process.call_count == 1


@mock.patch("time.sleep")
def test_terminate_process(mock_sleep: mock.MagicMock) -> None:
    """Test that _terminate_process properly terminates a process."""
    # Create a mock process that needs to be killed after terminate
    mock_process = mock.MagicMock(spec=subprocess.Popen)
    mock_process.pid = 12345
    # Configure poll to return None first (still running) then 0 (terminated)
    mock_process.poll.side_effect = [None, None, None, None, None, None]

    # Call the function
    _terminate_process(mock_process)

    # Verify the process was terminated and then killed
    mock_process.terminate.assert_called_once()
    mock_process.kill.assert_called_once()
    assert mock_sleep.call_count == 5


@mock.patch("time.sleep")
def test_terminate_process_graceful_exit(mock_sleep: mock.MagicMock) -> None:
    """Test that _terminate_process handles graceful process termination."""
    # Create a mock process that exits after terminate
    mock_process = mock.MagicMock(spec=subprocess.Popen)
    mock_process.pid = 12345
    # Return None first, then 0 to simulate process terminating
    mock_process.poll.side_effect = [None, 0]

    # Call the function
    _terminate_process(mock_process)

    # Verify the process was terminated but not killed
    mock_process.terminate.assert_called_once()
    mock_process.kill.assert_not_called()
    assert mock_sleep.call_count == 1  # Should have slept once before detecting termination


@mock.patch("aignostics.dataset._service.logger")
def test_terminate_process_exception_handling(mock_logger: mock.MagicMock) -> None:
    """Test that _terminate_process handles exceptions properly."""
    # Create a mock process that raises an exception when terminated
    mock_process = mock.MagicMock(spec=subprocess.Popen)
    mock_process.pid = 12345
    mock_process.terminate.side_effect = Exception("Test exception")

    # Call the function
    _terminate_process(mock_process)

    # Verify the exception was logged
    mock_logger.exception.assert_called_once()
    assert "Error terminating subprocess with PID 12345" in mock_logger.exception.call_args[0][0]
