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

        @ui.page("/alive")
        def alive() -> None:
            """Simple page to check the GUI is alive."""
            ui.label("Yes")

        @ui.page("/system")
        async def page_system() -> None:  # noqa: PLR0915
            """System info and settings page."""
            with frame("Info and Settings", left_sidebar=False):
                pass

            with ui.row().classes("w-full gap-4 flex-nowrap"):  # noqa: PLR1702
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
                            # Note: editor.update(...) broken in NiceGUI 3.0.4
                            editor.run_editor_method("update", properties["content"])
                            editor.run_editor_method(":expand", "[]", "path => true")
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
                                # Note: editor.update(...) broken in NiceGUI 3.0.4
                                editor.run_editor_method("update", properties["content"])
                                editor.run_editor_method(":expand", "[]", "path => true")
                                spinner.set_visibility(False)
                                editor.set_visibility(True)
                                mask_secrets_switch.set_visibility(True)

                            # Initial load
                            editor.set_visibility(False)
                            await load_info()
                        with ui.tab_panel(tab_settings):
                            # Remote Diagnostics Setting
                            with (
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

                            # Default Folder Path Setting
                            # This setting controls the starting directory for all file selection dialogs
                            # across application, dataset, and other modules. The path is persisted in
                            # app.storage.general and survives across GUI sessions.
                            with (
                                ui.card().classes("w-full mt-4"),
                                ui.column().classes("w-full gap-2"),
                            ):
                                ui.label("Default Folder Path").classes("text-h6")
                                ui.label(
                                    "Set the default folder that opens when selecting files for application runs."
                                ).classes("text-caption text-grey-7")

                                # Display current default path
                                from aignostics.utils import get_user_data_directory  # noqa: PLC0415

                                current_path = app.storage.general.get(
                                    "default_folder_path", str(get_user_data_directory("datasets"))
                                )

                                path_label = ui.label(f"Current: {current_path}").classes("text-body2 font-mono")

                                async def select_default_folder() -> None:
                                    """Open file picker to select default folder.

                                    The selected path will be used as the starting directory for all file selection
                                    dialogs throughout the application (run submission, downloads, dataset selection).
                                    upper_limit=None allows full directory tree navigation.
                                    """
                                    from aignostics.utils import GUILocalFilePicker  # noqa: PLC0415

                                    # upper_limit=None enables unrestricted navigation up the directory tree
                                    result = await GUILocalFilePicker(current_path, upper_limit=None, multiple=False)  # type: ignore
                                    if result and len(result) > 0:
                                        from aiopath import AsyncPath  # noqa: PLC0415

                                        selected_path = AsyncPath(result[0])
                                        if await selected_path.is_dir():
                                            app.storage.general["default_folder_path"] = str(selected_path)
                                            path_label.set_text(f"Current: {selected_path}")
                                            ui.notify(f"Default folder path set to: {selected_path}", type="positive")
                                        else:
                                            ui.notify("Please select a valid directory.", type="warning")
                                    else:
                                        ui.notify("No folder selected.", type="info")

                                def reset_default_folder() -> None:
                                    """Reset to default datasets folder.

                                    Restores the default folder path to the SDK's datasets directory.
                                    This is the recommended location for storing downloaded datasets
                                    and analysis inputs.
                                    """
                                    default_path = str(get_user_data_directory("datasets"))
                                    app.storage.general["default_folder_path"] = default_path
                                    path_label.set_text(f"Current: {default_path}")
                                    ui.notify(f"Reset to default: {default_path}", type="positive")

                                with ui.row().classes("gap-2"):
                                    ui.button(
                                        "Select Folder",
                                        icon="folder_open",
                                        on_click=select_default_folder,
                                    ).props("outline")
                                    ui.button(
                                        "Reset to Default",
                                        icon="refresh",
                                        on_click=reset_default_folder,
                                    ).props("flat")
                with ui.column().classes("w-2/5 flex-shrink-0 flex items-center justify-start mt-[200px]"):
                    ui.html(
                        '<dotlottie-player src="/system_assets/system.lottie" '
                        'background="transparent" speed="1" style="width: 300px; height: 300px" '
                        'direction="1" playMode="normal" loop autoplay></dotlottie-player>',
                        sanitize=False,
                    )
