"""Homepage (index) of GUI."""

from pathlib import Path

from nicegui import ui

from aignostics.utils import BasePageBuilder, GUILocalFilePicker

from ._service import Service

SERIES_INSTANCE_ID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"


async def pick_file() -> None:
    """Open a file picker dialog and show notifier when closed again."""
    result = await GUILocalFilePicker(str(Path.cwd() / "examples"), multiple=True)
    ui.notify(f"You chose {result}")


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        @ui.page("/")
        def page_index() -> None:
            """Homepage of GUI."""
            service = Service()
            ui.button("Choose file", on_click=pick_file, icon="folder").mark("BUTTON_CHOOSE_FILE")

            ui.button("Click me", on_click=lambda: ui.notify("Hello, world!"), icon="check").mark("BUTTON_CLICK_ME")

            from importlib.util import find_spec  # noqa: PLC0415

            if find_spec("matplotlib") and find_spec("numpy"):
                import numpy as np  # noqa: PLC0415

                with ui.card().tight().mark("CARD_PLOT"):  # noqa: SIM117
                    with ui.matplotlib(figsize=(4, 3)).figure as fig:
                        x = np.linspace(0.0, 5.0)
                        y = np.cos(2 * np.pi * x) * np.exp(-x)
                        ax = fig.gca()
                        ax.plot(x, y, "-")

            if find_spec("matplotlib") and find_spec("wsidicom"):
                from wsidicom import WsiDicom  # noqa: PLC0415

                if (service.get_data_directory() / SERIES_INSTANCE_ID).exists():
                    slide = WsiDicom.open(service.get_data_directory() / SERIES_INSTANCE_ID)

                    with ui.card().tight().mark("DICOM_PLOT"):  # noqa: SIM117
                        with ui.matplotlib(figsize=(4, 3)).figure as fig:
                            ax = fig.gca()
                            thumbnail = slide.read_thumbnail()
                            ax.imshow(thumbnail)
                            ax.axis("off")

            ui.link("Info", "/info").mark("LINK_INFO")
