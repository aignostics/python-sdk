"""Aignostics Launchpad launcher for pyinstaller."""

import os
import platform
import ssl
import sys
from multiprocessing import freeze_support

freeze_support()

if platform.system() != "Darwin":
    try:
        import pyi_splash  # pyright: ignore[reportMissingModuleSource]
    except ImportError:
        pyi_splash = None
else:
    pyi_splash = None

if pyi_splash and pyi_splash.is_alive():
    pyi_splash.update_text("Initializing services ...")

os.environ["LOGFIRE_PYDANTIC_RECORD"] = "off"

from aignostics.constants import MODULES_TO_INSTRUMENT  # noqa: E402
from aignostics.utils import boot, get_logger, gui_run  # noqa: E402

boot(MODULES_TO_INSTRUMENT)

logger = get_logger(__name__)


EXEC_SCRIPT_FLAG = "--exec-script"
MIN_ARGS_FOR_SCRIPT = 3  # program name, flag, and script content
MODULE_FLAG = "--run-module"
MIN_ARGS_FOR_MODULE = 3  # program name, flag, and module name

DEBUG_FLAG = "--debug"

if len(sys.argv) > 1 and sys.argv[1] == EXEC_SCRIPT_FLAG:
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
    if pyi_splash and pyi_splash.is_alive():
        pyi_splash.close()

    if len(sys.argv) >= MIN_ARGS_FOR_MODULE:
        module_name = sys.argv[2]
        module_args = sys.argv[MIN_ARGS_FOR_MODULE:] if len(sys.argv) > MIN_ARGS_FOR_MODULE else []
        sys.argv = [module_name, *module_args]
        try:
            if module_name == "marimo":
                from marimo._cli.cli import main  # noqa: PLC2701

                main(prog_name="marimo")
            else:
                import runpy

                runpy.run_module(module_name, run_name="__main__")
        except Exception:
            logger.exception("Failed to execute module '%s'", module_name)
            sys.exit(1)
    else:
        logger.error("No module name provided")
        sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == DEBUG_FLAG:
    if pyi_splash and pyi_splash.is_alive():
        pyi_splash.close()

    import ssl

    print(ssl.get_default_verify_paths())
else:
    if pyi_splash and pyi_splash.is_alive():
        pyi_splash.update_text("Opening user interface ...")
    gui_run(native=True, with_api=False, title="Aignostics Launchpad", icon="🔬")
