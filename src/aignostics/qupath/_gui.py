"""GUI of QuPath module."""

from multiprocessing import Manager
from pathlib import Path

import humanize

from aignostics.gui import frame
from aignostics.utils import BasePageBuilder, get_logger

from ._service import InstallProgress, InstallProgressState, Service

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: C901, PLR0915
        from nicegui import app, run, ui  # noq  # noqa: PLC0415

        app.add_static_files("/qupath_assets", Path(__file__).parent / "assets")

        @ui.page("/qupath")
        def page_index() -> None:  # noqa: C901, PLR0915
            """QuPath Extension."""
            with frame("QuPath Extension", left_sidebar=False):
                # Nothing to do here, just to show the page
                pass

            async def install_qupath() -> None:
                def update_install_progress() -> None:
                    """Update the progress indicator with values from the queue."""
                    while not progress_queue.empty():
                        progress: InstallProgress = progress_queue.get()
                        if progress.status is InstallProgressState.DOWNLOADING:
                            if progress.archive_path and progress.archive_size:
                                install_info.set_text(
                                    f"Downloading QuPath v{progress.archive_version} "
                                    f"({humanize.naturalsize(float(progress.archive_size))}) "
                                    f"to {progress.archive_path}"
                                )
                            download_progress.set_value(progress.archive_download_progress_normalized)

                ui.notify("Installing QuPath  ...", type="info")

                progress_queue = Manager().Queue()
                ui.timer(0.1, update_install_progress)

                install_button.props(add="loading")
                install_info.set_text("Connecting with GitHub ...")
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

                download_progress.set_visibility(False)
                install_button.props(remove="loading")

                ui.navigate.reload()

            async def uninstall_qupath() -> None:
                uninstall_button.props(add="loading")
                try:
                    await run.io_bound(Service.uninstall_qupath)
                    ui.notify("QuPath uinstalled successfully.", type="positive")
                except Exception as e:
                    message = f"Failed to uninstall QuPath: {e!s}."
                    logger.exception(message)
                    ui.notify("Failed to uninstall QuPath.", type="negative")

                uninstall_button.props(remove="loading")

                ui.navigate.reload()

            async def launch_qupath() -> None:
                """Launch QuPath."""
                launch_button.props(add="loading")

                try:
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

                launch_button.props(remove="loading")

            version = Service().get_version()
            expected_version = Service().get_expected_version()

            ui.markdown(
                """
                    ### Manage your QuPath Extension
                """
            )
            with ui.row().classes("w-full justify-start"):
                with ui.column().classes("w-2/5"):
                    with ui.card().classes("w-full"):
                        if version:
                            if version.version == expected_version:
                                install_info = ui.label(
                                    f"QuPath {expected_version} is installed and ready to execute. "
                                    "Go to a completed application result and click the QuPath button, "
                                    "or open directly from here."
                                )
                            else:
                                install_info = ui.label(
                                    f"QuPath {version.version} is installed, but version {expected_version} "
                                    "is expected. Please update to the latest version by reinstalling."
                                )
                        else:
                            install_info = ui.label(
                                "Install QuPath to enable visualizing your Whole Slide Image and application results "
                                "with one click. "
                                f"QuPath will be installed at '{Service.get_installation_path()}'. "
                            )

                        download_progress = ui.linear_progress(value=0, show_value=False).props("instant-feedback")
                        download_progress.set_visibility(False)

                        with ui.row().classes("w-full justify-between items-center"):
                            launch_button = ui.button(
                                "Open",
                                on_click=launch_qupath,
                                icon="visibility",
                            ).mark("BUTTON_QUPATH_LAUNCH")
                            if not version:
                                launch_button.disable()
                            ui.space()
                            install_button = ui.button(
                                "Install" if not version else "Reinstall",
                                on_click=install_qupath,
                                icon="install_desktop",
                            ).mark("BUTTON_QUPATH_INSTALL")
                            uninstall_button = ui.button(
                                "Uninstall",
                                on_click=uninstall_qupath,
                                icon="extension_off",
                            ).mark("BUTTON_QUPATH_INSTALL")
                            if not version:
                                uninstall_button.disable()

                    ui.markdown(
                        """
                            ###### What is QuPath?
                            QuPath [1, 2] is a powerful open-source software for digital pathology.
                            It allows you to visualize and annotate whole slide images (WSIs) with ease.

                            Using the Aignostics Launchpad you can install QuPath with one click, and
                            start visualizing your WSIs and application results with ease.

                            *References:*

                            1. <a href="https://qupath.github.io/" target="_blank">QuPath website</a>

                            2. Bankhead, P. et al. QuPath:
                                <a href="https://doi.org/10.1038/s41598-017-17204-5" target="_blank">
                                Open source software for digital pathology image analysis.
                                Scientific Reports (2017)</a>

                            3. <a href="https://qupath.readthedocs.io/en/stable/docs/intro/acknowledgements.html"
                                target="_blank">License</a>
                        """
                    )
                ui.space()
                with ui.column().classes("w-2/5"), ui.row().classes("w-1/2 justify-center content-center"):
                    ui.space()
                    if version:
                        if version.version == expected_version:
                            animation = "/qupath_assets/microscope.lottie"
                        else:
                            animation = "/qupath_assets/update.lottie"
                    else:
                        animation = "/qupath_assets/download.lottie"
                    ui.html(
                        f"<dotlottie-player "
                        f'src="{animation}" '
                        f'background="transparent" '
                        f'speed="1" '
                        f'style="width: 300px; height: 300px" '
                        f'direction="1" '
                        f'playMode="normal" '
                        f"loop "
                        f"autoplay>"
                        f"</dotlottie-player>"
                    )
                    ui.space()
