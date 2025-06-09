"""Homepage (index) of GUI."""

from pathlib import Path

from aignostics.gui import frame
from aignostics.utils import BaseService, locate_subclasses

from ..utils import BasePageBuilder  # noqa: TID252
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: PLR0915
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
        async def page_system() -> None:  # noqa: PLR0915
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
                        with ui.tab_panel(tab_health).classes("min-h-[calc(100vh-12rem)]"):
                            spinner = ui.spinner(size="lg").classes(
                                "absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10"
                            )
                            properties = {
                                "content": {"json": "Loading ..."},
                                "mode": "tree",
                                "readOnly": True,
                                "mainMenuBar": True,
                                "navigationBar": True,
                                "statusBar": True,
                            }
                            editor = ui.json_editor(properties).style("width: 100%").mark("JSON_EDITOR_HEALTH")
                            editor.set_visibility(False)
                            health = await run.cpu_bound(Service.health_static)
                            if health is None:
                                properties["content"] = {"json": "Health check failed."}  # type: ignore[unreachable]
                            else:
                                properties["content"] = {"json": health.model_dump()}
                            editor.update()
                            editor.run_editor_method(":expand", "path => true")
                            spinner.set_visibility(False)
                            editor.set_visibility(True)
                        with ui.tab_panel(tab_info).classes("min-h-[calc(100vh-12rem)]"):
                            # Mask secrets switch with reload functionality
                            with ui.row().classes("w-full items-center gap-2 mb-4"):
                                mask_secrets_switch = ui.switch(
                                    text="Mask secrets", value=True, on_change=lambda e: load_info(mask_secrets=e.value)
                                )

                            spinner = ui.spinner(size="lg").classes(
                                "absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10"
                            )
                            properties = {
                                "content": {"json": "Loading ..."},
                                "mode": "tree",
                                "readOnly": True,
                                "mainMenuBar": True,
                                "navigationBar": True,
                                "statusBar": True,
                            }
                            editor = ui.json_editor(properties).style("width: 100%").mark("JSON_EDITOR_INFO")

                            async def load_info(mask_secrets: bool = True) -> None:
                                """Load system info with current mask_secrets setting."""
                                editor.set_visibility(False)
                                spinner.set_visibility(True)
                                mask_secrets_switch.set_visibility(False)
                                info = await run.cpu_bound(
                                    Service.info, include_environ=True, mask_secrets=mask_secrets
                                )
                                if info is None:
                                    properties["content"] = {"json": "Info retrieval failed."}  # type: ignore[unreachable]
                                else:
                                    properties["content"] = {"json": info}
                                editor.update()
                                editor.run_editor_method(":expand", "path => true")
                                spinner.set_visibility(False)
                                editor.set_visibility(True)
                                mask_secrets_switch.set_visibility(True)

                            # Initial load
                            editor.set_visibility(False)
                            await load_info()
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
