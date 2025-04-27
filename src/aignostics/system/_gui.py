"""Homepage (index) of GUI."""

from ..utils import BasePageBuilder, __project_name__, __version__  # noqa: TID252
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import run, ui  # noqa: PLC0415

        @ui.page("/info")
        async def page_info() -> None:
            """Homepage of GUI."""
            ui.label(f"{__project_name__} v{__version__}").mark("LABEL_VERSION")
            spinner = ui.spinner("dots", size="lg", color="red")
            properties = {
                "content": {"json": "Loading ..."},
                "readOnly": True,
            }
            editor = ui.json_editor(properties).mark("JSON_EDITOR_INFO")
            ui.link("Home", "/").mark("LINK_HOME")
            info = await run.cpu_bound(Service().info, True, True)
            properties["content"] = {"json": info}
            editor.update()
            spinner.delete()
