"""Module for dynamic import and discovery of implementations and subclasses."""

import importlib
import pkgutil
from collections.abc import Callable
from functools import lru_cache
from importlib.metadata import entry_points
from inspect import isclass
from typing import Any

from ._constants import _package_name

_implementation_cache: dict[Any, list[Any]] = {}
_subclass_cache: dict[Any, list[Any]] = {}

# Entry point group name for aignostics plugins
PLUGIN_ENTRY_POINT_GROUP = "aignostics.plugins"

# Packages to deep-scan for DI discovery.
# Scans the full "aignostics" package if installed (handled gracefully via ImportError).
# Does NOT scan the slim package (aignostics_sdk) itself for typer instances — slim CLI
# commands are wired into the heavy CLI via [project.entry-points."aignostics.cli"].
# BaseService subclasses in the slim package ARE scanned (needed for health checks etc.)
_SCAN_PACKAGES = (_package_name, "aignostics")


@lru_cache(maxsize=1)
def discover_plugin_packages() -> tuple[str, ...]:
    """
    Discover plugin packages using entry points.

    Plugins register themselves in their pyproject.toml:

        [project.entry-points."aignostics.plugins"]
        my_plugin = "my_plugin"

    Results are cached after the first call.

    Returns:
        tuple[str, ...]: Tuple of discovered plugin package names.
    """
    eps = entry_points(group=PLUGIN_ENTRY_POINT_GROUP)
    return tuple(ep.value for ep in eps)


def load_modules() -> None:
    """Load all top-level modules from all scan packages."""
    for pkg_name in _SCAN_PACKAGES:
        try:
            package = importlib.import_module(pkg_name)
        except ImportError:
            continue
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            try:
                importlib.import_module(f"{pkg_name}.{name}")
            except ImportError:
                continue


def _scan_packages_deep(package_name: str, predicate: Callable[[object], bool]) -> list[Any]:
    """
    Deep-scan a package by walking all top-level submodules via pkgutil.iter_modules.

    Discovers objects by importing the package, iterating through all submodules,
    and checking each module's members against the predicate. Used for the main
    aignostics package to ensure all registered implementations are found.

    Example:
        >>> from inspect import isclass
        >>> _scan_packages_deep("aignostics", lambda m: isclass(m))

    Args:
        package_name (str): Name of the package to deep-scan.
        predicate (Callable[[object], bool]): Function to filter members.

    Returns:
        list[Any]: List of members matching the predicate.
    """
    results: list[Any] = []
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        return results

    for _, name, _ in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(f"{package_name}.{name}")
            for member_name in dir(module):
                member = getattr(module, member_name)
                if predicate(member):
                    results.append(member)
        except ImportError:
            continue

    return results


def _scan_packages_shallow(package_names: tuple[str, ...], predicate: Callable[[object], bool]) -> list[Any]:
    """
    Shallow-scan plugin packages by checking only top-level exports.

    Discovers objects by importing each package and checking its top-level members
    (i.e. what is exported from __init__.py via dir(package)) against the predicate.
    Does NOT walk submodules via pkgutil.iter_modules. This prevents over-discovering
    objects from plugin submodules that happen to be imported internally.

    Args:
        package_names (tuple[str, ...]): Names of the plugin packages to shallow-scan.
        predicate (Callable[[object], bool]): Function to filter members.

    Returns:
        list[Any]: List of members matching the predicate.
    """
    results: list[Any] = []
    for package_name in package_names:
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            continue

        for member_name in dir(package):
            member = getattr(package, member_name)
            if predicate(member):
                results.append(member)

    return results


def locate_implementations(_class: type[Any]) -> list[Any]:
    """
    Dynamically discover all instances of some class.

    Searches plugin packages using a shallow scan and the main project package using
    a deep scan.

    Args:
        _class (type[Any]): Class to search for.

    Returns:
        list[Any]: List of discovered implementations of the given class.
    """
    if _class in _implementation_cache:
        return _implementation_cache[_class]

    def predicate(member: object) -> bool:
        return isinstance(member, _class)

    results = [
        *_scan_packages_shallow(discover_plugin_packages(), predicate),
        *(item for pkg in _SCAN_PACKAGES for item in _scan_packages_deep(pkg, predicate)),
    ]

    _implementation_cache[_class] = results
    return results


def locate_subclasses(_class: type[Any]) -> list[Any]:
    """
    Dynamically discover all classes that are subclasses of some type.

    Searches plugin packages using a shallow scan and the main project package using
    a deep scan.

    Args:
        _class (type[Any]): Parent class of subclasses to search for.

    Returns:
        list[type[Any]]: List of discovered subclasses of the given class.
    """
    if _class in _subclass_cache:
        return _subclass_cache[_class]

    def predicate(member: object) -> bool:
        return isclass(member) and issubclass(member, _class) and member != _class

    results = [
        *_scan_packages_shallow(discover_plugin_packages(), predicate),
        *(item for pkg in _SCAN_PACKAGES for item in _scan_packages_deep(pkg, predicate)),
    ]

    _subclass_cache[_class] = results
    return results
