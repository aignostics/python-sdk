"""Layout and theme of GUI."""

from importlib.util import find_spec

__all__ = []

# advertise PageBuilder to enable auto-discovery
if find_spec("nicegui"):
    from ._frame import frame
    from ._theme import PageBuilder, theme

    __all__ += ["PageBuilder", "frame", "theme"]
