"""Command-line interface utilities."""

import sys
from pathlib import Path

import typer

from ._di import locate_implementations


def prepare_cli(cli: typer.Typer, epilog: str) -> None:
    """
    Dynamically locate, register and prepare subcommands.

    Args:
        cli (typer.Typer): Typer instance
        epilog (str): Epilog to add
    """
    for _cli in locate_implementations(typer.Typer):
        if _cli != cli:
            cli.add_typer(_cli)

    cli.info.epilog = epilog
    cli.info.no_args_is_help = True
    if not any(arg.endswith("typer") for arg in Path(sys.argv[0]).parts):
        for command in cli.registered_commands:
            command.epilog = cli.info.epilog

    # add epilog for all subcommands
    if not any(arg.endswith("typer") for arg in Path(sys.argv[0]).parts):
        _add_epilog_recursively(cli, epilog)

    # add no_args_is_help for all subcommands
    _no_args_is_help_recursively(cli)


def _add_epilog_recursively(cli: typer.Typer, epilog: str) -> None:
    """
    Add epilog to all typers in the tree.

    Args:
        cli (typer.Typer): Typer instance
        epilog (str): Epilog to add
    """
    cli.info.epilog = epilog
    for group in cli.registered_groups:
        if isinstance(group, typer.models.TyperInfo):
            typer_instance = group.typer_instance
            if (typer_instance is not cli) and typer_instance:
                _add_epilog_recursively(typer_instance, epilog)
    for command in cli.registered_commands:
        if isinstance(command, typer.models.CommandInfo):
            command.epilog = cli.info.epilog


def _no_args_is_help_recursively(cli: typer.Typer) -> None:
    """
    Show help if no command is given by the user.

    Args:
        cli (typer.Typer): Typer instance
    """
    for group in cli.registered_groups:
        if isinstance(group, typer.models.TyperInfo):
            group.no_args_is_help = True
            typer_instance = group.typer_instance
            if (typer_instance is not cli) and typer_instance:
                _no_args_is_help_recursively(typer_instance)
