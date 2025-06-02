"""Homepage (index) of GUI."""

from pathlib import Path

from aignostics.gui import frame
from aignostics.utils import BaseService, locate_subclasses

from ..utils import BasePageBuilder  # noqa: TID252
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app, run, ui  # noqa: PLC0415

        locate_subclasses(BaseService)  # Ensure settings are loaded
        app.add_static_files("/system_assets", Path(__file__).parent / "assets")

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
            """System info and settings page."""
            with frame("Info and Settings", left_sidebar=False):
                pass

            with ui.row().classes("w-full gap-4 flex-nowrap"):
                with ui.column().classes("w-3/5 flex-shrink-0"):
                    with ui.tabs().classes("w-full") as tabs:
                        tab_health = ui.tab("Health")
                        tab_info = ui.tab("Info")
                        tab_settings = ui.tab("Settings")
                    with ui.tab_panels(tabs, value=tab_health).classes("w-full"):
                        with ui.tab_panel(tab_health):
                            properties = {
                                "content": {"json": Service().health().model_dump()},
                                "mode": "tree",
                                "readOnly": True,
                                "mainMenuBar": False,
                                "navigationBar": False,
                                "statusBar": False,
                            }
                            ui.json_editor(properties).style("width: 100%").mark("JSON_EDITOR_INFO")
                        with ui.tab_panel(tab_info):
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
                        with (
                            ui.tab_panel(tab_settings),
                            ui.card().classes("w-full"),
                            ui.row().classes("items-center justify-between"),
                        ):
                            ui.switch(
                                value=Service.remote_diagnostics_enabled(),
                                on_change=lambda e: (
                                    Service.remote_diagnostics_enable()
                                    if e.value
                                    else Service.remote_diagnostics_disable(),
                                    ui.notify("Restart the app to apply changes.", color="warning"),  # type: ignore[func-returns-value]
                                    None,
                                )[0],
                            )
                            ui.label("Remote Diagnostics")
                with ui.column().classes("w-2/5 flex-shrink-0 flex items-center justify-start mt-[200px]"):
                    ui.html(
                        '<dotlottie-player src="/system_assets/system.lottie" '
                        'background="transparent" speed="1" style="width: 300px; height: 300px" '
                        'direction="1" playMode="normal" loop autoplay></dotlottie-player>'
                    )
