"""Notebook GUI."""

from aignostics.gui import theme
from aignostics.utils import BasePageBuilder, get_logger

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import ui  # noq  # noqa: PLC0415

        from ._service import Service  # noqa: PLC0415

        @ui.page("/notebook/{application_run_id}")
        def page_application_run_marimo(application_run_id: str) -> None:
            """Inspect Application Run in Marimo."""
            theme()

            with ui.row().classes("w-full justify-end"):
                ui.button("Back to Application Run", icon="arrow_back", on_click=ui.navigate.back)

            try:
                server_url = Service().start()
                ui.html(
                    f'<iframe src="{server_url}?run_id={application_run_id}" width="100%" height="100%"></iframe>'
                ).classes("w-full h-[calc(100vh-5rem)]")
            except Exception:
                message = "Failed to start Marimo server."
                logger.exception("Failed to start Marimo server")
                ui.label(message).classes("text-red-500")
                ui.button("Retry", on_click=ui.navigate.reload).props("color=red")
