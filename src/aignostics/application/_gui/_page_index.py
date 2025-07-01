"""GUI of application module including homepage of Aignostics Launchpad."""

from importlib.util import find_spec

from nicegui import Client, app, ui  # noq

from aignostics.utils import get_logger

from ._frame import _frame

logger = get_logger(__name__)


async def _page_index(client: Client) -> None:
    """Homepage of Applications."""
    client.content.classes(remove="nicegui-content")
    client.content.classes(add="pl-5 pt-5")

    await _frame("Analyze your Whole Slide Images with AI", left_sidebar=True)

    with ui.row().classes("p-4 pt-2 pr-0"), ui.column():
        await ui.context.client.connected()
        ui.label("Welcome to the Aignostics Launchpad").bind_text_from(
            app.storage.tab,
            "user_info",
            lambda user_info: (
                f"Welcome "
                f"{user_info.profile.given_name if hasattr(user_info, 'profile') and user_info.profile else ''} "
                f"to the Aignostics Launchpad"
            ),
        ).classes("text-4xl mb-2")
        ui.label(
            "Using the Launchpad, you can run Aignostics Atlas applications on your whole slide images, "
            "monitor progress, and download results for analysis."
        ).classes("text-2xl")
        with ui.row().classes("w-full h-screen flex"):
            with ui.column().classes("flex-1 pr-0"):
                ui.label("Have your slides ready to go?").classes("text-xl")
                ui.label(
                    "Select the relevant application from the left sidebar to upload your images to get started."
                ).classes("text")
                ui.label("Looking to test with public data first?").classes("text-xl")
                ui.label(
                    'Open ☰ menu and click "Download Datasets" to select a dataset '
                    "from Image Data Commons by the National Cancer Institute to test with."
                ).classes("text")
                ui.label("Already submitted your slides?").classes("text-xl")
                ui.label(
                    "Select your run on the left to monitor progress, cancel while pending, or download results."
                ).classes("text")

                if find_spec("ijson"):
                    from aignostics.qupath import Service as QuPathService  # noqa: PLC0415

                    ui.label("Visualize results in QuPath Microscopy Viewer?").classes("text-xl")
                    if QuPathService.is_installed():
                        ui.label('Select a completed run and click "QuPath" to visualize results.').classes("text")
                    else:
                        ui.label(
                            "To visualize results with one click the QuPath application must be installed. "
                            'Select "QuPath extension" in the ☰ menu to install.'
                        ).classes("text")

                if find_spec("marimo"):
                    ui.label("Analyze results in Python Notebooks?").classes("text-xl")
                    ui.label('On completed runs click "Marimo" to directly open the notebook.').classes("text")

            with (
                ui.carousel(animated=True, arrows=True, navigation=True)
                .classes("flex-1 h-full m-0 p-0 self-end bg-[#423D6B] ")
                .props("infinite autoplay=1000 control-color=transparent")
            ):
                for i in range(1, 5):  # Loop from 1 to 4
                    with ui.carousel_slide().classes("p-0 m-0"):
                        ui.image(f"/application_assets/home-card-{i}.png").classes("w-full h-auto object-contain")
