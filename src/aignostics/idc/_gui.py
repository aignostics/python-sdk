"""GUI for IDC."""

from multiprocessing import Manager
from pathlib import Path

from showinfm import show_in_file_manager

from aignostics.gui import frame

from ..utils import BasePageBuilder, GUILocalFilePicker  # noqa: TID252
from ._service import TARGET_LAYOUT_DEFAULT, Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import binding, run, ui  # noqa: PLC0415
        from nicegui.events import ValueChangeEventArguments  # noqa: PLC0415

        @binding.bindable_dataclass
        class DownloadForm:
            """Download."""

            source: str | None = None
            destination: Path | None = None
            download_button: ui.button | None = None
            destination_label: ui.label | None = None
            destination_open_button: ui.button | None = None

        download_form = DownloadForm()

        @ui.page("/idc")
        async def page_idc() -> None:
            """IDC page."""
            with frame("National Cancer Institute - Image Data Commons", False):
                pass
            ui.image("https://storage.googleapis.com/idc-prod-web-static-files/static/img/NIH_IDC_title.svg").classes(
                "w-64"
            )
            ui.markdown("""
                ##### Download DICOM datasets from IDC Portal of NCI
                1. Explore the Image Data Commons (IDC) Portal of National Cancer Institute (NCI) to find DICOM datasets of interest.
                2. Copy and paste a Case UID, Study Instance UID or Series Instance UID into your clipboard.
                3. Paste the UID into the source field below. You can use '1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0' as an example.
                4. Click the destination button and folder.
                5. Click the download button to start the download. A progress bar will appear.
                6. Use the menu to go to Home and run application on the downloaded dataset.
                """)
            with ui.link(target="https://portal.imaging.datacommons.cancer.gov/explore/", new_tab=True):
                ui.button("Explore")
            ui.label("Download Dataset").classes("text-h6")

            def _on_source_input_change(e: ValueChangeEventArguments) -> None:
                """On change event."""
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
                from nicegui import ui  # noqa: PLC0415

                result = await GUILocalFilePicker(str(Path.home()), multiple=False)  # type: ignore
                if result and len(result) > 0:
                    path = Path(result[0])
                    if not path.is_dir():
                        download_form.destination = None
                        download_form.destination_label.set_text("No destination selected")
                        download_form.destination_open_button.disable()
                        ui.notify("The selected path is not a directory. Please select a valid directory.")
                    else:
                        download_form.destination = path
                        download_form.destination_label.set_text(str(path))
                        download_form.destination_open_button.enable()
                        ui.notify(f"You chose directory {download_form.destination}.")
                else:
                    download_form.destination = None
                    download_form.destination_label.set_text("No destination selected")
                    download_form.destination_open_button.disable()
                    ui.notify("You did not make a selection. You must chose a destination directory to download to.")
                if (download_form.source is not None) and (download_form.destination is not None):
                    download_form.download_button.enable()
                else:
                    download_form.download_button.disable()

            def _open_destination() -> None:
                """Open the destination directory in the file explorer."""
                show_in_file_manager(str(download_form.destination))

            with ui.row():
                source_input = ui.input(
                    label="Source",
                    placeholder="start typing",
                    on_change=lambda e: _on_source_input_change(e),
                )
                ui.icon("east")
                with ui.column():
                    with ui.row():
                        download_form.destination_label = ui.label(
                            "No destination selected"
                            if download_form.destination is None
                            else download_form.destination
                        )
                        download_form.destination_open_button = ui.button(
                            icon="folder_open", on_click=_open_destination
                        )
                        download_form.destination_open_button.mark("BUTTON_OPEN_DESTINATION").disable()
                    ui.button("Destination", on_click=_select_destination, icon="folder").mark(
                        "BUTTON_DOWNLOAD_DESTINATION"
                    )

            async def _download(source: str) -> None:
                """Download."""
                ui.notify("Download has started: " + source)
                progressbar.visible = True
                await run.cpu_bound(
                    Service.download_with_queue,
                    download_message_queue,
                    source,
                    download_form.destination,
                    TARGET_LAYOUT_DEFAULT,
                    False,
                )
                ui.notify("Download completed.")
                progressbar.visible = False
                _open_destination()

            download_form.download_button = ui.button("Download", icon="cloud_download").mark("BUTTON_DOWNLOAD")
            download_form.download_button.on("click", lambda _: _download(source_input.value))
            download_form.download_button.disable()

            download_message_queue = Manager().Queue()
            ui.timer(
                0.1,
                callback=lambda: progressbar.set_value(
                    download_message_queue.get() if not download_message_queue.empty() else progressbar.value
                ),
            )

            progressbar = ui.linear_progress(value=0).props("instant-feedback")
            progressbar.visible = False
