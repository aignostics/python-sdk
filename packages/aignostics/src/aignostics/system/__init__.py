"""System module — re-exports from slim aignostics_sdk.system."""

from aignostics_sdk.system import (
    Service,
    Settings,
    cli,
)

__all__ = [
    "Service",
    "Settings",
    "cli",
]

from importlib.util import find_spec

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from aignostics.system._gui import PageBuilder

    __all__ += [
        "PageBuilder",
    ]
