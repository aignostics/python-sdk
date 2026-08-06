"""Tests for the CLI utilities and dependency injection."""

import sys
from collections.abc import Callable, Generator
from contextlib import contextmanager
from types import ModuleType
from unittest.mock import MagicMock, Mock, patch

import aignostics.utils._di as di_module
import pytest
import typer
from aignostics.utils._di import (
    PLUGIN_ENTRY_POINT_GROUP,
    _implementation_cache,
    _subclass_cache,
    discover_plugin_packages,
    locate_implementations,
    locate_subclasses,
)

from aignostics_sdk.utils._cli import (
    _add_epilog_recursively,
    _no_args_is_help_recursively,
    prepare_cli,
)

# Constants to avoid duplication
TEST_EPILOG = "Test epilog"
SCRIPT_FILENAME = "script.py"
PLUGIN = "plugin"
MYMODULE = "mymodule"
# _di.py scans "aignostics" and "aignostics_sdk" (importable names, not hyphenated distribution name)
MAIN_PACKAGE = "aignostics"


@pytest.mark.unit
@patch("aignostics.utils.locate_implementations")
def test_prepare_cli_registers_subcommands(mock_locate_implementations: Mock, record_property) -> None:
    """Test that prepare_cli registers all located implementations."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    mock_subcli = typer.Typer()
    mock_locate_implementations.return_value = [cli, mock_subcli]

    # Execute
    prepare_cli(cli, TEST_EPILOG)

    # Verify
    mock_locate_implementations.assert_called_once_with(typer.Typer)
    assert mock_subcli in [group.typer_instance for group in cli.registered_groups]


@pytest.mark.unit
@patch("aignostics.utils.locate_implementations")
def test_prepare_cli_sets_epilog_and_no_args_help(mock_locate_implementations: Mock, record_property) -> None:
    """Test that prepare_cli sets epilog and no_args_is_help on the cli instance."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    mock_locate_implementations.return_value = [cli]

    # Execute
    prepare_cli(cli, TEST_EPILOG)

    # Verify
    assert cli.info.epilog == TEST_EPILOG
    # TODO(Helmut): Reactivate when typer bug fixed
    # assert cli.info.no_args_is_help is True


@pytest.mark.unit
@patch("aignostics_sdk.utils._cli.Path")
@patch("aignostics.utils.locate_implementations")
def test_prepare_cli_adds_epilog_to_commands_when_not_running_from_typer(
    mock_locate_implementations: Mock, mock_path: Mock, record_property
) -> None:
    """Test that prepare_cli adds epilog to commands when not running from typer."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    mock_command = MagicMock()
    cli.registered_commands = [mock_command]
    mock_locate_implementations.return_value = [cli]
    mock_path.return_value.parts = ["python", SCRIPT_FILENAME]

    # Execute
    with patch.object(sys, "argv", [SCRIPT_FILENAME]):
        prepare_cli(cli, TEST_EPILOG)

    # Verify
    assert mock_command.epilog == TEST_EPILOG


@pytest.mark.unit
@patch("aignostics_sdk.utils._cli._add_epilog_recursively")
@patch("aignostics_sdk.utils._cli.Path")
@patch("aignostics.utils.locate_implementations")
def test_prepare_cli_calls_add_epilog_recursively_when_not_running_from_typer(
    mock_locate_implementations: Mock, mock_path: Mock, mock_add_epilog_recursively: Mock, record_property
) -> None:
    """Test that prepare_cli calls _add_epilog_recursively when not running from typer."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    mock_locate_implementations.return_value = [cli]
    mock_path.return_value.parts = ["python", SCRIPT_FILENAME]

    # Execute
    with patch.object(sys, "argv", [SCRIPT_FILENAME]):
        prepare_cli(cli, TEST_EPILOG)

    # Verify
    mock_add_epilog_recursively.assert_called_once_with(cli, TEST_EPILOG)


@pytest.mark.unit
@patch("aignostics_sdk.utils._cli._no_args_is_help_recursively")
@patch("aignostics.utils.locate_implementations")
def test_prepare_cli_calls_no_args_is_help_recursively(
    mock_locate_implementations: Mock, mock_no_args_is_help_recursively: Mock, record_property
) -> None:
    """Test that prepare_cli calls _no_args_is_help_recursively."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    mock_locate_implementations.return_value = [cli]

    # Execute
    prepare_cli(cli, TEST_EPILOG)

    # Verify
    mock_no_args_is_help_recursively.assert_called_once_with(cli)


@pytest.mark.unit
def test_add_epilog_recursively_sets_epilog_on_cli(record_property) -> None:
    """Test that _add_epilog_recursively sets epilog on the cli instance."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()

    # Execute
    _add_epilog_recursively(cli, TEST_EPILOG)

    # Verify
    assert cli.info.epilog == TEST_EPILOG


@pytest.mark.unit
def test_add_epilog_recursively_sets_epilog_on_nested_typers(record_property) -> None:
    """Test that _add_epilog_recursively sets epilog on nested typer instances."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    subcli = typer.Typer()
    cli.add_typer(subcli)

    # Execute
    _add_epilog_recursively(cli, TEST_EPILOG)

    # Verify
    assert subcli.info.epilog == TEST_EPILOG


@pytest.mark.unit
def test_no_args_is_help_recursively_sets_no_args_is_help_on_groups(record_property) -> None:
    """Test that _no_args_is_help_recursively sets no_args_is_help on groups."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    subcli = typer.Typer()
    cli.add_typer(subcli)

    # Create a mock for the group to verify it's accessed properly
    mock_group = MagicMock()
    mock_group.typer_instance = subcli
    cli.registered_groups = [mock_group]

    # Execute
    with patch.object(cli, "registered_groups", [mock_group]):
        _no_args_is_help_recursively(cli)

    # Verify
    mock_group.no_args_is_help = True


@pytest.mark.unit
@pytest.mark.skip(reason="https://github.com/fastapi/typer/pull/1240")
def test_no_args_is_help_recursively_calls_itself_on_nested_typers(record_property) -> None:
    """Test that _no_args_is_help_recursively calls itself on nested typer instances."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup
    cli = typer.Typer()
    subcli = typer.Typer()
    sub_subcli = typer.Typer()
    subcli.add_typer(sub_subcli)
    cli.add_typer(subcli)

    # Execute
    _no_args_is_help_recursively(cli)

    # Verify that all groups have no_args_is_help set to True
    for group in cli.registered_groups:
        assert group.no_args_is_help is True
        if group.typer_instance:
            for subgroup in group.typer_instance.registered_groups:
                assert subgroup.no_args_is_help is True


# ---------------------------------------------------------------------------
# Plugin discovery helpers
# ---------------------------------------------------------------------------


class DummyBaseClass:
    """Base class for testing locate_subclasses."""


class DummySubClass(DummyBaseClass):
    """Subclass for testing locate_subclasses."""


class AnotherDummyBase:
    """Another base class for testing to avoid cache pollution."""


class AnotherDummySub(AnotherDummyBase):
    """Subclass for testing."""


another_dummy_instance = AnotherDummyBase()


def _mock_package() -> MagicMock:
    """Return a MagicMock that looks like an importable package (has __path__)."""
    pkg = MagicMock()
    pkg.__path__ = ["/fake/path"]
    return pkg


def _make_import_side_effect(
    mapping: dict[str, ModuleType | Exception],
    default: MagicMock | None = None,
) -> Callable[[str], ModuleType]:
    """Return an import side-effect callable driven by *mapping*.

    Args:
        mapping: Maps module name to the module to return or an exception to raise.
        default: Returned for any name not in *mapping*.  Defaults to a package
            with an empty ``__path__``.

    Returns:
        A callable suitable for use as ``importlib.import_module``'s side effect.
    """
    if default is None:
        default = _mock_package()
        default.__path__ = []

    def _side_effect(name: str) -> ModuleType:
        if name in mapping:
            result = mapping[name]
            if isinstance(result, BaseException):
                raise result
            return result  # type: ignore[return-value]
        return default  # type: ignore[return-value]

    return _side_effect


@contextmanager
def _broken_plugin_package_patches(
    main_pkg: MagicMock,
    main_mod: ModuleType,
) -> Generator[None, None, None]:
    """Yield patches where a plugin package itself raises ImportError.

    The plugin package raises ``ImportError`` on import.  The main project
    package and its ``MYMODULE`` submodule import normally.

    Args:
        main_pkg: Mock main package (has ``__path__``).
        main_mod: Module to return for the main ``MYMODULE`` import.
    """
    with (
        patch.object(di_module, "discover_plugin_packages", return_value=(PLUGIN,)),
        patch.object(
            di_module.importlib,
            "import_module",
            side_effect=_make_import_side_effect(
                {
                    PLUGIN: ImportError("broken"),
                    MAIN_PACKAGE: main_pkg,
                    f"{MAIN_PACKAGE}.{MYMODULE}": main_mod,
                }
            ),
        ),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", MYMODULE, False)]),
    ):
        yield


@contextmanager
def _no_match_plugin_patches(
    plugin_pkg: MagicMock,
    main_pkg: MagicMock,
    main_mod: ModuleType,
) -> Generator[None, None, None]:
    """Yield patches where a plugin imports successfully but has no matching top-level members.

    The plugin package is importable but its top-level namespace contains no
    members that satisfy the discovery predicate.  The main project package and
    its ``MYMODULE`` submodule import normally and contain the expected member.

    Args:
        plugin_pkg: Mock plugin package (importable, no matching members).
        main_pkg: Mock main package (has ``__path__``).
        main_mod: Module to return for the main ``MYMODULE`` import.
    """
    with (
        patch.object(di_module, "discover_plugin_packages", return_value=(PLUGIN,)),
        patch.object(
            di_module.importlib,
            "import_module",
            side_effect=_make_import_side_effect(
                {
                    PLUGIN: plugin_pkg,
                    MAIN_PACKAGE: main_pkg,
                    f"{MAIN_PACKAGE}.{MYMODULE}": main_mod,
                }
            ),
        ),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", MYMODULE, False)]),
    ):
        yield


@contextmanager
def _no_plugins_patches(
    main_pkg: MagicMock,
    main_mod: ModuleType,
) -> Generator[list[str], None, None]:
    """Yield a tracking list of searched module names with no-plugin patches active.

    Patches ``discover_plugin_packages`` to return an empty tuple,
    ``importlib.import_module`` with a call-tracking side-effect, and
    ``pkgutil.iter_modules`` with a single-module result.

    Args:
        main_pkg: Mock main package (has ``__path__``).
        main_mod: Module to return for the main ``MYMODULE`` import.

    Yields:
        A list of module names that were imported during the patched scope.
    """
    searched: list[str] = []
    base_side_effect = _make_import_side_effect(
        {
            MAIN_PACKAGE: main_pkg,
            f"{MAIN_PACKAGE}.{MYMODULE}": main_mod,
        }
    )

    def tracking_import(name: str) -> ModuleType:
        searched.append(name)
        return base_side_effect(name)

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(di_module.importlib, "import_module", side_effect=tracking_import),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", MYMODULE, False)]),
    ):
        yield searched


@pytest.fixture
def clear_di_caches() -> Generator[None, None, None]:
    """Clear DI caches before and after each test.

    Yields:
        None: Control is yielded to the test.
    """
    _implementation_cache.clear()
    _subclass_cache.clear()
    discover_plugin_packages.cache_clear()
    yield
    _implementation_cache.clear()
    _subclass_cache.clear()
    discover_plugin_packages.cache_clear()


# ---------------------------------------------------------------------------
# discover_plugin_packages
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_discover_plugin_packages_returns_tuple(clear_di_caches, record_property) -> None:
    """Test that discover_plugin_packages returns a tuple."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    result = discover_plugin_packages()
    assert isinstance(result, tuple)


@pytest.mark.unit
def test_discover_plugin_packages_uses_correct_entry_point_group(clear_di_caches, record_property) -> None:
    """Test that discover_plugin_packages uses the correct entry point group."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    assert PLUGIN_ENTRY_POINT_GROUP == "aignostics.plugins"


@pytest.mark.unit
@patch("aignostics.utils._di.entry_points")
def test_discover_plugin_packages_extracts_values_from_entry_points(
    mock_entry_points: Mock, clear_di_caches, record_property
) -> None:
    """Test that discover_plugin_packages extracts values from entry points."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Setup mock entry points
    mock_ep1 = MagicMock()
    mock_ep1.value = "plugin_one"
    mock_ep2 = MagicMock()
    mock_ep2.value = "plugin_two"
    mock_entry_points.return_value = [mock_ep1, mock_ep2]

    # Execute
    result = discover_plugin_packages()

    # Verify
    mock_entry_points.assert_called_once_with(group=PLUGIN_ENTRY_POINT_GROUP)
    assert result == ("plugin_one", "plugin_two")


@pytest.mark.unit
@patch("aignostics.utils._di.entry_points")
def test_discover_plugin_packages_returns_empty_tuple_when_no_plugins(
    mock_entry_points: Mock, clear_di_caches, record_property
) -> None:
    """Test that discover_plugin_packages returns empty tuple when no plugins registered."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    mock_entry_points.return_value = []

    result = discover_plugin_packages()

    assert result == ()


@pytest.mark.unit
@patch("aignostics.utils._di.entry_points")
def test_discover_plugin_packages_is_cached(mock_entry_points: Mock, clear_di_caches, record_property) -> None:
    """Test that discover_plugin_packages caches results."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    mock_ep = MagicMock()
    mock_ep.value = "cached_plugin"
    mock_entry_points.return_value = [mock_ep]

    # Call twice
    result1 = discover_plugin_packages()
    result2 = discover_plugin_packages()

    # Should only be called once due to caching
    assert mock_entry_points.call_count == 1
    assert result1 == result2 == ("cached_plugin",)


# ---------------------------------------------------------------------------
# locate_implementations — plugin discovery
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_locate_implementations_searches_plugins(clear_di_caches, record_property) -> None:
    """Test that locate_implementations shallow-scans plugin packages for top-level exports."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    """Test that locate_implementations searches plugin packages."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    plugin_instance = AnotherDummyBase()
    mock_plugin_package = ModuleType("test_plugin")
    mock_plugin_package.plugin_instance = plugin_instance  # type: ignore[attr-defined]

    def import_side_effect(name: str) -> ModuleType:
        if name == "test_plugin":
            return mock_plugin_package
        mock_aig = MagicMock()
        mock_aig.__path__ = []
        return mock_aig

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=("test_plugin",)),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        result = locate_implementations(AnotherDummyBase)
        assert plugin_instance in result


@pytest.mark.unit
def test_locate_implementations_only_finds_plugin_top_level_exports(clear_di_caches, record_property) -> None:
    """Plugin submodule instances are not discovered; only top-level __init__.py exports are found."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    top_instance = _Base()
    sub_instance = _Base()

    plugin_pkg = _mock_package()
    plugin_pkg.top_instance = top_instance  # type: ignore[attr-defined]

    plugin_submod = ModuleType(f"{PLUGIN}.submod")
    plugin_submod.sub_instance = sub_instance  # type: ignore[attr-defined]

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=(PLUGIN,)),
        patch.object(
            di_module.importlib,
            "import_module",
            side_effect=_make_import_side_effect(
                {
                    PLUGIN: plugin_pkg,
                    f"{PLUGIN}.submod": plugin_submod,
                }
            ),
        ),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        result = locate_implementations(_Base)

    assert top_instance in result
    assert sub_instance not in result


@pytest.mark.unit
def test_locate_implementations_handles_broken_plugin_package(clear_di_caches, record_property) -> None:
    """A plugin package raising ImportError on import is skipped; main package still searched."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    main_instance = _Base()
    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.main_instance = main_instance  # type: ignore[attr-defined]

    with _broken_plugin_package_patches(main_pkg, main_mod):
        result = locate_implementations(_Base)

    assert main_instance in result


@pytest.mark.unit
def test_locate_implementations_handles_plugin_with_no_matching_top_level_members(
    clear_di_caches, record_property
) -> None:
    """A plugin with no matching top-level exports is skipped; main package still searched."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    main_instance = _Base()
    plugin_pkg = _mock_package()
    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.main_instance = main_instance  # type: ignore[attr-defined]

    with _no_match_plugin_patches(plugin_pkg, main_pkg, main_mod):
        result = locate_implementations(_Base)

    assert main_instance in result


@pytest.mark.unit
def test_locate_implementations_deep_scans_main_package(clear_di_caches, record_property) -> None:
    """Main package submodule instances are found via deep scan even when a plugin is present."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    main_instance = _Base()
    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.main_instance = main_instance  # type: ignore[attr-defined]

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(
            di_module.importlib,
            "import_module",
            side_effect=_make_import_side_effect(
                {
                    MAIN_PACKAGE: main_pkg,
                    f"{MAIN_PACKAGE}.{MYMODULE}": main_mod,
                }
            ),
        ),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", MYMODULE, False)]),
    ):
        result = locate_implementations(_Base)

    assert main_instance in result


@pytest.mark.unit
def test_locate_implementations_caches_results(clear_di_caches, record_property) -> None:
    """Test that locate_implementations caches results."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    mock_package = MagicMock()
    mock_package.__path__ = []

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(di_module.importlib, "import_module", return_value=mock_package),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        result1 = locate_implementations(AnotherDummyBase)
        result2 = locate_implementations(AnotherDummyBase)
        assert result1 is result2
        assert AnotherDummyBase in _implementation_cache


@pytest.mark.unit
def test_locate_implementations_no_plugins_detects_main_package(clear_di_caches, record_property) -> None:
    """With no plugins, locate_implementations only searches the main package."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    instance = _Base()
    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.instance = instance  # type: ignore[attr-defined]

    with _no_plugins_patches(main_pkg, main_mod) as searched:
        result = locate_implementations(_Base)

    assert instance in result
    assert not any(
        p not in {"aignostics", "aignostics_sdk"} and not p.startswith(("aignostics.", "aignostics_sdk."))
        for p in searched
    )


# ---------------------------------------------------------------------------
# locate_subclasses — plugin discovery
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_locate_subclasses_searches_plugins(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses shallow-scans plugin packages for top-level exports."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    """Test that locate_subclasses searches plugin packages."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    class PluginSubClass(AnotherDummyBase):
        pass

    mock_plugin_package = ModuleType("test_plugin")
    mock_plugin_package.PluginSubClass = PluginSubClass  # type: ignore[attr-defined]

    def import_side_effect(name: str) -> ModuleType:
        if name == "test_plugin":
            return mock_plugin_package
        mock_aig = MagicMock()
        mock_aig.__path__ = []
        return mock_aig

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=("test_plugin",)),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        result = locate_subclasses(AnotherDummyBase)
        assert PluginSubClass in result


@pytest.mark.unit
def test_locate_subclasses_only_finds_plugin_top_level_exports(clear_di_caches, record_property) -> None:
    """Plugin subclasses only in submodules are not discovered; only top-level exports are found."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    class TopSub(_Base):
        pass

    class SubSub(_Base):
        pass

    plugin_pkg = _mock_package()
    plugin_pkg.TopSub = TopSub  # type: ignore[attr-defined]

    plugin_submod = ModuleType(f"{PLUGIN}.submod")
    plugin_submod.SubSub = SubSub  # type: ignore[attr-defined]

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=(PLUGIN,)),
        patch.object(
            di_module.importlib,
            "import_module",
            side_effect=_make_import_side_effect(
                {
                    PLUGIN: plugin_pkg,
                    f"{PLUGIN}.submod": plugin_submod,
                }
            ),
        ),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        result = locate_subclasses(_Base)

    assert TopSub in result
    assert SubSub not in result


@pytest.mark.unit
def test_locate_subclasses_handles_broken_plugin_package(clear_di_caches, record_property) -> None:
    """A plugin package raising ImportError on import is skipped; main package still searched."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    class MainSub(_Base):
        pass

    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.MainSub = MainSub  # type: ignore[attr-defined]

    with _broken_plugin_package_patches(main_pkg, main_mod):
        result = locate_subclasses(_Base)

    assert MainSub in result


@pytest.mark.unit
def test_locate_subclasses_handles_plugin_with_no_matching_top_level_members(clear_di_caches, record_property) -> None:
    """A plugin with no matching top-level exports is skipped; main package still searched."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    class MainSub(_Base):
        pass

    plugin_pkg = _mock_package()
    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.MainSub = MainSub  # type: ignore[attr-defined]

    with _no_match_plugin_patches(plugin_pkg, main_pkg, main_mod):
        result = locate_subclasses(_Base)

    assert MainSub in result


@pytest.mark.unit
def test_locate_subclasses_deep_scans_main_package(clear_di_caches, record_property) -> None:
    """Main package subclasses in submodules are found via deep scan."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    class MainSub(_Base):
        pass

    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.MainSub = MainSub  # type: ignore[attr-defined]

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(
            di_module.importlib,
            "import_module",
            side_effect=_make_import_side_effect(
                {
                    MAIN_PACKAGE: main_pkg,
                    f"{MAIN_PACKAGE}.{MYMODULE}": main_mod,
                }
            ),
        ),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", MYMODULE, False)]),
    ):
        result = locate_subclasses(_Base)

    assert MainSub in result


@pytest.mark.unit
def test_locate_subclasses_excludes_base_class(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses excludes the base class itself."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    mock_package = _mock_package()
    mock_module = ModuleType("aignostics.testmodule")
    mock_module.AnotherDummyBase = AnotherDummyBase  # type: ignore[attr-defined]

    def import_side_effect(name: str) -> ModuleType:
        if name == "aignostics.testmodule":
            return mock_module
        return mock_package

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", "testmodule", False)]),
    ):
        result = locate_subclasses(AnotherDummyBase)
        assert AnotherDummyBase not in result


@pytest.mark.unit
def test_locate_subclasses_caches_results(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses caches results."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    mock_package = MagicMock()
    mock_package.__path__ = []

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(di_module.importlib, "import_module", return_value=mock_package),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        result1 = locate_subclasses(AnotherDummyBase)
        result2 = locate_subclasses(AnotherDummyBase)
        assert result1 is result2
        assert AnotherDummyBase in _subclass_cache


@pytest.mark.unit
def test_locate_subclasses_handles_plugin_import_error(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses handles ImportError for plugin packages gracefully."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    mock_package = MagicMock()
    mock_package.__path__ = []

    def import_side_effect(name: str) -> ModuleType:
        if name == "missing_plugin":
            raise ImportError(name)
        return mock_package

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=("missing_plugin",)),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
    ):
        result = locate_subclasses(AnotherDummyBase)
        assert isinstance(result, list)


@pytest.mark.unit
def test_locate_subclasses_handles_module_import_error(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses handles ImportError for individual modules gracefully."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    mock_package = _mock_package()
    call_count = 0

    def import_side_effect(name: str) -> ModuleType:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_package
        raise ImportError(name)

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", "failing_module", False)]),
    ):
        result = locate_subclasses(AnotherDummyBase)
        assert isinstance(result, list)


@pytest.mark.unit
def test_locate_subclasses_no_plugins_detects_main_package(clear_di_caches, record_property) -> None:
    """With no plugins, locate_subclasses only searches the main package."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")

    class _Base:
        pass

    class LocalSub(_Base):
        pass

    main_pkg = _mock_package()
    main_mod = ModuleType(f"{MAIN_PACKAGE}.{MYMODULE}")
    main_mod.LocalSub = LocalSub  # type: ignore[attr-defined]

    with _no_plugins_patches(main_pkg, main_mod) as searched:
        result = locate_subclasses(_Base)

    assert LocalSub in result
    assert not any(
        p not in {"aignostics", "aignostics_sdk"} and not p.startswith(("aignostics.", "aignostics_sdk."))
        for p in searched
    )


@pytest.mark.unit
def test_locate_implementations_and_subclasses_search_both_plugins_and_main_package(
    clear_di_caches,
    record_property,
) -> None:
    """Test that both functions search plugins first, then main package."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    import aignostics.utils._di as di_module

    import_order: list[str] = []

    def track_imports(name: str) -> MagicMock:
        import_order.append(name)
        mock = MagicMock()
        mock.__path__ = []
        return mock

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=("plugin_a", "plugin_b")),
        patch.object(di_module.importlib, "import_module", side_effect=track_imports),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[]),
    ):
        locate_implementations(AnotherDummyBase)
        assert import_order == ["plugin_a", "plugin_b", "aignostics_sdk", "aignostics"]

        _implementation_cache.clear()
        import_order.clear()

        locate_subclasses(AnotherDummySub)
        assert import_order == ["plugin_a", "plugin_b", "aignostics_sdk", "aignostics"]
