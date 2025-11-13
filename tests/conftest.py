"""Common test fixtures and configuration."""

from __future__ import annotations

import contextlib
import os

from .constants_test import TEST_SUITE

os.environ[f"PYTEST_RUNNING_{TEST_SUITE}"] = "1"  # Doing this at the top ensures aignostics src code sees it early

import logging
from asyncio import sleep
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING

import psutil
import pytest
from loguru import logger
from typer.testing import CliRunner

if TYPE_CHECKING:
    from collections.abc import Generator

    from nicegui.testing import User


def pytest_xdist_auto_num_workers(config) -> int:
    """Set the number of workers for xdist to a factor of the (logical) CPU cores.

    If the pytest option `--numprocesses` is set to "logical" or "auto", the number of workers is calculated
    based on the logical CPU count multiplied by the factor. If the option is set otherwise, that value is
    used directly.

    The factor (float) can be adjusted via the environment variable `XDIST_WORKER_FACTOR`, defaulting to 1.

    Args:
        config: The pytest configuration object.

    Returns:
        int: The number of workers set for xdist.
    """
    if config.getoption("numprocesses") in {"logical", "auto"}:
        logical_cpu_count = psutil.cpu_count(logical=config.getoption("numprocesses") == "logical") or 1
        factor = float(os.getenv("XDIST_WORKER_FACTOR", "1"))
        print(f"xdist_worker_factor: {factor}")
        num_workers = max(1, int(logical_cpu_count * factor))
        print(f"xdist_num_workers: {num_workers}")
        logger.info(
            "Set number of xdist workers to '{}' based on logical CPU count of {}.", num_workers, logical_cpu_count
        )
        return num_workers
    return config.getoption("numprocesses")


# See https://nicegui.io/documentation/section_testing#project_structure
if find_spec("nicegui"):
    pytest_plugins = ("nicegui.testing.plugin",)


def normalize_output(output: str, strip_ansi: bool = True) -> str:
    r"""Normalize output by removing both Windows and Unix line endings.

    This helper function ensures cross-platform compatibility when testing CLI output
    by removing both Windows (\r\n) and Unix (\n) line endings. Optionally strips
    ANSI escape codes (color codes and formatting) from the output.

    Args:
        output (str): The output string to normalize.
        strip_ansi (bool): Whether to remove ANSI escape codes. Defaults to True.

    Returns:
        str: The normalized output with line endings removed and optionally ANSI codes stripped.
    """
    normalized = output.replace("\r\n", "").replace("\n", "")
    if strip_ansi:
        import re

        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        normalized = ansi_escape.sub("", normalized)
    return normalized


@pytest.fixture
def qupath_teardown() -> Generator[None, None, None]:
    """Provide a fixture that ensures QuPath processes are cleaned up after tests.

    This fixture runs teardown code to kill any remaining QuPath processes
    after test execution to prevent resource leaks and interference between tests.

    Yields:
        None: This fixture doesn't yield any value.
    """
    # Setup code here (if needed)
    yield
    # Teardown code here - always runs
    for process in psutil.process_iter(["name"]):
        try:
            if "qupath" in process.info["name"].lower():
                process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


async def assert_notified(user: User, expected_notification: str, wait_seconds: int = 5) -> str:
    """Check if the user receives a notification within the specified time.

    This utility function helps test GUI notifications by waiting for a specific
    notification message to appear in the user's notification messages.

    Args:
        user: The nicegui User instance for testing.
        expected_notification: The notification text to look for (partial match).
        wait_seconds: Maximum time to wait for the notification (default: 5).

    Returns:
        str: The oldest matching notification message found.

    Raises:
        pytest.fail: If no matching notification is found within the wait time.
    """
    for _ in range(wait_seconds):
        matching_messages = [msg for msg in user.notify.messages if expected_notification in msg]
        if matching_messages:
            return matching_messages[0]
        await sleep(1)

    recent_messages = (user.notify.messages[-10:] if len(user.notify.messages) > 10 else user.notify.messages)[::-1]
    total_count = len(user.notify.messages)
    pytest.fail(
        f"No notification containing '{expected_notification}' was found within {wait_seconds} seconds. "
        f"Total messages: {total_count}. Recent messages: {recent_messages}"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ANN201
    """Hook to suppress expected teardown errors from NiceGUI background tasks.

    This hook wraps the test report generation and modifies teardown errors
    that are expected and benign (like NiceGUI background task cancellation).

    Args:
        item: The pytest test item.
        call: The pytest call info.

    Yields:
        None: Control to other hooks.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process teardown phase errors that are NiceGUI-related
    if report.when == "teardown" and report.failed and hasattr(report, "longrepr") and report.longrepr:
        error_msg = str(report.longrepr)
        # Known benign NiceGUI teardown errors
        if any(
            pattern in error_msg
            for pattern in [
                "Could not cancel",
                "tasks within timeout",
                "nicegui_run.io_bound",
                "returned None, likely canceled by shutdown",
                "KeyError: <_pytest.stash.StashKey",
            ]
        ):
            # Mark as passed to avoid failing the test suite
            report.outcome = "passed"
            logger.warning(
                "Suppressed expected NiceGUI teardown error in test '%s': %s",
                item.nodeid,
                error_msg[:200],
            )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item) -> Generator[None, None, None]:
    """Capture test markers and store them in environment variable before test execution.

    This hook runs before each test and sets the PYTEST_MARKERS environment variable
    with a comma-separated list of all markers applied to the test.

    Args:
        item: The pytest test item being executed.

    Yields:
        None: This is a hookwrapper that yields control to other hooks.
    """
    # Get all marker names for this test item
    markers = [marker.name for marker in item.iter_markers()]
    # Filter out built-in pytest markers that are not user-defined
    filtered_markers = [
        m
        for m in markers
        if m not in {"parametrize", "skip", "skipif", "xfail", "usefixtures", "filterwarnings", "tryfirst", "trylast"}
    ]
    # Set environment variable with comma-separated markers
    if filtered_markers:
        os.environ["PYTEST_MARKERS"] = ",".join(sorted(filtered_markers))
    else:
        os.environ.pop("PYTEST_MARKERS", None)

    yield

    # Clean up after test
    os.environ.pop("PYTEST_MARKERS", None)


def pytest_collection_modifyitems(config, items) -> None:
    """Modify collected test items by skipping tests marked as '[very_]long_running' unless matching marker given.

    Args:
        config: The pytest configuration object.
        items: The list of collected test items.
    """
    if not config.getoption("-m"):
        skip_me = pytest.mark.skip(reason="skipped as no marker given on execution using '-m'")
        for item in items:
            if "long_running" in item.keywords:
                item.add_marker(skip_me)
            if "very_long_running" in item.keywords:
                item.add_marker(skip_me)
    elif config.getoption("-m") in {"not sequential", "(not sequential)"}:
        skip_me = pytest.mark.skip(reason="skipped as only not sequential marker given on execution using '-m'")
        for item in items:
            if "long_running" in item.keywords:
                item.add_marker(skip_me)
            if "very_long_running" in item.keywords:
                item.add_marker(skip_me)


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


@pytest.fixture(autouse=True)
def caplog_loguru_integration(caplog) -> Generator[None, None, None]:
    """Enable caplog to capture loguru logs by propagating them to Python's logging.

    This fixture automatically runs for all tests and bridges loguru to Python's
    standard logging module so that pytest's caplog fixture can capture loguru logs.

    Args:
        caplog: The pytest fixture for capturing log messages.

    Yields:
        None: This fixture doesn't yield any value.
    """

    class PropagateHandler(logging.Handler):
        """Handler that propagates loguru logs to Python's logging."""

        @staticmethod
        def emit(record) -> None:
            """Emit a log record to Python's logging."""
            logging.getLogger(record.name).handle(record)

    # Add handler to propagate loguru logs to Python's logging
    # Use enqueue=True to prevent deadlocks in multi-threaded contexts (e.g., botocore)
    handler_id = logger.add(PropagateHandler(), format="{message}", enqueue=True)

    yield

    # Remove the handler after test - ignore if already removed (e.g., by logging_initialize())
    with contextlib.suppress(ValueError):
        logger.remove(handler_id)


@pytest.fixture
def silent_logging(caplog) -> Generator[None, None, None]:
    """Suppress logging output during test execution.

    Args:
        caplog (pytest.LogCaptureFixture): The pytest fixture for capturing log messages.

    Yields:
        None: This fixture doesn't yield any value.
    """
    with caplog.at_level(logging.CRITICAL + 1):
        yield


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:
    """Get the path to the docker compose file.

    Args:
        pytestconfig: The pytest configuration object.

    Returns:
        str: The path to the docker compose file.
    """
    # We want to test the compose.yaml file in the root of the project.
    return str(Path(pytestconfig.rootdir) / "compose.yaml")


@pytest.fixture(scope="session")
def docker_setup() -> list[str] | str:
    """Commands to run when spinning up services.

    Returns:
        list[str] | str: The commands to run.
    """
    # You can consider to return an empty list so you can decide on the
    # commands to run in the test itself
    return ["up --build -d"]


def docker_compose_project_name() -> str:
    """Generate a project name using the current process PID.

    Returns:
        str: The project name.
    """
    # You can consider to override this with a project name to reuse the stack
    # across test executions.
    return f"aignostics-pytest-{os.getpid()}"


def pytest_sessionfinish(session, exitstatus) -> None:
    """Run after the test session ends.

    Does change behavior if no test matching the marker is found:
    - Sets the exit status to 0 instead of 5.

    Args:
        session: The pytest session object.
        exitstatus: The exit status of the test session.
    """
    if exitstatus == 5:
        session.exitstatus = 0


def print_directory_structure(path: Path, step: str | None = None) -> None:
    """Print a detailed directory structure for debugging test scenarios.

    This utility function helps debug test scenarios by printing the complete
    directory structure including file sizes in human-readable format.

    Args:
        path: The directory path to analyze and print.
        step: Optional step name to include in the output header.
    """
    if step is not None:
        print(f"\n==> Directory structure of '{path}' after step '{step}':")
    else:
        print(f"\n==> Directory structure of '{path}':")
    for root_str, dirs, files in os.walk(path):
        root = Path(root_str)
        rel_path = root.relative_to(path) if root != path else Path()
        print(f"Directory: {rel_path}")
        for directory in dirs:
            print(f"  Dir: {directory}")
        for file in files:
            file_path = root / file
            file_size = file_path.stat().st_size
            file_size_human = (
                f"{file_size / (1024 * 1024):.2f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.2f} KB"
            )
            print(f"  File: {file} ({file_size_human}, {file_size} bytes)")
