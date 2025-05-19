"""GUI of dataset module."""

from multiprocessing import Manager
from pathlib import Path

from showinfm.showinfm import show_in_file_manager

from aignostics.gui import frame

from ..utils import BasePageBuilder, GUILocalFilePicker  # noqa: TID252
from ._service import TARGET_LAYOUT_DEFAULT, Service

MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED = "No download folder selected"
PORTAL_URL = "https://portal.imaging.datacommons.cancer.gov/explore/"
SOURCE_EXAMPLE_ID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: C901, PLR0915 #NOSONAR
        import nicegui  # noqa: PLC0415
        from nicegui import binding, run, ui  # noqa: PLC0415
        from nicegui.events import ValueChangeEventArguments  # noqa: PLC0415

        @binding.bindable_dataclass
        class DownloadForm:
            """Download."""

            source: str | None = None
            destination: Path | None = None
            download_button: ui.button | None = None
            download_progress: ui.circular_progress | None = None
            destination_label: ui.label | None = None
            destination_open_button: ui.button | None = None

        download_form = DownloadForm()

        @ui.page("/dataset/idc")
        async def page_idc() -> None:  # noqa: C901, PLR0915, RUF029
            """IDC page."""
            with frame("Download Datasets from Image Data", left_sidebar=False):
                # No need to do anything here
                pass
            with ui.row(align_items="start").classes("full-width"):
                ui.markdown("""
                    ##### Download DICOM datasets from IDC Portal of NCI
                    1. Click 🔍 Explore Portal to find DICOM datasets of interest.
                    2. Find a collection, patient case, study, series, or instance of interest,
                        and copy one or multiple IDs into the field below.
                    3. If you don't want to explore, simply click on "Example Dataset".
                    4. Use ⌂ Home or 📁 select a download folder and hit ↓ download.
                    5. Run Applications via the ☰ menu, select an application, and the folder
                    """).classes("w-3/5")
                ui.space()
                with ui.column().classes("w-1/5"):
                    ui.image("/assets/NIH_IDC_title.svg").classes("w-25").style("margin-top:1.25rem")
                    with ui.link(target=PORTAL_URL, new_tab=True):
                        ui.button("Explore Portal", icon="search")

            def _on_source_input_change(e: ValueChangeEventArguments) -> None:
                """On change event."""
                if download_form.download_button is None:
                    return
                if e.value:
                    download_form.source = e.value
                else:
                    download_form.source = None
                if (download_form.source is not None) and (download_form.destination is not None):
                    download_form.download_button.enable()
                else:
                    download_form.download_button.disable()

            async def _select_destination() -> None:
                """Open a file picker dialog and show notifier when closed again."""
                if (
                    download_form.destination_label is None
                    or download_form.destination_open_button is None
                    or download_form.download_button is None
                ):
                    return

                result = await GUILocalFilePicker(str(Path.home()), multiple=False)  # type: ignore
                if result and len(result) > 0:
                    path = Path(result[0])
                    if not path.is_dir():
                        download_form.destination = None
                        download_form.destination_label.set_text(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)
                        download_form.destination_open_button.disable()
                        ui.notify(
                            "The selected path is not a directory. Please select a valid directory.", type="warning"
                        )
                    else:
                        download_form.destination = path
                        download_form.destination_label.set_text(str(path))
                        download_form.destination_open_button.enable()
                        ui.notify(f"You chose directory {download_form.destination}.", type="info")
                else:
                    download_form.destination = None
                    download_form.destination_label.set_text(MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED)
                    download_form.destination_open_button.disable()
                    ui.notify("You did not make a selection. You must choose a download folder.", type="warning")
                if (download_form.source is not None) and (download_form.destination is not None):
                    download_form.download_button.enable()
                else:
                    download_form.download_button.disable()

            async def _select_home() -> None:  # noqa: RUF029
                """Open a file picker dialog and show notifier when closed again."""
                if (
                    download_form.destination_label is None
                    or download_form.destination_open_button is None
                    or download_form.download_button is None
                ):
                    return

                download_form.destination = Path.home()
                download_form.destination_label.set_text(str(download_form.destination))
                download_form.destination_open_button.enable()
                if download_form.source is not None:
                    download_form.download_button.enable()
                else:
                    download_form.download_button.disable()

            def _open_destination() -> None:
                """Open the destination directory in the file explorer."""
                show_in_file_manager(str(download_form.destination))

            async def _download(source: str) -> None:
                """Download."""
                if (
                    download_form.destination is None
                    or download_form.download_button is None
                    or download_form.download_progress is None
                    or download_form.destination is None
                ):
                    return
                ui.notify(f"Downloading {source!s} ...", type="info")
                download_form.download_progress.visible = True
                download_form.download_button.visible = False
                try:
                    await run.io_bound(
                        Service.download_with_queue,  # type: ignore[arg-type]
                        download_message_queue,  # type: ignore[unused-ignore] # type: ignore
                        source,
                        str(download_form.destination),
                        TARGET_LAYOUT_DEFAULT,
                        False,
                    )
                except ValueError as e:
                    ui.label("bla")
                    nicegui.ui.notify(f"Download failed: {e}", type="negative", multi_line=True)
                    download_form.download_button.visible = True
                    download_form.download_progress.visible = False
                    return
                ui.notify("Download completed.", type="positive")
                download_form.download_button.visible = True
                download_form.download_progress.visible = False
                _open_destination()

            with ui.card().classes("w-full"):
                ui.label("Download Dataset").classes("text-h6")
                with ui.row(align_items="center").classes("w-full"):
                    source_input = (
                        ui.input(
                            label="Enter ID of collection, patient case, study, series or instance.",
                            placeholder="Click 🔍 Explore Portal to find IDs",
                            on_change=lambda e: _on_source_input_change(e),  # noqa: PLW0108
                        )
                        .props("clearable")
                        .classes("w-2/5")
                        .mark("SOURCE_INPUT")
                    )
                    ui.space()
                    ui.icon(name="east", size="lg", color="primary")
                    ui.space()
                    with ui.row(align_items="center").classes("w-2/5"):
                        ui.space()
                        download_form.destination_label = ui.label(
                            MESSAGE_NO_DOWNLOAD_FOLDER_SELECTED
                            if download_form.destination is None
                            else str(download_form.destination)
                        )
                        download_form.destination_open_button = ui.button(
                            icon="folder_open", on_click=_open_destination, color="secondary"
                        )
                        download_form.destination_open_button.mark("BUTTON_OPEN_DESTINATION").disable()

                with ui.row(align_items="center").classes("w-full"):
                    ui.button(
                        "Use Example Dataset",
                        on_click=lambda _: source_input.set_value(SOURCE_EXAMPLE_ID),
                        icon="folder",
                        color="secondary",
                    ).mark("BUTTON_EXAMPLE_DATASET")
                    ui.space()
                    with ui.row(align_items="center"):
                        download_form.download_button = ui.button("Download", icon="cloud_download").mark(
                            "BUTTON_DOWNLOAD"
                        )
                        download_form.download_button.on("click", lambda _: _download(source_input.value))
                        download_form.download_button.disable()
                        download_form.download_progress = ui.circular_progress(show_value=False).props(
                            "instant-feedback"
                        )
                        with download_form.download_progress:
                            ui.button(icon="cloud_download").props("flat round").disable()
                        download_form.download_progress.visible = False
                    ui.space()
                    ui.button("Use Home", on_click=_select_home, icon="home").mark("BUTTON_DOWNLOAD_DESTINATION_HOME")
                    ui.button("Select Download Folder", on_click=_select_destination, icon="folder").mark(
                        "BUTTON_DOWNLOAD_DESTINATION"
                    )

            download_message_queue = Manager().Queue()

            def update_progress() -> None:
                """Update the progress indicator with values from the queue."""
                if download_form.download_progress is None:
                    return

                if not download_message_queue.empty():
                    new_value = download_message_queue.get()
                    download_form.download_progress.set_value(new_value)

            ui.timer(0.1, update_progress)
