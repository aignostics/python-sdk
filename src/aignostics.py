"""Aignostics Launchpad launcher for pyinstaller."""

import os
from multiprocessing import freeze_support

freeze_support()

os.environ["LOGFIRE_PYDANTIC_RECORD"] = "off"

from aignostics.constants import MODULES_TO_INSTRUMENT  # noqa: E402
from aignostics.utils import boot, get_logger, gui_run  # noqa: E402

boot(MODULES_TO_INSTRUMENT)
logger = get_logger(__name__)

gui_run(native=True, with_api=False, title="Aignostics Launchpad", icon="🔬")
