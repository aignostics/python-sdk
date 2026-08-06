"""Notebook module."""

from importlib.util import find_spec

__all__ = []

if find_spec("marimo") and find_spec("nicegui"):
    from ._gui import PageBuilder
    from ._service import Service

    __all__ += [
        "PageBuilder",
        "Service",
    ]
