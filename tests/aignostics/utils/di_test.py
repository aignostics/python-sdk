"""Tests for the CLI utilities."""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer

from aignostics.utils._cli import (
    _add_epilog_recursively,
    _no_args_is_help_recursively,
    prepare_cli,
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
