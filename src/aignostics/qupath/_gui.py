"""GUI of QuPath module."""

import queue

import humanize

from aignostics.gui import frame
from aignostics.utils import BasePageBuilder, get_logger

from ._service import InstallProgress, InstallProgressState, Service

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import run, ui  # noq  # noqa: PLC0415

        @ui.page("/qupath")
        def page_index() -> None:
            """Homepage of Applications."""
            with frame("QuPath", left_sidebar=False):
                # Nothing to do here, just to show the page
                pass

            ui.markdown(
                """
                    ### Manage your QuPath Installation
                """
            )

            async def install_qupath() -> None:
                ui.notify("Installing QuPath  ...", type="info")

                def update_install_progress() -> None:
                    """Update the progress indicator with values from the queue."""
                    if not progress_queue.empty():
                        progress: InstallProgress = progress_queue.get()
                        if progress.status is InstallProgressState.DOWNLOADING:
                            if progress.archive_path and progress.archive_size:
                                installation_info.set_text(
                                    f"Downloading QuPath v{progress.archive_version} "
                                    f"({humanize.naturalsize(float(progress.archive_size))}) "
                                    f"to {progress.archive_path}"
                                )
                            download_archive_progress.set_value(progress.archive_download_progress_normalized)

                progress_queue: queue.Queue[InstallProgress] = queue.Queue()
                ui.timer(0.1, update_install_progress)

                installation_info.set_visibility(True)
                download_archive_progress.set_visibility(True)
                await run.io_bound(
                    Service.install_qupath,
                    progress_queue=progress_queue,
                )
                ui.notify("Installed QuPath.", type="positive")
                ui.navigate.reload()

            installed_path = Service().find_qupath()
            if installed_path:
                ui.label(f"QuPath is installed and ready to use at '{installed_path}'.")
                ui.button(
                    "Launch QuPath",
                    on_click=lambda: Service().launch_qupath(),
                    icon="visibility",
                )
            else:
                installation_path = Service.get_installation_path()
                ui.label(f"QuPath is not installed at the intended installation path '{installation_path}'.")
                ui.button(
                    "Install QuPath",
                    on_click=install_qupath,
                    icon="download",
                )
                installation_info = ui.label("Connecting with GitHub ...")
                installation_info.set_visibility(False)
                download_archive_progress = ui.linear_progress(value=0, show_value=False).props("instant-feedback")
                download_archive_progress.set_visibility(False)
