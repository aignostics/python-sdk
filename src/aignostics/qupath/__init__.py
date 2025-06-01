"""QuPath module."""

from importlib.util import find_spec

__all__ = []

# advertise PageBuilder to enable auto-discovery
if find_spec("paquo") and find_spec("nicegui"):
    from ._cli import cli
    from ._gui import PageBuilder
    from ._service import AddProgress, AnnotateProgress, Service

    __all__ += [
        "AddProgress",
        "AnnotateProgress",
        "PageBuilder",
        "Service",
        "cli",
    ]
