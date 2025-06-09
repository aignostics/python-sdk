"""QuPath module."""

from importlib.util import find_spec

__all__ = []

# advertise PageBuilder to enable auto-discovery
if find_spec("ijson") and find_spec("nicegui"):
    from ._cli import cli
    from ._gui import PageBuilder
    from ._service import QUPATH_LAUNCH_MAX_WAIT_TIME, QUPATH_VERSION, AddProgress, AnnotateProgress, Service

    __all__ += [
        "QUPATH_LAUNCH_MAX_WAIT_TIME",
        "QUPATH_VERSION",
        "AddProgress",
        "AnnotateProgress",
        "PageBuilder",
        "Service",
        "cli",
    ]
