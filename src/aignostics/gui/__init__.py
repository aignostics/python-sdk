"""Graphical User Interface (GUI) module."""

from importlib.util import find_spec

if find_spec("nicegui"):
    from ._gui import handle_shutdown, run
    from .components._filepicker import LocalFilePicker
    from .pages._home import home

    __all__ = [
        "LocalFilePicker",
        "handle_shutdown",
        "home",
        "run",
    ]
