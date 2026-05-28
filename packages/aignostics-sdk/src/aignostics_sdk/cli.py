"""CLI entry point for aignostics-sdk slim distribution.

This module wires only the platform sub-commands (user, sdk) into a trimmed
Typer application.  It deliberately does *not* call ``prepare_cli`` because
that function uses ``locate_implementations`` to deep-scan the ``aignostics``
package and would pull in the heavy domain modules (application, wsi, dataset,
bucket, qupath, …) that are absent from this slim distribution.
"""

from __future__ import annotations

import typer

from aignostics_sdk.platform import cli_sdk, cli_user
from aignostics_sdk.utils import __python_version__, __version__
from aignostics_sdk.utils._cli import _add_epilog_recursively, _no_args_is_help_recursively

_EPILOG = f"🔬 Aignostics SDK v{__version__} - built with love in Berlin 🐻 // Python v{__python_version__}"

cli = typer.Typer(
    help="Command Line Interface (CLI) of Aignostics SDK providing access to Aignostics Platform.",
)

cli.add_typer(cli_user)
cli.add_typer(cli_sdk)

# Apply epilog and no-args-is-help without the auto-discovery step that
# prepare_cli performs via locate_implementations(typer.Typer).
_add_epilog_recursively(cli, _EPILOG)
_no_args_is_help_recursively(cli)

if __name__ == "__main__":  # pragma: no cover
    cli()
