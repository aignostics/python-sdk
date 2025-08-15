"""Aignostics Launchpad launcher for pyinstaller."""

import os
import ssl
import sys
from multiprocessing import freeze_support

freeze_support()

os.environ["LOGFIRE_PYDANTIC_RECORD"] = "off"

from aignostics.constants import MODULES_TO_INSTRUMENT  # noqa: E402
from aignostics.utils import boot, get_logger, gui_run  # noqa: E402

boot(MODULES_TO_INSTRUMENT)
logger = get_logger(__name__)

# Constants for command line argument handling
EXEC_SCRIPT_FLAG = "--exec-script"
MIN_ARGS_FOR_SCRIPT = 3  # program name, flag, and script content
MODULE_FLAG = "--run-module"
MIN_ARGS_FOR_MODULE = 3  # program name, flag, and module name

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
elif len(sys.argv) > 1 and sys.argv[1] == MODULE_FLAG:
    # Execute the module passed as the second argument
    if len(sys.argv) >= MIN_ARGS_FOR_MODULE:
        module_name = sys.argv[2]
        # Build the command to run the module with remaining arguments
        module_args = sys.argv[MIN_ARGS_FOR_MODULE:] if len(sys.argv) > MIN_ARGS_FOR_MODULE else []

        # We're running as a packaged executable, run module directly
        # Update sys.argv to what the module expects
        sys.argv = [module_name, *module_args]
        try:
            if module_name == "marimo":
                # Special handling for marimo - importing from private module as marimo's __main__.py does
                from marimo._cli.cli import main  # noqa: PLC2701

                main(prog_name="marimo")
            else:
                # Generic module execution
                import runpy

                runpy.run_module(module_name, run_name="__main__")
        except Exception:
            logger.exception("Failed to execute module '%s'", module_name)
            sys.exit(1)
    else:
        logger.error("No module name provided")
        sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == DEBUG_FLAG:
    import ssl

    print(ssl.get_default_verify_paths())
else:
    # Normal GUI launch
    gui_run(native=True, with_api=False, title="Aignostics Launchpad", icon="🔬")
