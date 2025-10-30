"""Python SDK providing access to Aignostics AI services."""

import os

from .constants import (
    HETA_APPLICATION_ID,
    LOGFIRE_MODULES_TO_INSTRUMENT,
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

boot(logfire_modules_to_instrument=LOGFIRE_MODULES_TO_INSTRUMENT, sentry_integrations=SENTRY_INTEGRATIONS)

__all__ = [
    "HETA_APPLICATION_ID",
    "TEST_APP_APPLICATION_ID",
    "WSI_SUPPORTED_FILE_EXTENSIONS",
    "WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP",
]
