"""Command-line interface utilities."""

import typer


def prepare_cli(cli: typer.Typer, epilog: str) -> None:
    """
    Dynamically locate, register and prepare subcommands.

    Args:
        cli (typer.Typer): Typer instance
        epilog (str): Epilog to add

    """
    cli.info.epilog = epilog
    cli.info.no_args_is_help = True
    for command in cli.registered_commands:
        command.epilog = cli.info.epilog

    # add epilog for all subcommands
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
    Add epilog to all typers in the tree.

    Args:
        cli (typer.Typer): Typer instance

    """
    for group in cli.registered_groups:
        if isinstance(group, typer.models.TyperInfo):
            group.no_args_is_help = True
            typer_instance = group.typer_instance
            if (typer_instance is not cli) and typer_instance:
                _no_args_is_help_recursively(typer_instance)
