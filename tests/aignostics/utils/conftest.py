"""Shared fixtures for utils tests."""

from __future__ import annotations

import importlib
import shutil
import site
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

DUMMY_PLUGIN_DIR = Path(__file__).resolve().parents[2] / "resources" / "mcp_dummy_plugin"


@pytest.fixture(scope="session")
def install_dummy_plugin() -> Iterator[None]:
    """Install the dummy plugin package in editable mode for the test session.

    Refreshes site-packages so the running interpreter sees the new package
    and its entry points without a process restart.

    Note: Plugin discovery caches (discover_plugin_packages, DI caches) may have
    been populated before this fixture runs. Tests that rely on post-install
    discovery must pair this fixture with clear_plugin_caches to ensure caches
    are reset before and after each test.

    Raises:
        subprocess.CalledProcessError: If install fails, or if uninstall fails for
            a reason other than the package already being absent.
    """
    uv = shutil.which("uv")
    if uv:
        install_cmd = [uv, "pip", "install", "--no-deps", "-e", str(DUMMY_PLUGIN_DIR)]
        uninstall_cmd = [uv, "pip", "uninstall", "-y", "mcp-dummy-plugin"]
    else:
        install_cmd = [sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(DUMMY_PLUGIN_DIR)]
        uninstall_cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "mcp-dummy-plugin"]

    subprocess.run(install_cmd, check=True, capture_output=True, text=True)

    importlib.invalidate_caches()
    for sp in site.getsitepackages():
        site.addsitedir(sp)

    yield

    result = subprocess.run(uninstall_cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        output = (result.stderr or result.stdout or "").lower()
        if not any(marker in output for marker in ("not installed", "no packages found")):
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
