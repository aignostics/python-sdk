"""Application module."""

from ._cli import cli
from ._models import DownloadProgress, DownloadProgressState
from ._service import Service
from ._settings import Settings

__all__ = ["DownloadProgress", "DownloadProgressState", "Service", "Settings", "cli"]

from importlib.util import find_spec

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from ._gui._frame import _frame
    from ._gui._page_builder import PageBuilder

    # Create public alias for the frame function
    application_frame = _frame

    __all__ += [
        "PageBuilder",
        "application_frame",
    ]
