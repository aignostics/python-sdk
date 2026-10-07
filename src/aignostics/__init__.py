"""Python SDK providing access to Aignostics AI services."""

import multiprocessing
import os
import warnings
from typing import Any

# TODO(Helmut): remove when google_crc32c supports Python 3.14
warnings.filterwarnings("ignore", message="As the c extension couldn't be imported", category=RuntimeWarning)

from loguru import logger  # noqa: E402

from .constants import (  # noqa: E402
    DEPRECATION_NOTICE,
    HETA_APPLICATION_ID,
    SENTRY_INTEGRATIONS,
    TEST_APP_APPLICATION_ID,
    WSI_SUPPORTED_FILE_EXTENSIONS,
    WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP,
)
from .utils import __is_library_mode__  # noqa: E402
from .utils.boot import boot  # noqa: E402

# Add scheme to HTTP proxy environment variables if missing
for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY"]:
    proxy_url = os.environ.get(proxy_var)
    if proxy_url and not proxy_url.startswith(("http://", "https://")):
        os.environ[proxy_var] = f"http://{proxy_url}"


def _log_filter(record: Any) -> bool:  # noqa: ANN401
    """Filter out unwanted log messages.

    Args:
        record: The log record to filter

    Returns:
        bool: True to log the message, False to filter it out
    """
    return not (
        (record["name"] == "azure.storage.blob._shared.avro.schema" and record["function"] == "register")
        or (record["name"] == "matplotlib.font_manager" and record["function"] == "_findfont_cached")
        or (record["name"] == "PIL.PngImagePlugin" and record["function"] == "call")
        or (record["name"] == "PIL.PngImagePlugin" and record["function"] == "_open")
    )


boot(sentry_integrations=SENTRY_INTEGRATIONS, log_filter=_log_filter)

# Warn library users once per process tree. The CLI shows its own notice, and child processes
# (for example of the Launchpad) import the package again.
if __is_library_mode__ and multiprocessing.parent_process() is None:
    logger.warning("{}", DEPRECATION_NOTICE)
    warnings.warn(DEPRECATION_NOTICE, FutureWarning, stacklevel=2)

__all__ = [
    "DEPRECATION_NOTICE",
    "HETA_APPLICATION_ID",
    "TEST_APP_APPLICATION_ID",
    "WSI_SUPPORTED_FILE_EXTENSIONS",
    "WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP",
]
