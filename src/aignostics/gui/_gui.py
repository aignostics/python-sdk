from nicegui import app, native, ui

from aignostics.utils import __project_name__, get_logger

logger = get_logger(__name__)


def handle_shutdown() -> None:
    """Handle shutdown of the GUI."""
    logger.info("Shutdown initiated")


def run(in_browser: bool = True, watch: bool = False) -> None:
    """Start the GUI."""
    app.on_shutdown(handle_shutdown)
    ui.run(
        title=__project_name__,
        favicon="⭐",
        native=not in_browser,
        reload=watch,
        dark=False,
        port=native.find_open_port(),
        frameless=False,
        show_welcome_message=True,
    )
