"""Python SDK providing access to Aignostics AI services."""

from .constants import MODULES_TO_INSTRUMENT
from .utils.boot import boot

boot(modules_to_instrument=MODULES_TO_INSTRUMENT)
