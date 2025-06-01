"""GUI of application module including homepage of Aignostics Launchpad."""

from pathlib import Path

from aignostics.utils import BasePageBuilder


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app, ui  # noq  # noqa: PLC0415

        app.add_static_files("/application_assets", Path(__file__).parent / "assets")

        @ui.page("/")
        async def page_index() -> None:
            """Index page of application module, serving as the homepage of Aignostics Launchpad."""
            from ._page_index import _page_index  # noqa: PLC0415

            await _page_index()

        @ui.page("/application/{application_id}")
        async def page_application_describe(application_id: str) -> None:
            """Describe Application.

            Args:
                application_id (str): The application ID.
            """
            from ._page_application_describe import _page_application_describe  # noqa: PLC0415

            await _page_application_describe(application_id)

        @ui.page("/application/run/{application_run_id}")
        async def page_application_run_describe(application_run_id: str) -> None:
            """Describe Application Run.

            Args:
                application_run_id (str): The application run id
            """
            from ._page_application_run_describe import _page_application_run_describe  # noqa: PLC0415

            await _page_application_run_describe(application_run_id)
