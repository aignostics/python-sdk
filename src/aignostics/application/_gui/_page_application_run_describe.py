"""Run describe page, including download, QuPath and Marimo control."""

import webbrowser
from importlib.util import find_spec
from multiprocessing import Manager
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import humanize
from loguru import logger
from nicegui import (
    app,
    ui,  # noq
)
from nicegui import run as nicegui_run

from aignostics.platform import ItemOutput, ItemResult, ItemState, RunState
from aignostics.third_party.showinfm.showinfm import show_in_file_manager
from aignostics.utils import GUILocalFilePicker, get_user_data_directory

if TYPE_CHECKING:
    from aignx.codegen.models import RunReadResponse

    from aignostics.platform import UserInfo

from .._models import DownloadProgressState  # noqa: TID252
from .._service import Service  # noqa: TID252
from .._utils import get_mime_type_for_artifact, queue_position_string_from_run  # noqa: TID252
from ._frame import _frame
from ._utils import (
    mime_type_to_icon,
    run_item_status_and_termination_reason_to_icon_and_color,
    run_status_to_icon_and_color,
)

WIDTH_1200px = "width: 1200px; max-width: none"
RESULTS_PAGE_SIZE = 20

service = Service()


async def _page_application_run_describe(run_id: str) -> None:  # noqa: C901, PLR0912, PLR0914, PLR0915
    """Describe Application.

    Args:
        run_id (str): The ID of the application run to describe.
    """
    import pandas as pd  # noqa: PLC0415

    if find_spec("ijson"):
        from aignostics.qupath import Service as QuPathService  # noqa: PLC0415

    ui.add_head_html("""
        <style>
        /* Force text wrapping in code blocks */
        .nicegui-code pre {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            max-width: 100% !important;
        }
        /* Remove padding from expansion items to make full use of space */
        .q-expansion-item .q-item {
            padding-left: 0 !important;
        }
        .q-expansion-item .q-expansion-item__content {
            padding: 0 !important;
        }
        </style>
    """)

    spinner = ui.spinner(size="xl").classes("fixed inset-0 m-auto")
    run = await nicegui_run.io_bound(service.application_run, run_id)
    await ui.context.client.connected()  # Wait for client connection before accessing app.storage
    user_info: UserInfo | None = app.storage.tab.get("user_info", None)
    run_data: RunReadResponse | None = (
        await nicegui_run.io_bound(
            run.details,
            hide_platform_queue_position=not (user_info and user_info.is_internal_user),
        )
        if run
        else None
    )
    spinner.set_visibility(False)

    if run and run_data:
        icon, color = run_status_to_icon_and_color(
            run_data.state.value,
            run_data.termination_reason,
            run_data.statistics.item_count,
            run_data.statistics.item_succeeded_count,
        )
        await _frame(
            navigation_title=(
                f"Run of {run_data.application_id} ({run_data.version_number}) on "
                f"{run_data.submitted_at.astimezone().strftime('%m-%d %H:%M')}"
            ),
            navigation_icon=icon,
            navigation_icon_color=color,
            navigation_icon_tooltip=f"Run {run_data.run_id}, status {run_data.state.value.upper()}",
            left_sidebar=True,
            args={"run_id": run_id},
        )
    else:
        await _frame(
            navigation_title=f"Run {run_id}",
            navigation_icon="bug_report",
            navigation_icon_color="negative",
            navigation_icon_tooltip="Could not load run data",
            left_sidebar=True,
            args={"run_id": run_id},
        )

    if run is None:
        ui.label(f"Failed to get run '{run_id}'").mark("LABEL_ERROR")  # type: ignore[unreachable]
        return

    # Forward declaration of UI buttons that will be defined later
    cancel_button: ui.button
    delete_button: ui.button

    async def _cancel(run_id: str) -> bool:
        """Cancel the application run.

        Args:
            run_id (str): The ID of the run to cancel.

        Returns:
            bool: True if the run was cancelled, False otherwise.
        """
        ui.notify(f"Canceling application run with id '{run_id}' ...", type="info")
        try:
            cancel_button.disable()
            cancel_button.props(add="loading")
            await nicegui_run.io_bound(service.application_run_cancel, run_id)
            cancel_button.props(remove="loading")
            ui.navigate.reload()
            ui.notify("Application run cancelled!", type="positive")
            return True
        except Exception as e:
            cancel_button.enable()
            cancel_button.props(remove="loading")
            ui.notify(f"Failed to cancel application run: {e}.", type="warning")
            return False

    async def _delete(run_id: str) -> bool:
        """Delete the application run results and navigate to the main page.

        Args:
            run_id (str): The ID of the run to cancel.

        Returns:
            bool: True if the run was cancelled, False otherwise.
        """
        ui.notify(f"Deleting results of application run with id '{run_id}' ...", type="info")
        try:
            delete_button.disable()
            delete_button.props(add="loading")
            await nicegui_run.io_bound(service.application_run_delete, run_id)
            delete_button.props(remove="loading")
            ui.navigate.to("/")
            ui.notify("Application run deleted!", type="positive")
            return True
        except Exception as e:
            delete_button.enable()
            delete_button.props(remove="loading")
            ui.notify(f"Failed to delete results of application run: {e}.", type="warning")
            return False

    # Mutable container for qupath_project and marimo options that persists across @ui.refreshable calls.
    # Defined OUTSIDE the @ui.refreshable function so closures (like start_download) always read
    # from the same dict instance, even after refresh() is called with new parameter values.
    download_options: dict[str, bool] = {"qupath_project": False, "marimo": False}

    @ui.refreshable
    def download_run_dialog_content(qupath_project: bool = False, marimo: bool = False) -> None:  # noqa: C901, PLR0915
        # Update the shared options dict so closures read the current values
        download_options["qupath_project"] = qupath_project
        download_options["marimo"] = marimo

        if qupath_project:
            ui.markdown(
                "##### Visualize results in QuPath with one click \n"
                "1. Use data directory of Launchpad or select a custom folder. \n"
                "2. A subfolder with the application run will be created and all results downloaded there. \n"
                "3. A QuPath project will be created in a subfolder of the application run folder. \n"
                "4. The QuPath project will reference the input slides and resulting image heatmaps. \n"
                "5. Detected cells will be added as annotations to input slides. \n"
            )
        elif marimo:
            ui.markdown(
                "##### Open results in Marimo with one click \n"
                "1. Use data directory of Launchpad or select a custom folder. \n"
                "2. A subfolder with the application run will be created and all results downloaded there. \n"
                "3. A Marimo notebook will be started pointing to the subfolder. \n"
            )
        else:
            ui.markdown(
                "##### Download all results with one click \n"
                "1. Use data directory of Launchpad or select a custom folder. \n"
                "2. A subfolder with the application run will be created and all results downloaded there. \n"
            )

        # Use the input field directly as the source of truth for folder selection.
        # We bind to folder_state dict so start_download can read the current value.
        folder_state: dict[str, str] = {"value": ""}
        folder_input = ui.input("Selected folder", value="").classes("w-full").props("readonly")
        folder_input.bind_value(folder_state, "value")

        with ui.row().classes("w-full"):

            async def _select_download_destination() -> None:
                result = await GUILocalFilePicker(str(Path.home()), multiple=False)  # type: ignore[misc]
                if result and len(result) > 0:
                    folder_path = Path(result[0])
                    folder_value = str(folder_path) if folder_path.is_dir() else str(folder_path.parent)
                    folder_state["value"] = folder_value
                    folder_input.set_value(folder_value)
                    ui.notify(f"Using custom directory: {folder_value}", type="info")
                    download_button.enable()
                else:
                    ui.notify("No folder selected", type="warning")

            def _select_data() -> None:
                """Select the Launchpad data directory."""
                folder_value = str(get_user_data_directory("results"))
                folder_state["value"] = folder_value
                folder_input.set_value(folder_value)
                ui.notify("Using Launchpad results directory", type="info")
                download_button.enable()

            with ui.row().classes("w-full"):
                with ui.button("Data", on_click=_select_data, icon="folder_special", color="purple-400").mark(
                    "BUTTON_DOWNLOAD_DESTINATION_DATA"
                ):
                    ui.tooltip("Use Launchpad results directory")
                ui.space()
                with ui.button("Custom", on_click=_select_download_destination, icon="folder").mark(
                    "BUTTON_DOWNLOAD_DESTINATION_SELECT"
                ):
                    ui.tooltip("Select custom directory")

        download_item_status = ui.label("")
        download_item_status.set_visibility(False)
        download_item_progress = ui.linear_progress(value=0, show_value=False).props("instant-feedback")
        download_item_progress.set_visibility(False)
        download_artifact_status = ui.label("")
        download_artifact_status.set_visibility(False)
        download_artifact_progress = ui.linear_progress(value=0, show_value=False).props("instant-feedback")
        download_artifact_progress.set_visibility(False)

        # Create a mutable container for the progress queue that will be set when download starts
        # This allows the timer callback to access the queue that's created during start_download
        progress_state: dict[str, Any] = {"queue": None}

        def update_download_progress() -> None:  # noqa: C901, PLR0912
            """Update the progress indicator with values from the queue."""
            progress_queue = progress_state.get("queue")
            if progress_queue is None:
                return
            while not progress_queue.empty():
                progress = progress_queue.get()
                if progress.status is DownloadProgressState.DOWNLOADING_INPUT:
                    status_text = (
                        f"Downloading input slide {progress.item_index + 1} of {progress.item_count}"
                        if progress.item_index is not None and progress.item_count
                        else "Downloading input slide ..."
                    )
                elif progress.status is DownloadProgressState.DOWNLOADING and progress.total_artifact_index is not None:
                    status_text = (
                        f"Downloading artifact {progress.total_artifact_index + 1} of {progress.total_artifact_count}"
                    )
                else:
                    status_text = progress.status

                download_item_status.set_text(status_text)
                download_item_status.set_visibility(True)
                download_item_progress.set_value(progress.item_progress_normalized)
                download_artifact_progress.set_value(progress.artifact_progress_normalized)
                if progress.status is DownloadProgressState.INITIALIZING:
                    download_artifact_status.set_visibility(False)
                    download_item_progress.set_visibility(False)
                    download_artifact_progress.set_visibility(False)
                elif progress.status is DownloadProgressState.DOWNLOADING_INPUT:
                    if progress.input_slide_path:
                        download_artifact_status.set_text(f"Input: {progress.input_slide_path.name}")
                    download_artifact_status.set_visibility(True)
                    download_item_progress.set_visibility(True)
                    download_artifact_progress.set_visibility(True)
                elif progress.status is DownloadProgressState.DOWNLOADING:
                    if progress.artifact_path:
                        download_artifact_status.set_text(str(progress.artifact_path))
                    download_artifact_status.set_visibility(True)
                    download_item_progress.set_visibility(True)
                    download_artifact_progress.set_visibility(True)
                elif progress.status is DownloadProgressState.QUPATH_ADD_INPUT and progress.qupath_add_input_progress:
                    download_artifact_status.set_text(progress.qupath_add_input_progress.status)
                    download_artifact_status.set_visibility(True)
                    download_item_progress.set_visibility(True)
                    download_artifact_progress.set_visibility(False)
                elif (
                    progress.status is DownloadProgressState.QUPATH_ADD_RESULTS and progress.qupath_add_results_progress
                ):
                    download_artifact_status.set_text(progress.qupath_add_results_progress.status)
                    download_artifact_status.set_visibility(True)
                    download_item_progress.set_visibility(True)
                    download_artifact_progress.set_visibility(False)
                elif (
                    progress.status is DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
                    and progress.qupath_annotate_input_with_results_progress
                ):
                    download_artifact_status.set_text(progress.qupath_annotate_input_with_results_progress.status)
                    download_artifact_status.set_visibility(True)
                    download_item_progress.set_visibility(True)
                    download_artifact_progress.set_visibility(True)
                else:
                    download_artifact_status.set_text("")
                    download_item_progress.set_visibility(False)
                    download_artifact_progress.set_visibility(False)

        # Create the timer during dialog construction (in valid slot context), but inactive initially
        # This avoids RuntimeError when trying to create timer inside async event handler
        progress_timer = ui.timer(0.1, update_download_progress, active=False)

        async def start_download() -> None:
            # Read from download_options dict (defined outside @ui.refreshable) to get current values
            current_qupath_project = download_options["qupath_project"]
            current_marimo = download_options["marimo"]
            current_folder = folder_state["value"]
            if not current_folder:
                ui.notify("Please select a folder first", type="warning")
                return

            ui.notify("Downloading ...", type="info")
            progress_queue = Manager().Queue()
            progress_state["queue"] = progress_queue  # Store queue so timer callback can access it

            # Activate the timer now that download is starting
            progress_timer.activate()
            try:
                download_button.disable()
                download_button.props(add="loading")
                results_folder = await nicegui_run.cpu_bound(
                    Service.application_run_download_static,
                    run_id=run.run_id,
                    destination_directory=Path(current_folder),
                    wait_for_completion=True,
                    qupath_project=current_qupath_project,
                    download_progress_queue=progress_queue,
                )
                if not results_folder:
                    message = "Download returned without results folder."
                    raise ValueError(message)  # noqa: TRY301
                if current_qupath_project:
                    if results_folder:
                        ui.notify("Download and QuPath project creation completed.", type="positive")
                        download_item_status.set_text("Opening QuPath ...")
                        await open_qupath(project=results_folder / "qupath", button=download_button)
                elif current_marimo:
                    ui.notify("Download and Notebook preparation completed.", type="positive")
                    download_item_status.set_text("Opening Notebook ...")
                    open_marimo(results_folder=results_folder, button=download_button)
                else:
                    ui.notify("Download completed.", type="positive")
                show_in_file_manager(str(results_folder))
            except ValueError as e:
                ui.notify(f"Download failed: {e}", type="negative", multi_line=True)
                progress_timer.deactivate()
                progress_state["queue"] = None
                return
            progress_timer.deactivate()
            progress_state["queue"] = None
            download_button.props(remove="loading")
            download_button.enable()
            download_item_status.set_visibility(False)
            download_item_progress.set_visibility(False)
            download_artifact_status.set_visibility(False)
            download_artifact_progress.set_visibility(False)

        ui.separator()
        with ui.row(align_items="end").classes("w-full justify-end"):
            if qupath_project:
                label = "Visualize with QuPath"
                icon = "zoom_in"
            elif marimo:
                label = "Analyze with Notebook"
                icon = "analytics"
            else:
                label = "Download all results"
                icon = "cloud_download"

            download_button = (
                ui.button(
                    label,
                    icon=icon,
                    on_click=start_download,
                )
                .props("color=primary")
                .mark("DIALOG_BUTTON_DOWNLOAD_RUN")
            )
            if not folder_state["value"]:  # Disable download button initially, will be enabled when folder is selected
                download_button.disable()

            ui.space()
            ui.button("Close", on_click=download_run_dialog.close).props("flat")

    with ui.dialog().props(add="persistent") as download_run_dialog, ui.card().style(WIDTH_1200px):
        download_run_dialog_content()

    def download_run_dialog_open(qupath_project: bool = False, marimo: bool = False) -> None:
        """Open the run dialog."""
        download_run_dialog_content.refresh(qupath_project=qupath_project, marimo=marimo)
        download_run_dialog.open()

    @ui.refreshable
    def csv_view_dialog_content(title: str | None, url: str | None) -> None:
        if title:
            ui.label(title).classes("text-h5")
        if url:
            try:
                csv_df = pd.read_csv(url, comment="#")
            except Exception as e:
                ui.notify(f"Failed to load CSV: {e!s}", type="negative")
                csv_df = pd.DataFrame()  # Empty dataframe as fallback
            ui.aggrid.from_pandas(csv_df)

    with ui.dialog() as csv_view_dialog, ui.card().style(WIDTH_1200px):
        csv_view_dialog_content(title=None, url=None)
        with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
            ui.button("Close", on_click=csv_view_dialog.close)

    def csv_dialog_open(title: str, url: str) -> None:
        """Open the CSV dialog."""
        csv_view_dialog_content.refresh(title=title, url=url)
        csv_view_dialog.open()

    @ui.refreshable
    def metadata_dialog_content(title: str | None, metadata: str | None) -> None:
        if title:
            ui.label(title).classes("text-h5")
        if metadata:
            try:
                ui.json_editor({
                    "content": {"json": metadata},
                    "mode": "tree",
                    "readOnly": True,
                    "mainMenuBar": False,
                    "navigationBar": True,
                    "statusBar": False,
                }).classes("full-width")
            except Exception as e:
                ui.notify(f"Failed to render metadata: {e!s}", type="negative")

    with ui.dialog() as metadata_dialog, ui.card().style(WIDTH_1200px):
        metadata_dialog_content(title=None, metadata=None)
        with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
            ui.button("Close", on_click=metadata_dialog.close)

    def metadata_dialog_open(title: str, metadata: dict[str, Any]) -> None:
        """Open the Meta dialog."""
        metadata_dialog_content.refresh(title=title, metadata=metadata)
        metadata_dialog.open()

    @ui.refreshable
    def tiff_view_dialog_content(title: str | None, url: str | None) -> None:
        if title:
            ui.label(title).classes("text-h5")
        if url:
            try:
                with ui.scroll_area().classes("w-full h-[calc(100vh-2rem)]"):
                    ui.image("/tiff?url=" + quote(url))
            except Exception as e:
                ui.notify(f"Failed to load CSV: {e!s}", type="negative")

    with ui.dialog() as tiff_view_dialog, ui.card().style(WIDTH_1200px):
        tiff_view_dialog_content(title=None, url=None)
        with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
            ui.button("Close", on_click=tiff_view_dialog.close)

    def tiff_dialog_open(title: str, url: str) -> None:
        """Open the TIFF dialog.

        Args:
            title (str): The title of the TIFF dialog.
            url (str): The URL of the TIFF image.

        """
        tiff_view_dialog_content.refresh(title=title, url=url)
        tiff_view_dialog.open()

    @ui.refreshable
    def custom_metadata_dialog_content(title: str | None, custom_metadata: str | None) -> None:
        if title:
            ui.label(title).classes("text-h5")
        if custom_metadata:
            try:
                ui.json_editor({
                    "content": {"json": custom_metadata},
                    "mode": "tree",
                    "readOnly": True,
                    "mainMenuBar": False,
                    "navigationBar": True,
                    "statusBar": False,
                }).classes("full-width")
            except Exception as e:
                ui.notify(f"Failed to render metadata: {e!s}", type="negative")

    with ui.dialog() as custom_metadata_dialog, ui.card().style(WIDTH_1200px):
        custom_metadata_dialog_content(title=None, custom_metadata=None)
        with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
            ui.button("Close", on_click=custom_metadata_dialog.close)

    def custom_metadata_dialog_open(title: str, custom_metadata: dict[str, Any]) -> None:
        """Open the Custom Metadata dialog."""
        custom_metadata_dialog_content.refresh(title=title, custom_metadata=custom_metadata)
        custom_metadata_dialog.open()

    async def open_qupath(
        project: Path | None = None, image: Path | str | None = None, button: ui.button | None = None
    ) -> None:
        """Launch QuPath."""
        try:
            if button:
                button.disable()
                button.props(add="loading")
            ui.notify("Opening QuPath ...", type="info")
            pid = await nicegui_run.cpu_bound(QuPathService.execute_qupath, project=project, image=image)
            if pid:
                message = f"QuPath opened successfully with process id '{pid}'."
                logger.debug(message)
                ui.notify(message, type="positive")
            else:
                message = "Failed to launch QuPath."
                logger.error(message)
                ui.notify(message, type="negative")
        except Exception as e:
            message = f"Failed to launch QuPath: {e!s}."
            logger.exception(message)
            ui.notify("Failed to launch QuPath.", type="negative")
        if button:
            button.enable()
            button.props(remove="loading")

    def open_marimo(results_folder: Path, button: ui.button | None = None) -> None:
        if button:
            button.disable()
            button.props(add="loading")
        ui.navigate.to(f"/notebook/{run.run_id}?results_folder={quote(results_folder.as_posix())}")
        ui.navigate.reload()  # TODO(Helmut): Find out why this workaround works. Was just a hunch ...

    if run_data:  # noqa: PLR1702
        with ui.row().classes("w-full justify-center"):
            expansion = ui.expansion(text=f"Run {run.run_id}", icon="info")
            expansion.on_value_change(
                lambda e: expansion.classes(add="w-full" if e.value else "", remove="w-full" if not e.value else "")
            )
            with expansion:
                submitted_at = run_data.submitted_at.astimezone()
                terminated_at = run_data.terminated_at.astimezone() if run_data.terminated_at else None
                if submitted_at and terminated_at:
                    duration_seconds = (terminated_at - submitted_at).total_seconds()
                    duration_str = humanize.precisedelta(duration_seconds, format="%0.0f")
                else:
                    duration_str = "N/A"

                if run_data.state is RunState.TERMINATED and run_data.termination_reason:
                    status_str = f"{run_data.state.value} ({run_data.termination_reason.name})"
                else:
                    status_str = f"{run_data.state.value}"

                ui.code(
                    f"""
                    * Run ID: {run_data.run_id}
                    * Application: {run_data.application_id} ({run_data.version_number})
                    * Status: {status_str}
                    * Queue Position: {queue_position_string_from_run(run_data)}
                    * Output: {run_data.output.name}
                        - {run_data.statistics.item_count} items
                        - {run_data.statistics.item_pending_count} pending
                        - {run_data.statistics.item_processing_count} processing
                        - {run_data.statistics.item_skipped_count} skipped
                        - {run_data.statistics.item_succeeded_count} succeeded
                        - {run_data.statistics.item_user_error_count} user errors
                        - {run_data.statistics.item_system_error_count} system errors
                    * Submitted: {submitted_at.strftime("%m-%d %H:%M")} ({run_data.submitted_by})
                    * Terminated: {terminated_at.strftime("%m-%d %H:%M") if terminated_at else "N/A"} ({duration_str})
                    * Error: {run_data.error_message or "N/A"} ({run_data.error_code or "N/A"})
                    """,
                    language="markdown",
                ).classes("full-width").mark("CODE_RUN_METADATA")
                if run_data.custom_metadata:
                    is_editable = user_info and user_info.role in {"admin", "super_admin"}
                    properties = {
                        "content": {"json": run_data.custom_metadata},
                        "mode": "tree",
                        "readOnly": not is_editable,
                        "mainMenuBar": True,
                        "navigationBar": False,
                        "statusBar": False,
                    }

                    async def handle_metadata_change(e: Any) -> None:  # noqa: ANN401
                        """Handle changes to the custom metadata and update the run."""
                        if not is_editable:
                            return
                        try:
                            # Extract the new metadata from the event's content attribute
                            new_metadata = e.content.get("json") if hasattr(e, "content") else None
                            if new_metadata:
                                ui.notify("Updating custom metadata...", type="info")
                                await nicegui_run.io_bound(
                                    Service.application_run_update_custom_metadata_static,
                                    run_id=run_id,
                                    custom_metadata=new_metadata,
                                )
                                ui.notify("Custom metadata updated successfully!", type="positive")
                                ui.navigate.reload()
                        except Exception as ex:
                            ui.notify(f"Failed to update custom metadata: {ex!s}", type="negative")

                    ui.json_editor(properties, on_change=handle_metadata_change).classes("full-width").mark(
                        "JSON_EDITOR_CUSTOM_METADATA"
                    )
            ui.space()
            with ui.row().classes("justify-end"):
                if run_data.state.value == RunState.TERMINATED and run_data.statistics.item_succeeded_count > 0:
                    with ui.button_group().props("push"):
                        with (
                            ui.button("Download", icon="cloud_download", on_click=lambda _: download_run_dialog_open())
                            .mark("BUTTON_DOWNLOAD_RUN")
                            .props("push")
                        ):
                            ui.tooltip("Download all results of this run")
                        if find_spec("ijson") and QuPathService.is_qupath_installed():
                            with (
                                ui.button(
                                    "QuPath",
                                    icon="zoom_in",
                                    on_click=lambda _: download_run_dialog_open(qupath_project=True),
                                )
                                .mark("BUTTON_OPEN_QUPATH")
                                .props("push")
                            ):
                                ui.tooltip("Open results in QuPath Microscopy Viewer")
                        if find_spec("marimo"):
                            with (
                                ui.button(
                                    "Marimo",
                                    icon="analytics",
                                    on_click=lambda _: download_run_dialog_open(qupath_project=False, marimo=True),
                                )
                                .mark("BUTTON_OPEN_NOTEBOOK")
                                .props("push")
                            ):
                                ui.tooltip("Open results in Python Notebook served by Marimo")

                if run_data.state.value in {RunState.PENDING, RunState.PROCESSING}:
                    cancel_button = ui.button(
                        "Cancel",
                        color="red",
                        on_click=lambda: _cancel(run.run_id),
                        icon="cancel",
                    ).mark("BUTTON_APPLICATION_RUN_CANCEL")

                if run_data:
                    delete_button = ui.button(
                        "Delete",
                        color="red",
                        on_click=lambda: _delete(run.run_id),
                        icon="delete",
                    ).mark("BUTTON_APPLICATION_RUN_RESULT_DELETE")

        note = run_data.custom_metadata.get("sdk", {}).get("note") if run_data.custom_metadata else None
        if note:
            with ui.card().classes("full-width bg-aignostics-light"):
                ui.label("Note:").classes("text-italic text-sm text-gray-500")
                ui.label(str(note)).classes("-mt-4")

        tags = run_data.custom_metadata.get("sdk", {}).get("tags") if run_data.custom_metadata else None
        if tags and len(tags):
            with ui.row().classes("gap-1 -mt-2 full-width"):
                for tag in tags[:20]:
                    ui.chip(
                        tag,
                        on_click=lambda t=tag: ui.navigate.to(f"/?query={quote(str(t))}"),
                    ).props("small outlined clickable").classes("bg-white text-black")

        # Pagination state
        results_iterator = run.results()
        displayed_results: list[ItemResult] = []
        has_more_results = True

        def render_item(item: ItemResult) -> None:  # noqa: C901, PLR0912, PLR0915
            """Render a single result item."""
            with ui.item().classes("h-96 px-0").props("clickable"):
                with (
                    ui.item_section().classes("h-full"),
                    ui.card().tight().classes("h-full"),
                    ui.row().classes("w-full"),
                ):
                    image_file: Path | None = Path(item.external_id).resolve()
                    if image_file and image_file.is_file():
                        image_url = "/thumbnail?source=" + quote(image_file.as_posix())
                    else:
                        image_file = None
                        image_url = "/application_assets/image-not-found.png"
                    ui.image(image_url).classes("object-contain absolute-center max-h-full")
                    icon, color = run_item_status_and_termination_reason_to_icon_and_color(
                        item.state.value, item.termination_reason
                    )
                    with ui.row().classes("justify-center w-full"):
                        with ui.icon(icon, color=color).classes("text-4xl pl-2 pt-1").props("floating"):
                            tooltip = f"Item {item.item_id}, status {item.state.value.upper()}"
                            if item.termination_reason:
                                tooltip += f" ({item.termination_reason})"
                            ui.tooltip(tooltip)
                        ui.space()
                        with ui.button_group():
                            if find_spec("ijson") and QuPathService.is_qupath_installed():
                                with ui.button(
                                    icon="zoom_in",
                                    color="primary",
                                ).props("floating") as qupath_button:
                                    qupath_button.on_click(
                                        lambda _, image_file=image_file, qupath_button=qupath_button: open_qupath(
                                            image=image_file, button=qupath_button
                                        )
                                    )
                                    ui.tooltip("Open in QuPath")
                            if item.custom_metadata:
                                with ui.button(
                                    icon="info",
                                    on_click=lambda _,
                                    custom_metadata=item.custom_metadata,
                                    external_id=item.external_id: custom_metadata_dialog_open(
                                        title=f"Custom Metadata of item {external_id} ",
                                        custom_metadata=custom_metadata,
                                    ),
                                ).props("floating"):
                                    ui.tooltip("Show custom metadata")
                            if image_file:
                                with ui.button(
                                    icon="folder_open",
                                    on_click=lambda _, image_file=image_file: show_in_file_manager(
                                        str(image_file.parent)
                                    ),
                                ).props("floating"):
                                    ui.tooltip("Open folder")
                    with ui.row().classes("absolute-bottom h-32 bg-indigo-700 bg-opacity-80 content-center w-full p-4"):
                        ui.label(item.external_id).classes(
                            "text-center break-all text-white font-semibold text-shadow-lg/30"
                        )
                if item.output is ItemOutput.FULL:
                    with ui.item_section().classes("w-full"), ui.scroll_area().classes("h-full p-0"):
                        for artifact in sorted(item.output_artifacts, key=lambda a: str(a.name)):
                            mime_type = get_mime_type_for_artifact(artifact)
                            with ui.expansion(
                                str(artifact.name),
                                icon=mime_type_to_icon(mime_type),
                                group="artifacts",
                            ).classes("w-full"):
                                if artifact.download_url:
                                    url = artifact.download_url
                                    title = artifact.name
                                    metadata = artifact.metadata
                                    with ui.button_group():
                                        if mime_type == "image/tiff":
                                            ui.button(
                                                "Preview",
                                                icon=mime_type_to_icon(mime_type),
                                                on_click=lambda _, url=url, title=title: tiff_dialog_open(title, url),
                                            )
                                        if mime_type == "text/csv":
                                            ui.button(
                                                "Preview",
                                                icon=mime_type_to_icon(mime_type),
                                                on_click=lambda _, url=url, title=title: csv_dialog_open(title, url),
                                            )
                                        if url:
                                            ui.button(
                                                text="Download",
                                                icon="cloud_download",
                                                on_click=lambda _, url=url: webbrowser.open(url),
                                            )
                                        if metadata:
                                            ui.button(
                                                text="Schema",
                                                icon="schema",
                                                on_click=lambda _, title=title, metadata=metadata: metadata_dialog_open(
                                                    title, metadata
                                                ),
                                            )
                elif item.state is ItemState.TERMINATED:
                    if item.error_message:
                        with (
                            ui.row()
                            .classes("w-1/2 justify-start items-start content-start ml-4")
                            .style("max-width: 50%;")
                        ):
                            ui.code(
                                f"Error: {item.error_message}, code: {item.error_code or 'N/A'}",
                                language="markdown",
                            ).classes("ml-8").style("width: 100%; max-width: 100%;")
                    else:
                        with ui.row().classes("w-1/2 justify-center content-center"):
                            ui.space()
                            ui.html(
                                '<dotlottie-player src="/application_assets/error.lottie" '
                                'background="transparent" speed="1" style="width: 300px; height: 300px" '
                                'direction="1" playMode="normal" loop autoplay></dotlottie-player>',
                                sanitize=False,
                            )
                            ui.space()
                else:
                    with ui.row().classes("w-1/2 justify-center content-center"):
                        ui.space()
                        animation_file = {
                            ItemState.PENDING: "pending.lottie",
                            ItemState.PROCESSING: "processing.lottie",  # TODO(Helmut): Different icon
                        }[item.state]
                        ui.html(
                            f'<dotlottie-player src="/application_assets/{animation_file}" '
                            'background="transparent" speed="1" style="width: 300px; height: 300px" '
                            'direction="1" playMode="normal" loop autoplay></dotlottie-player>',
                            sanitize=False,
                        )
                        ui.space()

        def fetch_next_batch() -> list[ItemResult]:
            """Fetch the next batch of results from the iterator.

            Returns:
                list[ItemResult]: The next batch of results, up to RESULTS_PAGE_SIZE items.
            """
            nonlocal has_more_results
            batch: list[ItemResult] = []
            for _ in range(RESULTS_PAGE_SIZE):
                try:
                    item = next(results_iterator)
                    batch.append(item)
                except StopIteration:
                    has_more_results = False
                    break
            return batch

        # Load initial batch
        initial_batch = await nicegui_run.io_bound(fetch_next_batch)
        displayed_results.extend(initial_batch)

        # Check if there are no results at all
        if not displayed_results:
            with ui.row().classes("w-full justify-center content-center"):
                ui.space()
                ui.html(
                    '<dotlottie-player src="/application_assets/empty.lottie" '
                    'background="transparent" speed="1" style="width: 700px; height: 700px" '
                    'direction="1" playMode="normal" loop autoplay></dotlottie-player>',
                    sanitize=False,
                )
                ui.space()
            return

        # Create the results list container
        results_list = ui.list().classes("full-width")

        # Render initial results
        with results_list:
            for item in displayed_results:
                render_item(item)

        # Calculate if we need pagination before creating UI elements
        remaining_initial = run_data.statistics.item_count - len(displayed_results)
        needs_pagination = has_more_results and remaining_initial > 0

        # Only create "Show more" button if there are more results to load
        show_more_container: ui.row | None = None
        show_more_button: ui.button | None = None

        if needs_pagination:
            show_more_container = ui.row().classes("w-full justify-center mt-4")

            async def load_more() -> None:
                """Load and render the next batch of results."""
                nonlocal has_more_results
                # These are guaranteed to be set since load_more is only defined when needs_pagination is True
                if show_more_button is None or show_more_container is None:
                    return  # Should never happen, but satisfies type checker

                show_more_button.disable()
                show_more_button.props(add="loading")

                # Fetch next batch
                next_batch = await nicegui_run.io_bound(fetch_next_batch)
                displayed_results.extend(next_batch)

                # Render new items
                with results_list:
                    for item in next_batch:
                        render_item(item)

                show_more_button.props(remove="loading")

                # Hide button if no more results or remaining count is 0
                remaining = run_data.statistics.item_count - len(displayed_results)
                if not has_more_results or remaining <= 0:
                    show_more_container.set_visibility(False)
                else:
                    show_more_button.enable()
                    # Update button text with count
                    show_more_button.text = f"Show more ({remaining} remaining)"

            # Add "Show more" button
            with show_more_container:
                show_more_button = (
                    ui.button(
                        f"Show more ({remaining_initial} remaining)",
                        icon="expand_more",
                        on_click=load_more,
                    )
                    .props("outline")
                    .mark("BUTTON_SHOW_MORE_RESULTS")
                )
