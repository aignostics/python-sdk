"""Common test fixtures and configuration."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:
    """Get the path to the docker compose file.

    Returns:
        str: The path to the docker compose file.
    """
    return str(Path(pytestconfig.rootdir) / "compose.yaml")
