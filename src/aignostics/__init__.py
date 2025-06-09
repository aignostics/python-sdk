"""Python SDK providing access to Aignostics AI services."""

import os

from .constants import MODULES_TO_INSTRUMENT, WSI_SUPPORTED_FILE_EXTENSIONS
from .utils.boot import boot

# Add scheme to HTTP proxy environment variables if missing
for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY"]:
    proxy_url = os.environ.get(proxy_var)
    if proxy_url and not proxy_url.startswith(("http://", "https://")):
        os.environ[proxy_var] = f"http://{proxy_url}"

boot(modules_to_instrument=MODULES_TO_INSTRUMENT)

__all__ = ["WSI_SUPPORTED_FILE_EXTENSIONS"]
