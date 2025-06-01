"""GUI of application module including homepage of Aignostics Launchpad."""

from importlib.util import find_spec

from nicegui import ui  # noq

from aignostics.utils import get_logger

from ._frame import _frame

logger = get_logger(__name__)


async def _page_index() -> None:
    """Homepage of Applications."""
    await _frame("Analyze your Whole Slide Images with AI", left_sidebar=True)

    ui.markdown(
        """
            ## Welcome to the Aignostics Launchpad!
            1. Select an application from the left sidebar and use our wizard to submit a run on your
            whole slide images.
            2. Select a run to monitor progress, cancel while pending, or download results.
        """  # noqa: S608
        + (
            """
            3. For analysis and visualization of results, launch """
            + ("Marimo Notebook" if find_spec("marimo") else "")
            + (" and " if find_spec("marimo") and find_spec("paquo") else "")
            + ("QuPath Microscopy viewer" if find_spec("paquo") else "")
            + " with one click."
            if find_spec("marimo") or find_spec("paquo")
            else ""
        )
        + """
            """
        + ("4" if find_spec("marimo") or find_spec("paquo") else "3")
        + """. Trial with public data? Open **☰** Menu and download datasets from
                Image Data Commons (IDC) by National Cancer Institute (NCI).
        """
    )

    carousel = ui.carousel(animated=True, arrows=True, navigation=True).props(
        "height=369px infinite autoplay=1000 control-color=purple"
    )
    with ui.row(align_items="center").classes("justify-center w-full"), carousel:
        for i in range(1, 5):  # Loop from 1 to 4
            with ui.carousel_slide().classes("p-0"):
                ui.image(f"/application_assets/home-card-{i}.png").classes("w-[860px]")
