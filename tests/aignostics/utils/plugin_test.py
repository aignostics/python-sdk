"""Integration tests for plugin CLI and GUI registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import typer
from aignostics_sdk.utils import BaseNavBuilder
from aignostics_sdk.utils._di import _implementation_cache, _subclass_cache, discover_plugin_packages

if TYPE_CHECKING:
    from collections.abc import Iterator


def _clear_plugin_caches() -> None:
    """Clear DI caches so plugin discovery starts fresh."""
    _implementation_cache.pop(typer.Typer, None)
    _subclass_cache.pop(BaseNavBuilder, None)
    discover_plugin_packages.cache_clear()


@pytest.fixture
def clear_plugin_caches() -> Iterator[None]:
    """Clear plugin DI caches before and after each test."""
    _clear_plugin_caches()
    yield
    _clear_plugin_caches()


@pytest.mark.integration
@pytest.mark.sequential
@pytest.mark.timeout(timeout=60)
def test_plugin_cli_registered(install_dummy_plugin, clear_plugin_caches, record_property) -> None:
    """Integration: plugin Typer CLI instance is discovered via DI after installation."""
    record_property("tested-item-id", "TC-UTILS-PLUGIN-02")

    from aignostics_sdk.utils._di import locate_implementations

    typer_instances = locate_implementations(typer.Typer)
    names = [t.info.name for t in typer_instances if hasattr(t, "info") and t.info.name]

    assert "dummy-plugin" in names


@pytest.mark.integration
@pytest.mark.sequential
@pytest.mark.timeout(timeout=60)
def test_plugin_nav_builder_registered(install_dummy_plugin, clear_plugin_caches, record_property) -> None:
    """Integration: plugin BaseNavBuilder subclass is discovered via DI after installation."""
    record_property("tested-item-id", "TC-UTILS-PLUGIN-03")

    from aignostics_sdk.utils import gui_get_nav_groups
    from aignostics_sdk.utils._di import locate_subclasses

    nav_builder_classes = locate_subclasses(BaseNavBuilder)
    class_names = [cls.__name__ for cls in nav_builder_classes]
    assert "DummyPluginNavBuilder" in class_names

    nav_groups = gui_get_nav_groups()
    group_names = [g.name for g in nav_groups]
    assert "Dummy Plugin" in group_names
