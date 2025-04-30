"""Homepage (index) of GUI."""

from pathlib import Path
from typing import Any

from aignostics.gui import frame
from aignostics.utils import BasePageBuilder, GUILocalFilePicker

from ._service import Service

SERIES_INSTANCE_ID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"


async def pick_file(multiple: bool = True) -> None:
    """Open a file picker dialog and show notifier when closed again."""
    from nicegui import ui  # noqa: PLC0415

    result = await GUILocalFilePicker(str(Path.home()), multiple=multiple)  # type: ignore
    ui.notify(f"You chose {result}")


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: C901, PLR0915
        from nicegui import ElementFilter, context, ui  # noq  # noqa: PLC0415

        def _frame(name: str, left_sidebar: bool = False, args: dict[str, Any] | None = None) -> None:
            if args is None:
                args = {}
            service = Service()
            with frame(name, left_sidebar=left_sidebar):
                ui.label("Applications").classes("text-h6")
                try:
                    for application in service.applications():
                        ui.link(f"{application.name}", f"/application/{application.application_id}").mark(
                            "LABEL_APPLICATION"
                        ).tailwind.font_weight(
                            "bold"
                            if context.client.page.path == "/application/{application_id}"
                            and args.get("application_id") == application.application_id
                            else "normal"
                        )
                except Exception:  # noqa: BLE001
                    ui.label("Failed to list applications.").mark("LABEL_ERROR")

                ui.label("Runs").classes("text-h6")
                try:
                    for application_run in service.application_runs():
                        ui.link(
                            f"{application_run.application_run_id}",
                            f"/application/run/{application_run.application_run_id}",
                        ).mark("LABEL_APPLICATION_RUN").tailwind.font_weight(
                            "bold"
                            if context.client.page.path == "/application/run/{application_run_id}"
                            and args.get("application_run_id") == application_run.application_run_id
                            else "normal"
                        )
                except Exception:  # noqa: BLE001
                    ui.label("Failed to list application runs.").mark("LABEL_ERROR")

        @ui.page("/")
        def page_index() -> None:
            """Homepage of GUI."""
            _frame("Home", left_sidebar=True)

            ui.markdown(
                """
                    ## Welcome to the Aignostics Platform Launcher!
                    1. From the list on the left select an application to run our AI on your data.
                    2. Select a run to view and analyze its results
                """
            )

            with ui.carousel(animated=True, arrows=True, navigation=True).props("height=312px"):
                with ui.carousel_slide().classes("p-0"):
                    # ui.image("/assets/home-card-1.png").classes("w-[768px]")
                    ui.image(
                        "https://raw.githubusercontent.com/aignostics/python-sdk/d2b951d97b2152bdbe39c249a82023ae03ec9c99/gui_assets/home-card-1.png?token=GHSAT0AAAAAACZ3KNX5LF7KIPJ6KEGU5MMC2ASCG5Q"
                    ).classes("w-[768px]")
                with ui.carousel_slide().classes("p-0"):
                    # ui.image("/assets/home-card-2.png").classes("w-[768px]")
                    ui.image(
                        "https://raw.githubusercontent.com/aignostics/python-sdk/d2b951d97b2152bdbe39c249a82023ae03ec9c99/gui_assets/home-card-2.png?token=GHSAT0AAAAAACZ3KNX4ZT2YAVUF2C7Y3DDA2ASCH2A"
                    ).classes("w-[768px]")

        @ui.page("/application/{application_id}")
        async def page_application_describe(application_id: str) -> None:
            """Describe Application."""
            service = Service()
            application = service.application(application_id)

            _frame(
                f"{application.name if application else ''}",
                left_sidebar=True,
                args={"application_id": application_id},
            )

            if application is None:
                ui.label(f"Failed to get application '{application_id}'").mark("LABEL_ERROR")
                return

            ui.markdown(
                f"""
                    > {application.description}

                    Latest version: {service.find_latest_application_version(application)}
                """
            )

            with ui.stepper().props("vertical").classes("w-full") as stepper:
                with ui.step("Whole Slide Images"):
                    ui.label("Pick the whole slide images you want to analyze. We support pyramidal TIFF and DICOM.")
                    ui.button("Select", on_click=pick_file, icon="folder").mark("BUTTON_PICK_FILES")
                    with ui.stepper_navigation():
                        ui.button("Next", on_click=stepper.next)

                with ui.step("Metadata"):
                    ui.label("Check the metadata extracted from the images, and provide additional information.")
                    grid = (
                        ui.aggrid({
                            "defaultColDef": {"flex": 1},
                            "columnDefs": [
                                {"headerName": "Source", "field": "source"},
                                {"headerName": "Staining", "field": "staining"},
                                {
                                    "headerName": "Tissue",
                                    "field": "tissue",
                                    "editable": True,
                                    "cellClassRules": {
                                        "bg-red-300": "!['lung','brain'].includes(x)",
                                        "bg-green-300": "['lung','brain'].includes(x)",
                                    },
                                },
                                {
                                    "headerName": "Disease",
                                    "field": "disease",
                                    "editable": True,
                                    "cellClassRules": {
                                        "bg-red-300": "!['lung','brain'].includes(x)",
                                        "bg-green-300": "['lung','brain'].includes(x)",
                                    },
                                },
                            ],
                            "rowData": [
                                {"source": "bla.tif", "staining": "H&E", "disease": "", "tissue": ""},
                                {"source": "blub.dicom", "staining": "H&E", "disease": "", "tissue": ""},
                                {"source": "hello.tif", "staining": "H&E", "disease": "", "tissue": ""},
                            ],
                            "rowSelection": "multiple",
                        })
                        .on("cellClicked", lambda event: ui.notify(f"Cell value: {event.args['value']}"))
                        .classes("max-h-40")
                    )

                    async def _validate() -> None:
                        rows = await grid.get_client_data()
                        valid = True
                        for row in rows:
                            if (row["tissue"] not in {"lung", "brain"}) or (row["disease"] not in {"lung", "brain"}):
                                valid = False
                                break
                        if not valid:
                            ui.notify("Your metadata is invalid! Check the cells highlighted in red.")
                        else:
                            ui.notify("Your metadata is valid!")
                            for button in ElementFilter(kind=ui.button, marker="BUTTON_METADATA_NEXT"):
                                button.enable()

                    with ui.stepper_navigation():
                        ui.button("Validate", on_click=_validate).mark("BUTTON_METADATA_VALIDATE")
                        ui.button("Next", on_click=stepper.next).mark("BUTTON_METADATA_NEXT").disable()
                        ui.button("Back", on_click=stepper.previous).props("flat")

                with ui.step("Submission"):
                    ui.label("Submit the application run to the platform.")
                    with ui.stepper_navigation():
                        ui.button(
                            "Submit",
                            on_click=lambda: ui.notify("Application Run Submitted!"),
                            icon="check",
                        ).mark("BUTTON_CLICK_ME")
                        ui.button("Back", on_click=stepper.previous).props("flat")

        @ui.page("/application/run/{application_run_id}")
        def page_application_run_describe(application_run_id: str) -> None:
            """Describe Application."""
            _frame("Application Run", left_sidebar=True, args={"application_run_id": application_run_id})
            ui.label(application_run_id).classes("text-h6")

            from importlib.util import find_spec  # noqa: PLC0415

            service = Service()

            if find_spec("matplotlib") and find_spec("numpy"):
                import numpy as np  # noqa: PLC0415

                with ui.card().tight().mark("CARD_PLOT"):  # noqa: SIM117
                    with ui.matplotlib(figsize=(4, 3)).figure as fig:
                        x = np.linspace(0.0, 5.0)
                        y = np.cos(2 * np.pi * x) * np.exp(-x)
                        ax = fig.gca()
                        ax.plot(x, y, "-")

            [ui.label(f"Line {i}") for i in range(100)]

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
