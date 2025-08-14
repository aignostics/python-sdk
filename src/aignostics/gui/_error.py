"""Custom error page."""

import traceback

from ..utils import BasePageBuilder  # noqa: TID252
from ._frame import frame


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app, ui  # noqa: PLC0415

        @app.on_page_exception
        def page_error(exception: Exception) -> None:
            """System info and settings page."""
            with frame("Error", left_sidebar=False):
                pass

            with ui.row().classes("w-full gap-4 flex-nowrap"):
                with (
                    ui.column().classes("w-3/5 flex-shrink-0"),
                    ui.column().classes("absolute-center items-center gap-8"),
                ):
                    ui.label(f"{exception}").classes("text-2xl")
                    ui.code(traceback.format_exc(chain=False))

                with ui.column().classes("w-2/5 flex-shrink-0 flex items-center justify-start mt-[200px]"):
                    ui.html(
                        '<dotlottie-player src="/assets/cat.lottie" '
                        'background="transparent" speed="1" style="width: 300px; height: 300px" '
                        'direction="1" playMode="normal" loop autoplay></dotlottie-player>'
                    )

        @ui.page("/force-error")
        async def page_error_force() -> None:  # noqa: RUF029
            """Forced exception for testing.

            Raises:
                Exception: Always raised to test error handling.
            """
            with frame("Forced Error", left_sidebar=False):
                pass
            raise Exception("bla")  # noqa: EM101, TRY002
