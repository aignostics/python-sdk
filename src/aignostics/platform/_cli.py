"""CLI of platform module."""

import json
import sys
from typing import Annotated

import typer

from aignostics.utils import console, get_logger

from ._service import Service

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"

logger = get_logger(__name__)

cli = typer.Typer(name="platform", help="Operations for interaction with Aignostics Platform.")

service = Service()


@cli.command("logout")
def logout() -> None:
    """Logout if authenticated.

    - Deletes the cached authentication token if existing.
    """
    try:
        if service.logout():
            console.print("Successfully logged out.")
        else:
            console.print("Was not logged in.", style="warning")
            sys.exit(2)
    except Exception as e:
        message = f"Error during logout: {e!s}"
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command("login")
def login(
    relogin: Annotated[bool, typer.Option(help="Re-login")] = False,
) -> None:
    """(Re)login."""
    try:
        if service.login(relogin=relogin):
            console.print("Successfully logged in.")
        else:
            console.print("Failed to log you in.", style="error")
            sys.exit(1)
    except Exception as e:
        message = f"Error during login: {e!s}"
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command("whoami")
def whoami(
    relogin: Annotated[bool, typer.Option(help="Re-login")] = False,
) -> None:
    """Print user info."""
    try:
        user_info = service.get_user_info(relogin=relogin)
        if user_info is None:
            console.print("Failed to log you in.", style="warning")
            sys.exit(1)
        console.print_json(data=json.loads(user_info.model_dump_json()))
    except Exception as e:
        message = f"Error while getting user info: {e!s}"
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)
