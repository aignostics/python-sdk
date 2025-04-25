"""Common test fixtures and configuration."""

import os
from importlib.util import find_spec
from pathlib import Path

import pytest

# See https://nicegui.io/documentation/section_testing#project_structure
if find_spec("nicegui"):
    pytest_plugins = ("nicegui.testing.plugin",)


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
