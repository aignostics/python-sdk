"""Aignostics Launchpad launcher for pyinstaller."""

import os
import sys
from multiprocessing import freeze_support

freeze_support()

import pip_system_certs.wrapt_requests  # noqa: E402

pip_system_certs.wrapt_requests.inject_truststore()  # See https://pypi.org/project/pip-system-certs/

os.environ["LOGFIRE_PYDANTIC_RECORD"] = "off"

from aignostics.constants import MODULES_TO_INSTRUMENT  # noqa: E402
from aignostics.utils import boot, get_logger, gui_run  # noqa: E402

boot(MODULES_TO_INSTRUMENT)
logger = get_logger(__name__)

# Constants for command line argument handling
EXEC_SCRIPT_FLAG = "--exec-script"
MIN_ARGS_FOR_SCRIPT = 3  # program name, flag, and script content

DEBUG_FLAG = "--debug"

# Check if we should execute a script instead of launching the GUI
if len(sys.argv) > 1 and sys.argv[1] == EXEC_SCRIPT_FLAG:
    # Execute the script passed as the second argument
    if len(sys.argv) >= MIN_ARGS_FOR_SCRIPT:
        script_content = sys.argv[2]
        try:
            exec(script_content)  # noqa: S102
        except Exception:
            logger.exception("Failed to execute script")
            sys.exit(1)
    else:
        logger.error("No script content provided")
        sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == DEBUG_FLAG:
    import ssl

    print(ssl.get_default_verify_paths())
else:
    # Normal GUI launch
    gui_run(native=True, with_api=False, title="Aignostics Launchpad", icon="🔬")
