"""Boot sequence."""

import os
import sys

from ._log import logging_initialize
from ._logfire import logfire_initialize
from ._sentry import sentry_initialize

_boot_called = False


def boot(modules_to_instrument: list[str]) -> None:
    """Boot the application.

    Args:
        modules_to_instrument (list): List of modules to be instrumented.
        repository_url (str): URL of the repository.
        repository_root_path (str): The root path of the repository. Default is the root path.
    """
    global _boot_called  # noqa: PLW0603
    if _boot_called:
        return
    _boot_called = True
    sentry_initialize()
    log_to_logfire = logfire_initialize(modules_to_instrument)
    logging_initialize(log_to_logfire)
    _amend_library_path()
    _parse_env_args()
    _log_boot_message()


from ._constants import __project_name__, __version__  # noqa: E402
from ._log import get_logger  # noqa: E402
from ._process import get_process_info  # noqa: E402


def _parse_env_args() -> None:
    """Parse --env arguments from command line and add to environment if prefix matches.

    - Last but not least removes those args so typer does not complain about them.
    """
    i = 1  # Start after script name
    to_remove = []
    prefix = f"{__project_name__.upper()}_"

    while i < len(sys.argv):
        current_arg = sys.argv[i]

        # Handle "--env KEY=VALUE" or "-e KEY=VALUE" format (two separate arguments)
        if (current_arg in {"--env", "-e"}) and i + 1 < len(sys.argv):
            key_value = sys.argv[i + 1]
            if "=" in key_value:
                key, value = key_value.split("=", 1)
                if key.startswith(prefix):
                    os.environ[key] = value.strip("\"'")
                to_remove.extend([i, i + 1])
                i += 2
                continue

        i += 1

    # Remove processed arguments from sys.argv in reverse order
    for index in sorted(to_remove, reverse=True):
        del sys.argv[index]


def _amend_library_path() -> None:
    """Patch environment variables before any other imports."""
    if "DYLD_FALLBACK_LIBRARY_PATH" not in os.environ:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{os.getenv('HOMEBREW_PREFIX', '/opt/homebrew')}/lib/"


def _log_boot_message() -> None:
    """Log boot message with version and process information."""
    logger = get_logger(__name__)
    process_info = get_process_info()
    logger.info(
        "⭐ Booting %s v%s (project root %s, pid %s), parent '%s' (pid %s)",
        __project_name__,
        __version__,
        process_info.project_root,
        process_info.pid,
        process_info.parent.name,
        process_info.parent.pid,
    )
