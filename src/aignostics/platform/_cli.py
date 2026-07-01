"""CLI of platform module."""

import json
import sys
from typing import Annotated

import typer
from loguru import logger

from aignostics.utils import console

from ._authentication import get_token
from ._sdk_metadata import get_item_sdk_metadata_json_schema, get_run_sdk_metadata_json_schema
from ._service import Service
from ._settings import settings

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


cli_auth = typer.Typer(name="auth", help="Authentication token operations for external integrations.")


@cli_user.command("token")
def auth_token() -> None:
    """Print an Aignostics access token for use as a gcloud external credential helper.

    Outputs a JSON document to stdout in the format expected by gcloud's pluggable
    authentication executable credential source (Workload Identity Federation).

    Configure as an executable credential source by adding the following to your ADC
    credentials JSON file, then run ``gcloud auth application-default login`` to activate
    it. The GOOGLE_EXTERNAL_ACCOUNT_ALLOW_EXECUTABLES environment variable must be set
    to 1 for gcloud to call this helper.

    On success writes: {"version": 1, "success": true, "token_type": "...", "id_token": "...", "expiration_time": ...}

    On failure writes: {"version": 1, "success": false, "code": "1", "message": "..."}
    """
    try:
        token = get_token(use_cache=True)
        stored = settings().token_file.read_text(encoding="utf-8")
        expiry = int(stored.rsplit(":", 1)[-1])
        print(
            json.dumps({
                "version": 1,
                "success": True,
                "token_type": "urn:ietf:params:oauth:token-type:id_token",
                "id_token": token,
                "expiration_time": expiry,
            })
        )
    except Exception as e:
        logger.debug("Failed to obtain Aignostics token for WIF credential helper: {}", e)
        print(
            json.dumps({
                "version": 1,
                "success": False,
                "code": "1",
                "message": str(e),
            })
        )
        sys.exit(1)
