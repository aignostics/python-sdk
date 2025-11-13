"""Boot sequence."""

import atexit
import contextlib
import os
import ssl
import sys
from pathlib import Path
from typing import Any

from loguru import logger

# Optional SSL certificate modules - gracefully degrade if not available
try:
    import certifi
except ImportError:
    certifi = None  # type: ignore[assignment]

try:
    import truststore  # pyright: ignore[reportMissingImports]
except ImportError:
    truststore = None  # type: ignore[assignment]
from collections.abc import Callable

from sentry_sdk.integrations import Integration

from ._constants import __is_library_mode__
from ._log import logging_initialize
from ._sentry import sentry_initialize

# Import third party dependencies.
third_party_dir = Path(__file__).parent.absolute() / ".." / "third_party"
if third_party_dir.is_dir() and str(third_party_dir) not in sys.path:
    sys.path.insert(0, str(third_party_dir))

# Amend library path
if "DYLD_FALLBACK_LIBRARY_PATH" not in os.environ:
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{os.getenv('HOMEBREW_PREFIX', '/opt/homebrew')}/lib/"

from ._constants import __project_name__, __version__  # noqa: E402
from ._process import get_process_info  # noqa: E402

_boot_called = False


def boot(
    sentry_integrations: list[Integration] | None,
    log_filter: Callable[[Any], bool] | None = None,
) -> None:
    """Boot the application or library.

    Args:
        sentry_integrations (list[Integration] | None): List of Sentry integrations to use
        log_filter (Callable[[Any], bool] | None): Optional filter function for logging
    """
    global _boot_called  # noqa: PLW0603
    if _boot_called:
        return
    _boot_called = True

    _parse_env_args()
    logging_initialize(filter_func=log_filter)
    _amend_ssl_trust_chain()
    sentry_initialize(integrations=sentry_integrations)
    _log_boot_message()
    _register_shutdown_message()
    logger.trace("Boot sequence completed successfully.")


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


def _amend_ssl_trust_chain() -> None:
    if __is_library_mode__:
        logger.trace("Skipping SSL trust chain amendment in library mode.")
        return
    if truststore is not None:
        truststore.inject_into_ssl()

    if (
        ssl.get_default_verify_paths().cafile is None
        and os.environ.get("SSL_CERT_FILE") is None
        and certifi is not None
    ):
        os.environ["SSL_CERT_FILE"] = certifi.where()


def _log_boot_message() -> None:
    """Log boot message with version and process information."""
    process_info = get_process_info()
    mode_suffix = ", library-mode" if __is_library_mode__ else ""
    logger.trace(
        "⭐ Booting {} v{} (project root {}, pid {}), parent '{}' (pid {}){}",
        __project_name__,
        __version__,
        process_info.project_root,
        process_info.pid,
        process_info.parent.name,
        process_info.parent.pid,
        mode_suffix,
    )


def _register_shutdown_message() -> None:
    def _shutdown_handler() -> None:
        """Log shutdown message, skipping in test environments to avoid stream closure issues."""
        # In test environments (pytest), stderr may be closed/replaced before atexit runs.
        # Skip logging in tests to avoid Loguru warnings about closed file handles.
        if "pytest" in sys.modules:
            return

        # Check if stderr is still open before attempting to log
        if not sys.stderr.closed:
            # Suppress I/O errors at shutdown - streams may be closed during logging
            with contextlib.suppress(ValueError, OSError):
                logger.trace(
                    "Exiting {project_name} v{version} ...", project_name=__project_name__, version=__version__
                )

    atexit.register(_shutdown_handler)
