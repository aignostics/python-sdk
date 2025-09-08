"""GUI page builder for example module."""

from aignostics.utils import BasePageBuilder


class PageBuilder(BasePageBuilder):
    """Page builder for example module."""

    @staticmethod
    def register_pages() -> None:
        """Register example module pages."""
        from nicegui import ui  # noqa: PLC0415

        @ui.page("/example")
        async def page_example() -> None:
            """Example page."""
            from ._page_example import _page_example  # noqa: PLC0415

            await _page_example()
