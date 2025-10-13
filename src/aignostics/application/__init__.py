"""Application module."""

from ._cli import cli
from ._service import Service
from ._settings import Settings

__all__ = ["Service", "Settings", "cli"]

from importlib.util import find_spec

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from ._gui._page_builder import PageBuilder

    __all__ += [
        "PageBuilder",
    ]
