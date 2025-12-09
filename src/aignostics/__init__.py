"""Python SDK providing access to Aignostics AI services."""

import os
from typing import Any

from .constants import (
    HETA_APPLICATION_ID,
    SENTRY_INTEGRATIONS,
    TEST_APP_APPLICATION_ID,
    WSI_SUPPORTED_FILE_EXTENSIONS,
    WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP,
)
from .utils.boot import boot

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

__all__ = [
    "HETA_APPLICATION_ID",
    "TEST_APP_APPLICATION_ID",
    "WSI_SUPPORTED_FILE_EXTENSIONS",
    "WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP",
]
