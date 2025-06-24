"""Common test fixtures and configuration."""

from __future__ import annotations

import logging
import os
from asyncio import sleep
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING

import psutil
import pytest
from typer.testing import CliRunner

from aignostics.utils import get_logger

logger = get_logger(__name__)
if TYPE_CHECKING:
    from collections.abc import Generator

    from nicegui.testing import User

# See https://nicegui.io/documentation/section_testing#project_structure
if find_spec("nicegui"):
    pytest_plugins = ("nicegui.testing.plugin",)


def normalize_output(output: str) -> str:
    r"""Normalize output by removing both Windows and Unix line endings.

    This helper function ensures cross-platform compatibility when testing CLI output
    by removing both Windows (\r\n) and Unix (\n) line endings.

    Args:
        output: The output string to normalize.

    Returns:
        str: The normalized output with line endings removed.
    """
    return output.replace("\r\n", "").replace("\n", "")


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
    pytest.fail(f"No notification containing '{expected_notification}' was found within {wait_seconds} seconds")


def pytest_collection_modifyitems(config, items) -> None:
    """Modify collected test items by skipping tests marked as 'long_running' unless matching marker given.

    Args:
        config: The pytest configuration object.
        items: The list of collected test items.
    """
    if not config.getoption("-m"):
        skip_me = pytest.mark.skip(reason="skipped as no marker given on execution using '-m'")
        for item in items:
            if "long_running" in item.keywords:
                item.add_marker(skip_me)
    elif config.getoption("-m") == "not sequential":
        skip_me = pytest.mark.skip(reason="skipped as only not sequential marker given on execution using '-m'")
        for item in items:
            if "long_running" in item.keywords:
                item.add_marker(skip_me)


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner fixture."""
    return CliRunner()


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

    Args:
        scope: The scope of the fixture.

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
