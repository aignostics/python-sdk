"""GUI of bucket module."""

from multiprocessing import Manager
from pathlib import Path

import humanize
from showinfm.showinfm import show_in_file_manager

from aignostics.gui import frame
from aignostics.utils import get_user_data_directory

from ..utils import BasePageBuilder, GUILocalFilePicker  # noqa: TID252
from ._service import DownloadProgress, Service

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: C901, PLR0915
        from nicegui import app, binding, run, ui  # noqa: PLC0415

        app.add_static_files("/bucket_assets", Path(__file__).parent / "assets")

        download_progress_queue = None

        @binding.bindable_dataclass
        class BucketForm:
            """Bucket form."""

            grid: ui.aggrid | None = None
            delete_button: ui.button | None = None
            download_button: ui.button | None = None
            destination: Path | None = None
            destination_label: ui.label | None = None
            destination_open_button: ui.button | None = None
            spinner: ui.spinner | None = None
            download_progress_card: ui.card | None = None
            overall_progress: ui.linear_progress | None = None
            overall_progress_label: ui.label | None = None
            file_progress: ui.linear_progress | None = None
            file_progress_label: ui.label | None = None

        bucket_form = BucketForm()

        @ui.page("/bucket")
        async def page_index() -> None:  # noqa: C901, PLR0915
            """Index page of bucket module."""
            with frame("Manage Cloud Bucket on Aignostics Platform", left_sidebar=False):
                # Nothing to do here, just to show the page
                pass

            with ui.row(align_items="start").classes("w-full"):
                ui.markdown("""
                        ## Managing your cloud bucket
                        1. For analysis whole slide images are
                            temporarily stored in a cloud bucket of the Aignostics Platform.
                        3. The bucket is private and only accessible to you and restricted staff of Aignostics.
                        2. The bucket is securely hosted on Google Cloud in EU.
                        3. All data is encrypted in transit and at rest.
                        4. Any data is automatically deleted after 30 days.
                        5. You can manually delete or download data at any time using the form below.
                        """).classes("w-3/5")
                ui.space()
                ui.image("/bucket_assets/Google-Cloud-logo.png").classes("w-1/5").style("margin-top:1.25rem")

            async def _get_rows() -> list[dict[str, str]]:
                if bucket_form.spinner is not None:
                    bucket_form.spinner.set_visibility(True)
                if bucket_form.grid is not None:
                    bucket_form.grid.set_visibility(False)
                if bucket_form.delete_button is not None:
                    bucket_form.delete_button.set_visibility(False)
                if bucket_form.download_button is not None:
                    bucket_form.download_button.set_visibility(False)
                objs = await run.io_bound(
                    Service.find_static,
                    detail=True,
                )
                if bucket_form.spinner is not None:
                    bucket_form.spinner.set_visibility(False)
                if bucket_form.grid is not None:
                    bucket_form.grid.set_visibility(True)
                if bucket_form.delete_button is not None:
                    bucket_form.delete_button.set_visibility(True)
                if bucket_form.download_button is not None:
                    bucket_form.download_button.set_visibility(True)
                return [
                    {
                        "key": obj["key"],  # type: ignore
                        "last_modified": obj["last_modified"].astimezone().strftime("%x %X %Z"),  # type: ignore
                        "size": f"{obj['size'] / (1024 * 1024 * 1024):.2f} GB",  # type: ignore
                    }
                    for obj in objs
                ]

            async def _delete_selected() -> None:
                """Delete selected objects."""
                if bucket_form.grid is None or bucket_form.delete_button is None:
                    return
                selected_rows = await bucket_form.grid.get_selected_rows()
                if not selected_rows or selected_rows == []:
                    ui.notify("No objects selected.", type="warning")
                    return
                ui.notify(f"Deleting {len(selected_rows)} objects ...", type="info")
                bucket_form.delete_button.props(add="loading")
                try:
                    await run.io_bound(
                        Service.delete_static,
                        [row["key"] for row in selected_rows],
                        True,
                        False,
                    )
                except Exception as e:  # noqa: BLE001
                    ui.notify(f"Error deleting objects: {e}", color="red", type="warning")
                    bucket_form.delete_button.props(remove="loading")
                    return
                ui.notify(f"Deleted {len(selected_rows)} objects.", type="positive")
                bucket_form.delete_button.props(remove="loading")
                bucket_form.delete_button.set_text("Delete")
                bucket_form.delete_button.disable()
                bucket_form.grid.options["rowData"] = await _get_rows()
                bucket_form.grid.update()

            async def _download_selected() -> None:  # noqa: C901, PLR0912
                """Download selected objects with progress tracking."""
                nonlocal download_progress_queue

                # Validation
                if bucket_form.grid is None or bucket_form.download_button is None:
                    return

                selected_rows = await bucket_form.grid.get_selected_rows()
                if not selected_rows:
                    ui.notify("No objects selected.", type="warning")
                    return

                if not bucket_form.destination:
                    ui.notify("No destination selected.", type="warning")
                    return

                # Setup UI for download
                if bucket_form.download_progress_card:
                    bucket_form.download_progress_card.set_visibility(True)
                bucket_form.download_button.props(add="loading")
                bucket_form.download_button.disable()
                # Disable delete button during download
                if bucket_form.delete_button:
                    bucket_form.delete_button.disable()

                # Initialize progress
                if download_progress_queue is None:
                    download_progress_queue = Manager().Queue()
                ui.notify(f"Starting download of {len(selected_rows)} objects ...", type="info")

                def progress_callback(progress: DownloadProgress) -> None:
                    """Progress callback to send updates to the UI."""
                    if download_progress_queue:
                        download_progress_queue.put(progress)

                # Perform download
                try:
                    result = await run.io_bound(
                        Service().download,
                        what=[row["key"] for row in selected_rows],
                        destination=bucket_form.destination,
                        what_is_key=True,
                        progress_callback=progress_callback,
                    )
                    # Show results
                    if result.downloaded:
                        ui.notify(f"Downloaded {len(result.downloaded)} objects.", type="positive")
                    if result.failed:
                        ui.notify(f"Failed to download {len(result.failed)} objects.", type="warning")
                except Exception as e:  # noqa: BLE001
                    ui.notify(f"Error downloading objects: {e}", color="red", type="warning")
                finally:
                    # Reset UI
                    bucket_form.download_button.props(remove="loading")
                    bucket_form.download_button.set_text("Download")
                    bucket_form.download_button.disable()
                    # Re-enable delete button if there are selected rows
                    if bucket_form.delete_button and bucket_form.grid:
                        selected_rows = await bucket_form.grid.get_selected_rows()
                        if selected_rows:
                            bucket_form.delete_button.enable()
                            bucket_form.delete_button.set_text(f"Delete {len(selected_rows)} objects")
                        else:
                            bucket_form.delete_button.disable()
                            bucket_form.delete_button.set_text("Delete")
                    if bucket_form.download_progress_card:
                        bucket_form.download_progress_card.set_visibility(False)

            def update_download_progress() -> None:
                """Update the download progress indicators with values from the queue."""
                if not download_progress_queue or download_progress_queue.empty():
                    return

                while not download_progress_queue.empty():
                    progress: DownloadProgress = download_progress_queue.get()

                    if bucket_form.overall_progress and bucket_form.overall_progress_label:
                        overall_percent = (
                            progress.overall_processed / progress.overall_total if progress.overall_total > 0 else 0
                        )
                        bucket_form.overall_progress.set_value(overall_percent)
                        bucket_form.overall_progress_label.set_text(
                            f"Overall: {progress.overall_processed} / {progress.overall_total} objects"
                        )

                    # Update file progress
                    if bucket_form.file_progress and bucket_form.file_progress_label and progress.current_file_key:
                        file_percent = (
                            progress.current_file_downloaded / progress.current_file_size
                            if progress.current_file_size > 0
                            else 0
                        )
                        bucket_form.file_progress.set_value(file_percent)
                        file_text = (
                            f"Current: {progress.current_file_key} "
                            f"({humanize.naturalsize(progress.current_file_downloaded)}/{humanize.naturalsize(progress.current_file_size)})"
                        )
                        bucket_form.file_progress_label.set_text(file_text)

            async def _update_button_states() -> None:
                """Update button states based on grid selection."""
                if (
                    not bucket_form.grid
                    or not bucket_form.delete_button
                    or not bucket_form.download_button
                    or not bucket_form.destination_open_button
                ):
                    return

                if bucket_form.destination:
                    bucket_form.destination_open_button.enable()
                else:
                    bucket_form.destination_open_button.disable()

                selected_rows = await bucket_form.grid.get_selected_rows()
                if selected_rows and bucket_form.destination:
                    bucket_form.delete_button.enable()
                    bucket_form.delete_button.set_text(f"Delete {len(selected_rows)} objects")
                    bucket_form.download_button.enable()
                    bucket_form.download_button.set_text(f"Download {len(selected_rows)} objects")
                else:
                    bucket_form.delete_button.disable()
                    bucket_form.delete_button.set_text("Delete")
                    bucket_form.download_button.disable()
                    bucket_form.download_button.set_text("Download")

            bucket_form.spinner = ui.spinner(size="lg").classes(
                "absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10"
            )
            bucket_form.spinner.set_visibility(False)

            bucket_form.grid = (
                ui.aggrid({
                    "columnDefs": [
                        {
                            "object": "Key",
                            "field": "key",
                            "checkboxSelection": True,
                            "filter": "agTextColumnFilter",
                        },
                        {
                            "headerName": "Last modified",
                            "field": "last_modified",
                            "filter": "agTextColumnFilter",
                        },
                        {
                            "headerName": "Size",
                            "field": "size",
                        },
                    ],
                    "rowData": await _get_rows(),
                    "rowSelection": "multiple",
                    "enableCellTextSelection": "true",
                    "autoSizeStrategy": {
                        "type": "fitCellContents",
                        "defaultMinWidth": 10,
                    },
                    "domLayout": "normal",
                })
                .classes("ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham")
                .classes("full-width")
                .style("height: 310px")
                .mark("GRID_BUCKET")
                .on("selectionChanged", _update_button_states)
            )

            async def _select_data() -> None:
                """Open a file picker dialog and show notifier when closed again."""
                if (
                    bucket_form.destination_label is None
                    or bucket_form.destination_open_button is None
                    or bucket_form.download_button is None
                ):
                    return

                bucket_form.destination = get_user_data_directory("datasets/idc")
                bucket_form.destination_label.set_text(f"Will download to {bucket_form.destination!s}")
                await _update_button_states()

            async def _select_destination() -> None:
                """Open a file picker dialog and show notifier when closed again."""
                if (
                    bucket_form.destination_label is None
                    or bucket_form.destination_open_button is None
                    or bucket_form.download_button is None
                ):
                    return

                result = await GUILocalFilePicker(str(Path.home()), multiple=False)  # type: ignore
                if result and len(result) > 0:
                    path = Path(result[0])
                    if not path.is_dir():
                        bucket_form.destination = None
                        bucket_form.destination_label.set_text(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)
                        bucket_form.destination_open_button.disable()
                        ui.notify(
                            "The selected path is not a directory. Please select a valid directory.", type="warning"
                        )
                    else:
                        bucket_form.destination = path
                        bucket_form.destination_label.set_text(f"Will download to {bucket_form.destination!s}")
                        bucket_form.destination_open_button.enable()
                        ui.notify(f"You chose directory {bucket_form.destination}.", type="info")
                else:
                    bucket_form.destination = None
                    bucket_form.destination_label.set_text(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)
                    bucket_form.destination_open_button.disable()
                    ui.notify("You did not make a selection. You must choose a download folder.", type="warning")
                await _update_button_states()

            def _open_destination() -> None:
                """Open the destination directory in the file explorer."""
                show_in_file_manager(str(bucket_form.destination))

            with ui.row().classes("w-full gap-4"):
                with ui.column().classes("w-1/2"):
                    with ui.row().classes("w-full"):
                        bucket_form.download_button = (
                            ui.button(
                                "Download",
                                icon="download",
                                on_click=_download_selected,
                            )
                            .mark("BUTTON_DOWNLOAD_OBJECTS")
                            .props("color=primary")
                        )
                        bucket_form.download_button.disable()

                        ui.space()

                        with ui.button("Data", on_click=_select_data, icon="folder_special", color="purple-400").mark(
                            "BUTTON_DOWNLOAD_DESTINATION_DATA"
                        ):
                            ui.tooltip("Use Launchpad datasets directory")

                        with ui.button("Custom", on_click=_select_destination, icon="folder").mark(
                            "BUTTON_DOWNLOAD_DESTINATION"
                        ):
                            ui.tooltip("Select a custom directory")
                    with ui.row(align_items="center").classes("w-full"):
                        bucket_form.destination_label = ui.label(
                            MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED
                            if bucket_form.destination is None
                            else str(f"Will download to {bucket_form.destination}")
                        )
                        ui.space()
                        bucket_form.destination_open_button = ui.button(
                            icon="folder_open", on_click=_open_destination, color="secondary"
                        )
                        bucket_form.destination_open_button.mark("BUTTON_OPEN_DESTINATION").disable()

                ui.space()

                bucket_form.delete_button = (
                    ui.button(
                        "Delete",
                        icon="delete",
                        on_click=_delete_selected,
                    )
                    .mark("BUTTON_DELETE_OBJECTS")
                    .props("color=red")
                    .classes("w-1/5")
                )
                bucket_form.delete_button.disable()

            # Progress card for downloads (initially hidden)
            with ui.card().classes("w-full") as progress_card:
                bucket_form.download_progress_card = progress_card
                ui.label("Download Progress").classes("text-h6")

                bucket_form.overall_progress_label = ui.label("Overall: 0 / 0 objects")
                bucket_form.overall_progress = ui.linear_progress(value=0, show_value=False).classes("w-full")

                bucket_form.file_progress_label = ui.label("Current file: None")
                bucket_form.file_progress = ui.linear_progress(value=0, show_value=False).classes("w-full")

            bucket_form.download_progress_card.set_visibility(False)

            await _select_data()

            ui.timer(
                interval=1,
                callback=lambda: bucket_form.grid.classes(
                    add="ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham",
                    remove="ag-theme-balham" if app.storage.general.get("dark_mode", False) else "ag-theme-balham-dark",
                )
                if bucket_form.grid
                else None,
            )

            # Timer for updating download progress
            ui.timer(interval=0.1, callback=update_download_progress)
