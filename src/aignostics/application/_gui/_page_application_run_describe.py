"""Run describe page, including download, QuPath and Marimo control."""

from importlib.util import find_spec
from multiprocessing import Manager
from pathlib import Path
from typing import Any
from urllib.parse import quote

from nicegui import run as nicegui_run
from nicegui import ui  # noq
from showinfm.showinfm import show_in_file_manager

from aignostics.platform import ApplicationRunStatus, ItemStatus
from aignostics.system import Service as SystemService
from aignostics.utils import GUILocalFilePicker, get_logger

from .._service import DownloadProgressState, Service  # noqa: TID252
from .._utils import get_mime_type_for_artifact  # noqa: TID252
from ._frame import _frame
from ._utils import (
    mime_type_to_icon,
    run_item_status_to_icon_and_color,
    run_status_to_icon_and_color,
)

logger = get_logger(__name__)

WIDTH_100 = "width: 100%"
WIDTH_1200px = "width: 1200px; max-width: none"


async def _page_application_run_describe(application_run_id: str) -> None:  # noqa: C901, PLR0912, PLR0915
    import pandas as pd  # noqa: PLC0415

    if find_spec("paquo"):
        from aignostics.qupath import Service as QuPathService  # noqa: PLC0415

    """Describe Application."""
    service = Service()
    run = service.application_run(application_run_id)
    run_data = run.details()

    if run and run_data:
        icon, color = run_status_to_icon_and_color(run_data.status.value)
        await _frame(
            navigation_title=(
                f"Run of {run_data.application_version_id} "
                f"on {run_data.triggered_at.astimezone().strftime('%m-%d %H:%M')}"
            ),
            navigation_icon=icon,
            navigation_icon_color=color,
            navigation_icon_tooltip=f"Run {run_data.application_run_id}, status {run_data.status.value.upper()}",
            left_sidebar=True,
            args={"application_run_id": application_run_id},
        )
    else:
        await _frame(
            navigation_title=f"Run {application_run_id}",
            navigation_icon="bug_report",
            navigation_icon_color="negative",
            navigation_icon_tooltip="Could not load run data",
            left_sidebar=True,
            args={"application_run_id": application_run_id},
        )

    if run is None:
        ui.label(f"Failed to get run '{application_run_id}'").mark("LABEL_ERROR")  # type: ignore[unreachable]
        return

    def _cancel(run_id: str) -> bool:
        """Cancel the application run.

        Args:
            run_id (str): The ID of the run to cancel.

        Returns:
            bool: True if the run was cancelled, False otherwise.
        """
        ui.notify(f"Canceling application run with id '{run_id}' ...", type="info")
        try:
            service.application_run_cancel(run_id)
            ui.navigate.reload()
            ui.notify("Application run cancelled!", type="positive")
            return True
        except Exception as e:  # noqa: BLE001
            ui.notify(f"Failed to cancel application run: {e}.", type="warning")
            return False

    @ui.refreshable
    def download_run_dialog_content(qupath_project: bool = False, marimo: bool = False) -> None:  # noqa: C901, PLR0915
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

        selected_folder = ui.input("Selected folder", value="").classes("w-full").props("readonly")

        with ui.row().classes("w-full"):

            async def _select_download_destination() -> None:
                result = await GUILocalFilePicker(str(Path.home()), multiple=False)  # type: ignore[misc]
                if result and len(result) > 0:
                    folder_path = Path(result[0])
                    if folder_path.is_dir():
                        selected_folder.value = str(folder_path)
                    else:
                        selected_folder.value = str(folder_path.parent)
                    download_button.enable()
                else:
                    ui.notify("No folder selected", type="warning")

            async def _select_data() -> None:  # noqa: RUF029
                """Open a file picker dialog and show notifier when closed again."""
                selected_folder.value = str(SystemService.get_user_data_directory("results"))
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

        async def start_download() -> None:  # noqa: C901, PLR0915
            if not selected_folder.value:
                ui.notify("Please select a folder first", type="warning")
                return

            ui.notify("Downloading  ...", type="info")
            progress_queue = Manager().Queue()

            def update_download_progress() -> None:
                """Update the progress indicator with values from the queue."""
                while not progress_queue.empty():
                    progress = progress_queue.get()
                    download_item_status.set_text(
                        progress.status
                        if progress.status is not DownloadProgressState.DOWNLOADING
                        or progress.total_artifact_index is None
                        else (
                            f"Downloading artifact {progress.total_artifact_index + 1} "
                            f"of {progress.total_artifact_count}"
                        )
                    )
                    download_item_status.set_visibility(True)
                    download_item_progress.set_value(progress.item_progress_normalized)
                    download_artifact_progress.set_value(progress.artifact_progress_normalized)
                    if progress.status is DownloadProgressState.INITIALIZING:
                        download_artifact_status.set_visibility(False)
                        download_item_progress.set_visibility(False)
                        download_artifact_progress.set_visibility(False)
                    if progress.status is DownloadProgressState.DOWNLOADING:
                        if progress.artifact_path:
                            download_artifact_status.set_text(str(progress.artifact_path))
                        download_artifact_status.set_visibility(True)
                        download_item_progress.set_visibility(True)
                        download_artifact_progress.set_visibility(True)
                    elif (
                        progress.status is DownloadProgressState.QUPATH_ADD_INPUT and progress.qupath_add_input_progress
                    ):
                        download_artifact_status.set_text(progress.qupath_add_input_progress.status)
                        download_artifact_status.set_visibility(True)
                        download_item_progress.set_visibility(True)
                        download_artifact_progress.set_visibility(False)
                    elif (
                        progress.status is DownloadProgressState.QUPATH_ADD_RESULTS
                        and progress.qupath_add_results_progress
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

            ui.timer(0.1, update_download_progress)
            try:
                download_button.disable()
                download_button.props(add="loading")
                results_folder = await nicegui_run.cpu_bound(
                    Service.application_run_download_static,
                    run_id=run.application_run_id,
                    destination_directory=Path(selected_folder.value),
                    wait_for_completion=True,
                    qupath_project=qupath_project,
                    download_progress_queue=progress_queue,
                )
                if qupath_project:
                    ui.notify("Download and QuPath project creation completed.", type="positive")
                    download_item_status.set_text("Opening QuPath ...")
                    await open_qupath(project=results_folder / "qupath", button=download_button)
                elif marimo:
                    ui.notify("Download and Notebook preparation completed.", type="positive")
                    download_item_status.set_text("Opening Notebook ...")
                    open_marimo(results_folder=results_folder, button=download_button)
                else:
                    ui.notify("Download completed.", type="positive")
                show_in_file_manager(str(results_folder))
            except ValueError as e:
                ui.notify(f"Download failed: {e}", type="negative", multi_line=True)
                return
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
            download_button.disable()
            ui.space()
            ui.button("Close", on_click=download_run_dialog.close).props("flat")

    with ui.dialog() as download_run_dialog, ui.card().style(WIDTH_1200px):
        download_run_dialog_content()

    def download_run_dialog_open(qupath_project: bool = False, marimo: bool = False) -> None:
        """Open the CSV dialog."""
        download_run_dialog_content.refresh(qupath_project=qupath_project, marimo=marimo)
        download_run_dialog.open()

    @ui.refreshable
    def csv_view_dialog_content(title: str | None, url: str | None) -> None:
        if title:
            ui.label(title).classes("text-h5")
        if url:
            try:
                csv_df = pd.read_csv(url, comment="#")
            except Exception as e:  # noqa: BLE001
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
                }).style(WIDTH_100)
            except Exception as e:  # noqa: BLE001
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
            except Exception as e:  # noqa: BLE001
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

    async def open_qupath(
        project: Path | None = None, image: Path | str | None = None, button: ui.button | None = None
    ) -> None:
        """Launch QuPath."""
        try:
            if button:
                button.disable()
                button.props(add="loading")
            ui.notify("Opening QuPath ...", type="info")
            pid = await nicegui_run.cpu_bound(QuPathService.launch_qupath, project=project, image=image)
            if pid:
                message = f"QuPath opened successfully with process id '{pid}'."
                logger.info(message)
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
        ui.navigate.to(f"/notebook/{run.application_run_id}?results_folder={quote(results_folder.as_posix())}")

    if run_data:  # noqa: PLR1702
        with ui.row().classes("w-full justify-center"):
            with ui.expansion(text=f"Run {run.application_run_id}"):
                ui.markdown(
                    f"""
                    * Application Version: {run_data.application_version_id}
                    * Triggered by: {run_data.triggered_by}
                    * Organization: {run_data.organization_id}
                    """
                )
            ui.space()
            with ui.row().classes("justify-end"):
                if run_data.status.value == ApplicationRunStatus.COMPLETED:
                    with ui.button_group().props("push"):
                        with (
                            ui.button("Download", icon="cloud_download", on_click=lambda _: download_run_dialog_open())
                            .mark("BUTTON_DOWNLOAD_RUN")
                            .props("push")
                        ):
                            ui.tooltip("Download all results of this run")
                        if find_spec("paquo") and QuPathService.find_qupath():
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
                if run_data.status.value == ApplicationRunStatus.RUNNING:
                    ui.button(
                        "Cancel",
                        color="red",
                        on_click=lambda: _cancel(run.application_run_id),
                        icon="cancel",
                    ).mark("BUTTON_APPLICATION_RUN_CANCEL")

        with ui.list().classes("full-width"):
            results = list(run.results())
            if not results:
                with ui.row().classes("w-full justify-center content-center"):
                    ui.space()
                    ui.html(
                        '<dotlottie-player src="/application_assets/empty.lottie" '
                        'background="transparent" speed="1" style="width: 700px; height: 700px" '
                        'direction="1" playMode="normal" loop autoplay></dotlottie-player>'
                    )
                    ui.space()
                return
            for item in results:
                with ui.item().classes("h-96").props("clickable"):
                    with (
                        ui.item_section().classes("h-full"),
                        ui.card().tight().classes("h-full"),
                        ui.row().classes("w-full"),
                    ):
                        image_file: Path | None = Path(item.reference).resolve()
                        if image_file and image_file.is_file():
                            image_url = "/thumbnail?source=" + quote(image_file.as_posix())
                        else:
                            image_file = None
                            image_url = "/application_assets/image-not-found.png"
                        ui.image(image_url).classes("object-contain absolute-center max-h-full")
                        icon, color = run_item_status_to_icon_and_color(item.status.value)
                        with ui.row().classes("justify-center w-full"):
                            with ui.icon(icon, color=color).classes("text-4xl pl-2 pt-1").props("floating"):
                                if item.error:
                                    ui.tooltip(
                                        f"Item {item.item_id}, status {item.status.value.upper()}, error: {item.error}"
                                    )
                                else:
                                    ui.tooltip(f"Item {item.item_id}, status {item.status.value.upper()}")
                            ui.space()
                            with ui.button_group().props():
                                if find_spec("paquo") and QuPathService.find_qupath():
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
                                if image_file:
                                    with ui.button(
                                        icon="folder_open",
                                        color="primary",
                                        on_click=lambda _, image_file=image_file: show_in_file_manager(
                                            str(image_file.parent)
                                        ),
                                    ).props("floating"):
                                        ui.tooltip("Open folder")
                        with ui.row().classes(
                            "absolute-bottom h-32 bg-indigo-700 bg-opacity-80 content-center w-full p-4"
                        ):
                            ui.label(item.reference).classes(
                                "text-center break-all text-white font-semibold text-shadow-lg/30"
                            )
                    if item.status is ItemStatus.SUCCEEDED:
                        with ui.item_section().classes("w-full"):
                            if item.status is ItemStatus.SUCCEEDED and item.output_artifacts:
                                with ui.scroll_area().classes("h-full").style("padding: 0"):
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
                                                            on_click=lambda _, url=url, title=title: tiff_dialog_open(
                                                                title, url
                                                            ),
                                                        )
                                                    if mime_type == "text/csv":
                                                        ui.button(
                                                            "Preview",
                                                            icon=mime_type_to_icon(mime_type),
                                                            on_click=lambda _, url=url, title=title: csv_dialog_open(
                                                                title, url
                                                            ),
                                                        )
                                                    if url:
                                                        ui.button(
                                                            text="Download",
                                                            icon="cloud_download",
                                                            on_click=lambda _, url=url: ui.download.from_url(url),
                                                        )
                                                    if metadata:
                                                        ui.button(
                                                            text="Schema",
                                                            icon="schema",
                                                            on_click=lambda _,
                                                            title=title,
                                                            metadata=metadata: metadata_dialog_open(title, metadata),
                                                        )
                    elif item.status in {
                        ItemStatus.PENDING,
                        ItemStatus.ERROR_USER,
                        ItemStatus.ERROR_SYSTEM,
                        ItemStatus.CANCELED_USER,
                        ItemStatus.CANCELED_SYSTEM,
                    }:
                        with ui.row().classes("w-1/2 justify-center content-center"):
                            ui.space()
                            animation_file = {
                                ItemStatus.PENDING: "pending.lottie",
                                ItemStatus.ERROR_USER: "error.lottie",
                                ItemStatus.ERROR_SYSTEM: "error.lottie",
                                ItemStatus.CANCELED_USER: "canceled.lottie",
                                ItemStatus.CANCELED_SYSTEM: "canceled.lottie",
                            }[item.status]
                            ui.html(
                                f'<dotlottie-player src="/application_assets/{animation_file}" '
                                'background="transparent" speed="1" style="width: 300px; height: 300px" '
                                'direction="1" playMode="normal" loop autoplay></dotlottie-player>'
                            )
                            ui.space()
