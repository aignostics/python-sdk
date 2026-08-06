"""Smoke tests for the aignostics-sdk slim package.

These tests verify the slim distribution works in isolation:
- Correct imports resolve
- Core constants are accessible

Note: The aignostics-sdk CLI entry point (aignostics_sdk.cli) is pending
PYSDK-137 (CLI carve-out). The test_slim_cli_entry_point test is marked
xfail until that phase lands.

Note: Dependency slimming (removal of heavy deps such as openslide, nicegui,
etc.) is pending PYSDK-138 (dependency split). Until that phase merges,
aignostics-sdk carries the full dependency tree.
"""

from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.unit
@pytest.mark.slim
def test_platform_client_importable() -> None:
    """Core import from aignostics_sdk.platform works."""
    from aignostics_sdk.platform import Client

    assert Client is not None


@pytest.mark.unit
@pytest.mark.slim
def test_utils_importable() -> None:
    """Core imports from aignostics_sdk.utils work."""
    from aignostics_sdk.utils import BaseService, Health

    assert BaseService is not None
    assert Health is not None


@pytest.mark.unit
@pytest.mark.slim
def test_aignx_codegen_importable() -> None:
    """Bundled codegen is accessible."""
    from aignostics_sdk._codegen.exceptions import ApiException

    assert ApiException is not None


@pytest.mark.unit
@pytest.mark.slim
def test_slim_cli_entry_point() -> None:
    """aignostics-sdk CLI entry point exits 0."""
    result = subprocess.run(
        [sys.executable, "-m", "aignostics_sdk.cli", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0
    assert "user" in result.stdout
    assert "sdk" in result.stdout
    assert "application" in result.stdout
    assert "system" in result.stdout


@pytest.mark.unit
@pytest.mark.slim
def test_project_name_preserved() -> None:
    """__project_name__ is the slim distribution name; ENV_PREFIX preserves backward compat for env vars."""
    from aignostics_sdk.utils._constants import ENV_PREFIX, __project_name__

    assert __project_name__ == "aignostics-sdk"
    assert ENV_PREFIX == "AIGNOSTICS"


@pytest.mark.unit
@pytest.mark.slim
def test_version_available() -> None:
    """Package version is accessible."""
    from aignostics_sdk.utils._constants import __version__

    assert __version__ is not None
    assert len(__version__) > 0
