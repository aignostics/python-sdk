"""Tests to verify the CLI functionality of OE Python Template works with Docker."""

import os
import platform

import pytest

BUILT_WITH_LOVE = "built with love in Berlin"


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Docker CLI tests are not supported on Windows due to path issues."
)
@pytest.mark.skipif(
    platform.system() == "Darwin" and os.getenv("GITHUB_ACTIONS") == "true",
    reason="Docker CLI tests are not supported on Mac when running on GitHub actions.",
)
@pytest.mark.skip_with_act
@pytest.mark.xdist_group(name="docker")
@pytest.mark.docker
@pytest.mark.long_running
@pytest.mark.scheduled
def test_core_docker_cli_help_with_love(docker_services) -> None:
    """Test the CLI help command with docker services returns expected output."""
    out = docker_services._docker_compose.execute("run aignostics --help")
    out_str = out.decode("utf-8")
    assert "built with love in Berlin" in out_str
