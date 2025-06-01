"""Notebook GUI."""

from pathlib import Path
from urllib.parse import quote

from aignostics.gui import frame, theme
from aignostics.system import Service as SystemService
from aignostics.utils import BasePageBuilder, get_logger

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app, ui  # noq  # noqa: PLC0415

        from ._service import Service  # noqa: PLC0415

        app.add_static_files("/notebook_assets", Path(__file__).parent / "assets")

        @ui.page("/notebook")
        def page_index() -> None:
            """Marimo Extension."""
            with frame("Marimo Extension", left_sidebar=False):
                # Nothing to do here, just to show the page
                pass

            def launch_marimo() -> None:
                """Launch QuPath."""
                launch_button.props(add="loading")
                ui.notify("Launching Python Notebook...", color="blue")
                ui.navigate.to(
                    f"/notebook/all?results_folder={quote(SystemService.get_user_data_directory('results').as_posix())}"
                )

            ui.markdown(
                """
                    ### Manage your Marimo Extension
                """
            )
            with ui.row().classes("w-full justify-start"):
                with ui.column().classes("w-2/5"):
                    with ui.card().classes("w-full"):
                        ui.label(
                            "Marimo is installed and ready to execute. "
                            "Go to a completed application result and click the Notebook button."
                        )
                        with ui.row().classes("w-full justify-between items-center"):
                            launch_button = ui.button(
                                "Open",
                                on_click=launch_marimo,
                                icon="visibility",
                            ).mark("BUTTON_NOTEBOOK_LAUNCH")
                    ui.markdown(
                        """
                            ###### What is Marimo?
                            marimo [1, 2] is an open-source reactive notebook for Python — reproducible, git-friendly,
                            SQL built-in, executable as a script, and shareable as an app.

                            The Aignostics Launchpad embeds Marimo so you can apply data analysis on
                            your application results without having to leave the application.

                            *References:*

                            1. <a href="https://marimo.io/" target="_blank">Marimo website</a>

                            2. <a href="https://raw.githubusercontent.com/marimo-team/marimo/refs/heads/main/LICENSE"
                                target="_blank">License</a>
                        """
                    )
                ui.space()
                with ui.column().classes("w-2/5"), ui.row().classes("w-1/2 justify-center content-center"):
                    ui.space()
                    animation = "/notebook_assets/python.lottie"
                    ui.html(
                        f"<dotlottie-player "
                        f'src="{animation}" '
                        f'background="transparent" '
                        f'speed="1" '
                        f'style="width: 300px; height: 300px" '
                        f'direction="1" '
                        f'playMode="normal" '
                        f"loop "
                        f"autoplay>"
                        f"</dotlottie-player>"
                    )
                    ui.space()

        @ui.page("/notebook/{application_run_id}")
        def page_application_run_marimo(application_run_id: str, results_folder: str) -> None:
            """Inspect Application Run in Marimo."""
            theme()

            with ui.row().classes("w-full justify-end"):
                ui.button(
                    "Back to Application Run" if application_run_id != "all" else "Back to Marimo Extension",
                    icon="arrow_back",
                    on_click=lambda _, application_run_id=application_run_id: ui.navigate.to(
                        f"/application/run/{application_run_id}" if application_run_id != "all" else "/notebook"
                    ),
                ).mark("BUTTON_NOTEBOOK_BACK")

            try:
                server_url = Service().start()
                ui.html(
                    f'<iframe src="{server_url}?application_run_id={application_run_id}'
                    f'&results_folder={quote(results_folder)}" '
                    'width="100%" height="100%"></iframe>'
                ).classes("w-full h-[calc(100vh-5rem)]")
            except Exception:
                message = "Failed to start Marimo server."
                logger.exception("Failed to start Marimo server")
                ui.label(message).classes("text-red-500")
                ui.button("Retry", on_click=ui.navigate.reload).props("color=red")
