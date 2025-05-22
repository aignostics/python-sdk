"""Bucket module."""

from importlib.util import find_spec

__all__ = []

from ._cli import cli
from ._service import Service

__all__ += [
    "Service",
    "cli",
]

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from ._gui import PageBuilder

    __all__ += [
        "PageBuilder",
    ]
