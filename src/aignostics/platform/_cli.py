"""CLI of platform module."""

import json
import sys
from typing import Annotated

import typer
from loguru import logger

from aignostics.utils import console

from ._sdk_metadata import get_item_sdk_metadata_json_schema, get_run_sdk_metadata_json_schema
from ._service import Service

cli_user = typer.Typer(name="user", help="User operations such as login, logout and whoami.")

service: Service | None = None


def _get_service() -> Service:
    """Get the service instance, initializing it if necessary.

    Returns:
        Service: The service instance.
    """
    global service  # noqa: PLW0603
    if service is None:
        service = Service()
    return service


@cli_user.command("logout")
def logout() -> None:
    """Logout if authenticated.

    - Deletes the cached authentication token if existing.
    """
    service = _get_service()
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


@cli_user.command("login")
def login(
    relogin: Annotated[bool, typer.Option(help="Re-login")] = False,
) -> None:
    """(Re)login."""
    service = _get_service()
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


@cli_user.command("whoami")
def whoami(
    mask_secrets: Annotated[bool, typer.Option(help="Mask secrets")] = True,
    relogin: Annotated[bool, typer.Option(help="Re-login")] = False,
) -> None:
    """Print user info."""
    service = _get_service()
    try:
        user_info = service.get_user_info(relogin=relogin)
        console.print_json(
            data=user_info.model_dump_secrets_masked() if mask_secrets else user_info.model_dump(mode="json")
        )
    except Exception as e:
        message = f"Error while getting user info: {e!s}"
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)
        sys.exit(1)


cli_sdk = typer.Typer(name="sdk", help="Platform operations such as dumping the SDK metadata schema.")


@cli_sdk.command("run-metadata-schema")
def run_sdk_metadata_schema(
    pretty: Annotated[bool, typer.Option(help="Pretty print JSON output")] = True,
) -> None:
    """Print the JSON Schema for Run SDK metadata.

    This schema defines the structure and validation rules for metadata
    that the SDK attaches to application runs. Use this to understand
    what fields are expected and their types.
    """
    try:
        schema = get_run_sdk_metadata_json_schema()
        if pretty:
            console.print_json(data=schema)
        else:
            print(json.dumps(schema))
    except Exception as e:
        message = f"Error getting run SDK metadata schema: {e!s}"
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli_sdk.command("item-metadata-schema")
def item_sdk_metadata_schema(
    pretty: Annotated[bool, typer.Option(help="Pretty print JSON output")] = True,
) -> None:
    """Print the JSON Schema for Item SDK metadata.

    This schema defines the structure and validation rules for metadata
    that the SDK attaches to individual items within application runs.
    Use this to understand what fields are expected and their types.
    """
    try:
        schema = get_item_sdk_metadata_json_schema()
        if pretty:
            console.print_json(data=schema)
        else:
            print(json.dumps(schema))
    except Exception as e:
        message = f"Error getting item SDK metadata schema: {e!s}"
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)
