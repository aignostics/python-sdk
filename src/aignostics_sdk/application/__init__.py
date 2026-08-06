"""Application module."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from ._cli import cli

if TYPE_CHECKING:
    from ._models import DownloadProgress, DownloadProgressState
    from ._service import Service
    from ._settings import Settings

_LAZY: dict[str, tuple[str, str]] = {
    "DownloadProgress": ("aignostics_sdk.application._models", "DownloadProgress"),
    "DownloadProgressState": ("aignostics_sdk.application._models", "DownloadProgressState"),
    "Service": ("aignostics_sdk.application._service", "Service"),
    "Settings": ("aignostics_sdk.application._settings", "Settings"),
}


def __getattr__(name: str) -> object:
    if name in _LAZY:
        module_path, attr_name = _LAZY[name]
        mod = importlib.import_module(module_path)
        obj = getattr(mod, attr_name)
        globals()[name] = obj
        return obj
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = ["DownloadProgress", "DownloadProgressState", "Service", "Settings", "cli"]
