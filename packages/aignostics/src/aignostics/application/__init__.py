"""Application module — re-exports from slim aignostics_sdk.application."""

from aignostics_sdk.application import (
    DownloadProgress,
    DownloadProgressState,
    Service,
    Settings,
    cli,
)

__all__ = ["DownloadProgress", "DownloadProgressState", "Service", "Settings", "cli"]

from importlib.util import find_spec

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from aignostics.application._gui._page_builder import PageBuilder  # noqa: PLC0415,PLC2701

    __all__ += [
        "PageBuilder",
    ]
