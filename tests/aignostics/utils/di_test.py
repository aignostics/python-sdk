"""Tests for the CLI utilities and dependency injection."""

import sys
from collections.abc import Generator
from types import ModuleType
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer

from aignostics.utils._cli import (
    _add_epilog_recursively,
    _no_args_is_help_recursively,
    prepare_cli,
)
from aignostics.utils._di import (
    PLUGIN_ENTRY_POINT_GROUP,
    _implementation_cache,
    _subclass_cache,
    discover_plugin_packages,
    locate_implementations,
    locate_subclasses,
)

# Constants to avoid duplication
TEST_EPILOG = "Test epilog"
SCRIPT_FILENAME = "script.py"


@pytest.mark.unit
@patch("aignostics.utils._cli.locate_implementations")
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
@patch("aignostics.utils._cli.locate_implementations")
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
@patch("aignostics.utils._cli.Path")
@patch("aignostics.utils._cli.locate_implementations")
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
@patch("aignostics.utils._cli._add_epilog_recursively")
@patch("aignostics.utils._cli.Path")
@patch("aignostics.utils._cli.locate_implementations")
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
@patch("aignostics.utils._cli._no_args_is_help_recursively")
@patch("aignostics.utils._cli.locate_implementations")
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


class DummyBaseClass:
    """Base class for testing locate_subclasses."""


class DummySubClass(DummyBaseClass):
    """Subclass for testing locate_subclasses."""


class AnotherDummyBase:
    """Another base class for testing to avoid cache pollution."""


class AnotherDummySub(AnotherDummyBase):
    """Subclass for testing."""


another_dummy_instance = AnotherDummyBase()


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


@pytest.mark.unit
def test_discover_plugin_packages_returns_tuple(clear_di_caches, record_property) -> None:
    """Test that discover_plugin_packages returns a tuple."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
    result = discover_plugin_packages()
    assert isinstance(result, tuple)


@pytest.mark.unit
def test_discover_plugin_packages_uses_correct_entry_point_group(clear_di_caches, record_property) -> None:
    """Test that discover_plugin_packages uses the correct entry point group."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
    assert PLUGIN_ENTRY_POINT_GROUP == "aignostics.plugins"


@pytest.mark.unit
@patch("aignostics.utils._di.entry_points")
def test_discover_plugin_packages_extracts_values_from_entry_points(
    mock_entry_points: Mock, clear_di_caches, record_property
) -> None:
    """Test that discover_plugin_packages extracts values from entry points."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
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
    record_property("tested-item-id", "SPEC-UTILS-DI")
    mock_entry_points.return_value = []

    result = discover_plugin_packages()

    assert result == ()


@pytest.mark.unit
@patch("aignostics.utils._di.entry_points")
def test_discover_plugin_packages_is_cached(mock_entry_points: Mock, clear_di_caches, record_property) -> None:
    """Test that discover_plugin_packages caches results."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
    mock_ep = MagicMock()
    mock_ep.value = "cached_plugin"
    mock_entry_points.return_value = [mock_ep]

    # Call twice
    result1 = discover_plugin_packages()
    result2 = discover_plugin_packages()

    # Should only be called once due to caching
    assert mock_entry_points.call_count == 1
    assert result1 == result2 == ("cached_plugin",)


@pytest.mark.unit
def test_locate_implementations_searches_plugins(clear_di_caches, record_property) -> None:
    """Test that locate_implementations searches plugin packages."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
    import aignostics.utils._di as di_module

    plugin_instance = AnotherDummyBase()
    mock_plugin_package = MagicMock()
    mock_plugin_package.__path__ = ["/fake/path"]
    mock_plugin_module = ModuleType("test_plugin.submodule")
    mock_plugin_module.plugin_instance = plugin_instance  # type: ignore[attr-defined]

    def import_side_effect(name: str) -> ModuleType:
        if name == "test_plugin":
            return mock_plugin_package
        if name == "test_plugin.submodule":
            return mock_plugin_module
        mock_aig = MagicMock()
        mock_aig.__path__ = []
        return mock_aig

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=("test_plugin",)),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
        patch.object(di_module.pkgutil, "iter_modules", side_effect=[[("", "submodule", False)], []]),
    ):
        result = locate_implementations(AnotherDummyBase)
        assert plugin_instance in result


@pytest.mark.unit
def test_locate_implementations_caches_results(clear_di_caches, record_property) -> None:
    """Test that locate_implementations caches results."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
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
def test_locate_subclasses_searches_plugins(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses searches plugin packages."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
    import aignostics.utils._di as di_module

    class PluginSubClass(AnotherDummyBase):
        pass

    mock_plugin_package = MagicMock()
    mock_plugin_package.__path__ = ["/fake/path"]
    mock_plugin_module = ModuleType("test_plugin.submodule")
    mock_plugin_module.PluginSubClass = PluginSubClass  # type: ignore[attr-defined]

    def import_side_effect(name: str) -> ModuleType:
        if name == "test_plugin":
            return mock_plugin_package
        if name == "test_plugin.submodule":
            return mock_plugin_module
        mock_aig = MagicMock()
        mock_aig.__path__ = []
        return mock_aig

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=("test_plugin",)),
        patch.object(di_module.importlib, "import_module", side_effect=import_side_effect),
        patch.object(di_module.pkgutil, "iter_modules", side_effect=[[("", "submodule", False)], []]),
    ):
        result = locate_subclasses(AnotherDummyBase)
        assert PluginSubClass in result


@pytest.mark.unit
def test_locate_subclasses_excludes_base_class(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses excludes the base class itself."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
    import aignostics.utils._di as di_module

    mock_package = MagicMock()
    mock_package.__path__ = ["/fake/path"]
    mock_module = ModuleType("aignostics.testmodule")
    mock_module.AnotherDummyBase = AnotherDummyBase  # type: ignore[attr-defined]

    with (
        patch.object(di_module, "discover_plugin_packages", return_value=()),
        patch.object(di_module.importlib, "import_module", side_effect=[mock_package, mock_module]),
        patch.object(di_module.pkgutil, "iter_modules", return_value=[("", "testmodule", False)]),
    ):
        result = locate_subclasses(AnotherDummyBase)
        assert AnotherDummyBase not in result


@pytest.mark.unit
def test_locate_subclasses_caches_results(clear_di_caches, record_property) -> None:
    """Test that locate_subclasses caches results."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
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
    record_property("tested-item-id", "SPEC-UTILS-DI")
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
    record_property("tested-item-id", "SPEC-UTILS-DI")
    import aignostics.utils._di as di_module

    mock_package = MagicMock()
    mock_package.__path__ = ["/fake/path"]
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
def test_locate_implementations_and_subclasses_search_both_plugins_and_main_package(
    clear_di_caches,
    record_property,
) -> None:
    """Test that both functions search plugins first, then main package."""
    record_property("tested-item-id", "SPEC-UTILS-DI")
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
        assert import_order == ["plugin_a", "plugin_b", "aignostics"]

        _implementation_cache.clear()
        import_order.clear()

        locate_subclasses(AnotherDummySub)
        assert import_order == ["plugin_a", "plugin_b", "aignostics"]
