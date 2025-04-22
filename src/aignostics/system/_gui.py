"""Homepage (index) of GUI."""

from nicegui import ui

from ..utils import BasePageBuilder, __project_name__, __version__  # noqa: TID252
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        @ui.page("/info")
        def page_info() -> None:
            """Homepage of GUI."""
            ui.label(f"{__project_name__} v{__version__}").mark("LABEL_VERSION")
            ui.json_editor({
                "content": {"json": Service().info(True, True)},
                "readOnly": True,
            }).mark("JSON_EDITOR_INFO")
            ui.link("Home", "/").mark("LINK_HOME")
