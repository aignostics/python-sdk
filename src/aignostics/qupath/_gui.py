"""GUI of QuPath module."""

import queue

import humanize

from aignostics.gui import frame
from aignostics.utils import BasePageBuilder, get_logger

from ._service import InstallProgress, InstallProgressState, Service

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: C901, PLR0915
        from nicegui import run, ui  # noq  # noqa: PLC0415

        @ui.page("/qupath")
        def page_index() -> None:  # noqa: C901, PLR0915
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

                install_button.set_visibility(False)
                install_info.set_text("Connecting with GitHub ...")

                def update_install_progress() -> None:
                    """Update the progress indicator with values from the queue."""
                    if not progress_queue.empty():
                        progress: InstallProgress = progress_queue.get()
                        if progress.status is InstallProgressState.DOWNLOADING:
                            if progress.archive_path and progress.archive_size:
                                install_info.set_text(
                                    f"Downloading QuPath v{progress.archive_version} "
                                    f"({humanize.naturalsize(float(progress.archive_size))}) "
                                    f"to {progress.archive_path}"
                                )
                            download_progress.set_value(progress.archive_download_progress_normalized)

                progress_queue: queue.Queue[InstallProgress] = queue.Queue()
                ui.timer(0.1, update_install_progress)

                download_progress.set_visibility(True)
                try:
                    app_dir = await run.io_bound(
                        Service.install_qupath,
                        progress_queue=progress_queue,
                    )
                    ui.notify(f"QuPath installed successfully to '{app_dir!s}'.", type="positive")
                except Exception as e:
                    message = f"Failed to install QuPath: {e!s}."
                    logger.exception(message)
                    ui.notify("Failed to install QuPath.", type="negative")
                ui.navigate.reload()

            async def launch_qupath() -> None:
                """Launch QuPath."""
                try:
                    launch_button.set_visibility(False)
                    launch_spinner.set_visibility(True)
                    pid = await run.cpu_bound(Service.launch_qupath)
                    if pid:
                        message = f"QuPath launched successfully with process id '{pid}'."
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
                launch_spinner.set_visibility(False)
                launch_button.set_visibility(True)

            installed_path = Service().find_qupath()
            if installed_path:
                install_info = ui.label(f"QuPath is installed and ready to execute at '{installed_path}'.")
                launch_button = ui.button(
                    "Launch QuPath",
                    on_click=launch_qupath,
                    icon="visibility",
                ).mark("BUTTON_QUPATH_LAUNCH")
                launch_spinner = ui.spinner("dots", size="lg")
                launch_spinner.set_visibility(False)
            else:
                installation_path = Service.get_installation_path()
                install_info = ui.label(
                    f"QuPath is not installed at the intended installation path '{installation_path}'."
                )
                install_button = ui.button(
                    "Install QuPath",
                    on_click=install_qupath,
                    icon="download",
                ).mark("BUTTON_QUPATH_INSTALL")
                download_progress = ui.linear_progress(value=0, show_value=False).props("instant-feedback")
                download_progress.set_visibility(False)
