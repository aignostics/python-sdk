"""Python SDK providing access to Aignostics AI services."""

from .constants import (
    __project_name__,
    __project_path__,
    __version__,
)
from .service import Service

__all__ = [
    "Service",
    "__project_name__",
    "__project_path__",
    "__version__",
]
