"""Homepage (index) of GUI."""

from aignostics.gui import frame

from ..utils import BasePageBuilder  # noqa: TID252
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import run, ui  # noqa: PLC0415

        Service().health()  # Ensure settings are loaded

        ui.add_head_html("""
            <style>
                :global(.jse-modal-window.jse-modal-window-jsoneditor)
                {
                    width: 100%;
                    height: 100%;
                    min-height: 900px;
                }
            </style>
        """)

        @ui.page("/system")
        async def page_system() -> None:
            """System page."""
            with frame("Inspector", left_sidebar=False):
                pass
            ui.label("Health").classes("text-h6")
            properties = {
                "content": {"json": Service().health().model_dump()},
                "mode": "tree",
                "readOnly": True,
                "mainMenuBar": False,
                "navigationBar": False,
                "statusBar": False,
            }
            ui.json_editor(properties).style("width: 100%").mark("JSON_EDITOR_INFO")

            ui.label("Info").classes("text-h6")
            spinner = ui.spinner("dots", size="lg", color="red")
            properties = {
                "content": {"json": "Loading ..."},
                "mode": "tree",
                "readOnly": True,
                "mainMenuBar": False,
                "navigationBar": False,
                "statusBar": False,
            }
            editor = ui.json_editor(properties).style("width: 100%").mark("JSON_EDITOR_INFO")
            editor.set_visibility(False)
            info = await run.cpu_bound(Service().info, True, True)
            properties["content"] = {"json": info}
            editor.update()
            editor.run_editor_method(":expand", "path => true")
            spinner.delete()
            editor.set_visibility(True)
