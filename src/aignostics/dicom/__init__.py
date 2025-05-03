"""DICOM Module."""

from ._cli import cli
from ._service import Service

__all__ = ["Service", "cli"]
