"""Application module."""

from ._cli import cli
from ._service import Service

__all__ = [
    "Service",
    "cli",
]

from importlib.util import find_spec

# advertise PageBuuilder to enable auto-discovery
if find_spec("nicegui"):
    from ._gui import PageBuilder

    __all__ += [
        "PageBuilder",
    ]
