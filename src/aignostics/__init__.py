"""Copier template to scaffold Python projects compliant with best practices and modern tooling."""

from .constants import MODULES_TO_INSTRUMENT
from .utils.boot import boot

boot(modules_to_instrument=MODULES_TO_INSTRUMENT)
