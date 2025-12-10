"""Module for dynamic import and discovery of implementations and subclasses."""

import importlib
import pkgutil
from functools import lru_cache
from importlib.metadata import entry_points
from inspect import isclass
from typing import Any

from ._constants import __project_name__

_implementation_cache: dict[Any, list[Any]] = {}
_subclass_cache: dict[Any, list[Any]] = {}

# Entry point group name for aignostics plugins
PLUGIN_ENTRY_POINT_GROUP = "aignostics.plugins"


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
    package = importlib.import_module(__project_name__)
    for _, name, _ in pkgutil.iter_modules(package.__path__):
        importlib.import_module(f"{__project_name__}.{name}")


def locate_implementations(_class: type[Any]) -> list[Any]:
    """
    Dynamically discover all instances of some class.

    Searches in the main project and all plugins registered via entry points.

    Args:
        _class (type[Any]): Class to search for.

    Returns:
        list[Any]: List of discovered implementations of the given class.
    """
    if _class in _implementation_cache:
        return _implementation_cache[_class]

    plugin_packages = discover_plugin_packages()

    implementations = []
    for package_name in [*plugin_packages, __project_name__]:
        package = importlib.import_module(package_name)

        for _, name, _ in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{package_name}.{name}")
            # Check all members of the module
            for member_name in dir(module):
                member = getattr(module, member_name)
                if isinstance(member, _class):
                    implementations.append(member)

    _implementation_cache[_class] = implementations
    return implementations


def locate_subclasses(_class: type[Any]) -> list[Any]:
    """
    Dynamically discover all classes that are subclasses of some type.

    Searches in the main project and all plugins registered via entry points.

    Args:
        _class (type[Any]): Parent class of subclasses to search for.

    Returns:
        list[type[Any]]: List of discovered subclasses of the given class.
    """
    if _class in _subclass_cache:
        return _subclass_cache[_class]

    plugin_packages = discover_plugin_packages()

    subclasses = []
    for package_name in [*plugin_packages, __project_name__]:
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            continue

        for _, name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{name}")
                # Check all members of the module
                for member_name in dir(module):
                    member = getattr(module, member_name)
                    if isclass(member) and issubclass(member, _class) and member != _class:
                        subclasses.append(member)
            except ImportError:
                continue

    _subclass_cache[_class] = subclasses
    return subclasses
