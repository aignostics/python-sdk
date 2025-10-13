"""Bucket module."""

from importlib.util import find_spec

__all__ = []

from ._cli import cli
from ._service import Service
from ._settings import Settings

__all__ += ["Service", "Settings", "cli"]

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from ._gui import PageBuilder

    __all__ += [
        "PageBuilder",
    ]
