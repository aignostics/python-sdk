"""Marimo GUI."""

import time

from aignostics.gui import theme
from aignostics.utils import BasePageBuilder, get_logger

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import ui  # noq  # noqa: PLC0415

        from ._service import Service  # noqa: PLC0415

        @ui.page("/marimo/{application_run_id}")
        def page_application_run_marimo(application_run_id: str) -> None:
            """Inspect Application Run in Marimo."""
            theme()

            with ui.row().classes("w-full justify-end"):
                ui.button("Overview", icon="arrow_back", on_click=ui.navigate.back)

            Service().start()
            time.sleep(1)

            ui.html(
                f'<iframe src="http://localhost:2718?run_id={application_run_id}" width="100%" height="100%"></iframe>'
            ).classes("w-full h-[calc(100vh-5rem)]")
