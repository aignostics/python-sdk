"""Shared fixtures for utils tests."""

from __future__ import annotations

import importlib
import shutil
import site
import subprocess
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
    """
    uv = shutil.which("uv") or "uv"
    subprocess.run(
        [uv, "pip", "install", "--no-deps", "-e", str(DUMMY_PLUGIN_DIR)],
        check=True,
        capture_output=True,
        text=True,
    )

    importlib.invalidate_caches()
    for sp in site.getsitepackages():
        site.addsitedir(sp)

    yield

    subprocess.run(
        [uv, "pip", "uninstall", "-y", "mcp-dummy-plugin"],
        check=False,  # best-effort: if already absent, that's fine
        capture_output=True,
        text=True,
    )
