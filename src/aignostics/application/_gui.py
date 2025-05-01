"""Homepage (index) of GUI."""

import time
from multiprocessing import Manager
from pathlib import Path
from typing import Any

from aignostics.gui import frame
from aignostics.utils import BasePageBuilder, GUILocalFilePicker, get_logger

from ._service import Service

logger = get_logger(__name__)

SERIES_INSTANCE_ID = "1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:  # noqa: C901, PLR0915
        from nicegui import binding, context, run, ui  # noq  # noqa: PLC0415

        @binding.bindable_dataclass
        class SubmitForm:
            """Submit form."""

            application_version_id: str | None = None
            source: Path | None = None
            wsi_step_label: ui.label | None = None
            wsi_next_button: ui.button | None = None
            metadata: list[dict[str, Any]] | None = None
            metadata_grid: ui.aggrid | None = None
            metadata_next_button: ui.button | None = None
            submission_submit_button: ui.button | None = None

        submit_form = SubmitForm()

        def _application_id_to_icon(application_id: str) -> str:
            """Convert application ID to icon.

            Args:
                application_id (str): The application ID.

            Returns:
                str: The icon name.
            """
            match application_id:
                case "h-e-tme":
                    return "biotech"
                case "he-tme":
                    return "biotech"
                case "two-task-dummy":
                    return "construction"
                case _:
                    return "bug_report"

        def _run_status_to_icon(run_status: str) -> str:
            """Convert run status to icon.

            Args:
                run_status (str): The run status.

            Returns:
                str: The icon name.
            """
            match run_status:
                case "pending":
                    return "pending"
                case "running":
                    return "directions_run"
                case "canceled_system":
                    return "sync_problem"
                case "canceled_user":
                    return "cancel"
                case "completed":
                    return "done_all"
                case _:
                    return "bug_report"

        def _frame(
            navigation_title: str,
            navigation_icon: str | None = None,
            left_sidebar: bool = False,
            args: dict[str, Any] | None = None,
        ) -> None:
            if args is None:
                args = {}
            service = Service()
            with frame(navigation_title=navigation_title, navigation_icon=navigation_icon, left_sidebar=left_sidebar):  # noqa: PLR1702
                ui.label("Applications").classes("text-h6")
                try:
                    for application in service.applications():
                        with ui.row():
                            ui.icon(_application_id_to_icon(application.application_id))
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
                    for run, run_status in service.application_runs_with_status():
                        with ui.row():
                            ui.icon(_run_status_to_icon(run_status.status.value))
                            with ui.column():
                                with ui.link(target=f"/application/run/{run.application_run_id}"):
                                    ui.label(
                                        f"{run_status.application_version_id}",
                                    ).tailwind.font_weight(
                                        "bold"
                                        if context.client.page.path == "/application/run/{application_run_id}"
                                        and args.get("application_run_id") == run.application_run_id
                                        else "normal"
                                    )
                                ui.label(f"triggered on {run_status.triggered_at.astimezone().strftime('%m-%d %H:%M')}")
                except Exception:  # noqa: BLE001
                    ui.label("Failed to list application runs.").mark("LABEL_ERROR")

        @ui.page("/")
        def page_index() -> None:
            """Homepage of Applications."""
            _frame("Aignostics Applications", left_sidebar=True)

            ui.markdown(
                """
                    ## Welcome to the Aignostics Platform Launcher!
                    1. Analyze your whole slide images with our AI.
                        Select an application from the left sidebar and use our wizard to submit a run.
                    2. Select a run to monitor progress and inspect results, or cancel a pending run.
                        Our integration with QuPath enables to visualize results with one click.
                    3. You first want to try out with public data?
                        Our integration
                        with Image Data Commons (IDC) by National Cancer Institute (NCI)
                        makes downloading DICOM datasets easy.
                """
            )

            with ui.carousel(animated=True, arrows=True, navigation=True).props("height=312px"):
                with ui.carousel_slide().classes("p-0"):
                    ui.image("assets/home-card-1.png").classes("w-[768px]")
                with ui.carousel_slide().classes("p-0"):
                    ui.image("assets/home-card-2.png").classes("w-[768px]")

        @ui.page("/application/{application_id}")
        def page_application_describe(application_id: str) -> None:
            """Describe Application."""
            service = Service()
            application = service.application(application_id)

            if application is None:
                _frame(
                    navigation_icon="bug_report",
                    navigation_title=f"{application_id}",
                    left_sidebar=True,
                    args={"application_id": application_id},
                )
                ui.label(f"Failed to get application '{application_id}'").mark("LABEL_ERROR")
                return

            _frame(
                navigation_icon=_application_id_to_icon(application_id),
                navigation_title=f"{application.name if application else ''}",
                left_sidebar=True,
                args={"application_id": application_id},
            )

            application_versions = service.application_versions(application)
            latest_application_version = application_versions[0]
            latest_application_version_id = latest_application_version.application_version_id
            latest_application_version_name = latest_application_version.version
            submit_form.application_version_id = latest_application_version_id

            with ui.dialog() as release_notes_dialog, ui.card():
                ui.label(f'Release notes of {application.name}')
                for application_version in application_versions:
                    ui.label(f"Version {application_version.version}")
                    ui.markdown(
                        f"""
                            > {application_version.changelog}
                        """
                    )
                ui.button('Close', on_click=release_notes_dialog.close)

            with ui.row(align_items="center").classes("justify-center w-full"):
                ui.markdown(
                    f"""
                        > {application.description}
                    """
                )
                ui.space()
                with ui.column(align_items="left"):
                    for regulatory_class in application.regulatory_classes:
                        ui.label(f"Regulatory Class: {regulatory_class}")
                        if (regulatory_class == "RUO"):
                            with ui.row(align_items="center").classes("justify-center w-full"):
                                ui.image("assets/ruo.svg")
                    if not application.regulatory_classes:
                        ui.label(f"Regulatory Class: Missing")
                        with ui.row(align_items="center").classes("justify-center w-full"):
                            ui.icon("bug_report", color="red")
                    ui.label(f"Latest version: {latest_application_version_name}")
                    ui.button("Release Notes",icon="change_history",on_click=release_notes_dialog.open)

            async def _select_source() -> None:
                """Open a file picker dialog and show notifier when closed again."""
                from nicegui import ui  # noqa: PLC0415

                result = await GUILocalFilePicker(str(Path.home()), multiple=False)  # type: ignore
                if result and len(result) > 0:
                    path = Path(result[0])
                    if not path.is_dir():
                        submit_form.source = None
                        submit_form.wsi_step_label.set_text(
                            "Select a folder with whole slide images you want to analyze"
                        )
                        submit_form.wsi_next_button.disable()
                        ui.notify("The selected path is not a directory. Please select a valid directory.")
                    else:
                        submit_form.source = path
                        submit_form.wsi_step_label.set_text(f"Selected folder {submit_form.source} to analyze")
                        submit_form.wsi_next_button.enable()
                        ui.notify(f"You chose directory {submit_form.source}.")
                else:
                    submit_form.source = None
                    submit_form.wsi_step_label.set_text("Select a folder with whole slide images you want to analyze")
                    submit_form.wsi_next_button.disable()
                    ui.notify("You did not make a selection. You must choose a source directory to upload from.")

            def _on_wsi_next_click() -> None:
                """Handle the 'Next' button click in WSI step.

                This function:
                1. Generates metadata from the selected source directory
                2. Updates the metadata grid with the generated data
                3. Moves to the next step
                """
                if submit_form.source:
                    try:
                        ui.notify(f"Finding WSIs and generating metadata for {submit_form.source}...")
                        submit_form.metadata_grid.options["rowData"] = service.generate_metadata_from_source_directory(
                            submit_form.source
                        )
                        submit_form.metadata_grid.update()
                        ui.notify(f"Found {len(submit_form.metadata_grid.options['rowData'])} slides for analysis.")
                        stepper.next()
                    except Exception as e:
                        ui.notify(f"Error generating metadata: {e!s}", color="negative")
                        raise
                else:
                    ui.notify("No source directory selected", color="negative")


            with ui.stepper().props("vertical").classes("w-full") as stepper:
                with ui.step("Application Version"):
                    ui.label(f"Select the version of {application.name} you want to run.")
                    ui.select(
                        {
                            version.application_version_id: version.version
                            for version in application_versions
                        },
                        value=latest_application_version_id
                    ).bind_value(
                        submit_form, "application_version_id"
                    )
                    with ui.stepper_navigation():
                        ui.button("Next", on_click=stepper.next).mark("BUTTON_APPLICATION_VERSION_NEXT")

                with ui.step("Whole Slide Images"):
                    submit_form.wsi_step_label = ui.label(
                        "Select a folder with whole slide images you want to analyze."
                    )
                    with ui.stepper_navigation():
                        ui.button("Select", on_click=_select_source, icon="folder").mark("BUTTON_WSI_SELECT")
                        submit_form.wsi_next_button = ui.button("Next", on_click=_on_wsi_next_click)
                        submit_form.wsi_next_button.mark("BUTTON_WSI_NEXT").disable()
                        ui.button("Back", on_click=stepper.previous).props("flat")

                with ui.step("Metadata"):
                    ui.label("Check the metadata extracted from the images, and provide additional information.")

                    async def _validate() -> None:
                        rows = await submit_form.metadata_grid.get_client_data()
                        valid = True
                        for row in rows:
                            if (
                                row["tissue_type"]
                                not in [
                                    "adrenal gland",
                                    "bladder",
                                    "bone",
                                    "brain",
                                    "breast",
                                    "colon",
                                    "liver",
                                    "lung",
                                    "lymph node",
                                ]
                            ) or (row["disease"] not in ["lung", "liver", "breast", "bladder", "colorectal"]):
                                valid = False
                                break
                        if not valid:
                            submit_form.metadata_next_button.disable()
                        else:
                            ui.notify("Your metadata is now valid. Feel free to continue to the next step.")
                            submit_form.metadata_next_button.enable()

                    async def _metadata_next() -> None:
                        submit_form.metadata = await submit_form.metadata_grid.get_client_data()
                        _upload_ui.refresh(submit_form.metadata)
                        ui.notify("Prepared upload ui")
                        stepper.next()

                    submit_form.metadata_grid = (
                        ui.aggrid({
                            "autoSizeStrategy": {
                                "type": "fitCellContents",
                                "defaultMinWidth": 10,
                                "columnLimits": [{"colId": "source", "minWidth": 150}],
                            },
                            "columnDefs": [
                                {"headerName": "Reference", "field": "reference"},
                                {
                                    "headerName": "Tissue Type",
                                    "field": "tissue_type",
                                    "editable": True,
                                    "cellClassRules": {
                                        "bg-red-300": "!['adrenal gland', 'bladder', 'bone', 'brain', 'breast', 'colon', 'liver', 'lung', 'lymph node'].includes(x)",
                                        "bg-green-300": "['adrenal gland', 'bladder', 'bone', 'brain', 'breast', 'colon', 'liver', 'lung', 'lymph node'].includes(x)",
                                    },
                                },
                                {
                                    "headerName": "Disease",
                                    "field": "disease",
                                    "editable": True,
                                    "cellClassRules": {
                                        "bg-red-300": "!['lung', 'liver', 'breast', 'bladder', 'colorectal'].includes(x)",
                                        "bg-green-300": "['lung', 'liver', 'breast', 'bladder', 'colorectal'].includes(x)",
                                    },
                                },
                                {"headerName": "Source", "field": "source"},
                                {"headerName": "Checksum", "field": "checksum_crc32c"},
                                {"headerName": "MPP", "field": "mpp"},
                                {"headerName": "Width", "field": "width"},
                                {"headerName": "Height", "field": "height"},
                                {"headerName": "Staining", "field": "staining"},
                                {"headerName": "File size", "field": "file_size_human", "initialHide": True},
                                {"headerName": "Upload progress", "field": "file_upload_progress", "initialHide": True},
                                {"headerName": "Platform Bucket URL", "field": "platform_bucket_url", "initialHide": True},
                            ],
                            "rowData": [],
                            "rowSelection": "multiple",
                        })
                        .on("cellValueChanged", lambda _: _validate())
                        .classes("max-h-160")
                        .mark("GRID_METADATA")
                    )

                    with ui.stepper_navigation():
                        submit_form.metadata_next_button = ui.button("Next", on_click=lambda _: _metadata_next())
                        submit_form.metadata_next_button.mark("BUTTON_METADATA_NEXT").disable()
                        ui.button("Back", on_click=stepper.previous).props("flat")

                async def _upload() -> None:
                    """Upload prepared slides."""
                    ui.notify("Uploading slides to Aignostics Platform ...")
                    await run.cpu_bound(
                        Service.upload_with_queue,
                        str(time.time() * 1000),
                        submit_form.application_version_id,
                        submit_form.metadata,
                        upload_message_queue,
                    )
                    ui.notify("Upload to Aignostics Platform completed.")
                    submit_form.submission_submit_button.enable()

                @ui.refreshable
                def _upload_ui(metadata: list[dict[str, Any]]) -> None:
                    """Upload UI."""
                    with ui.column(align_items="left"):
                        ui.label(f"1. Upload {len(metadata)} slides you prepared to the Aignostics Platform.")
                        upload_complete = True
                        for row in metadata or []:
                            upload_complete = upload_complete and row["file_upload_progress"] == 1
                            with ui.row(align_items="center"):
                                with ui.circular_progress(value=row["file_upload_progress"], show_value=False):
                                    ui.button(icon="cloud_upload").props("flat round").disable()
                                ui.label(f"{row['source']} ({row['file_size_human']})")
                        if upload_complete:
                            ui.label(f"2. All uploads completed successfully. Click submit to run { submit_form.application_version_id } on {len(metadata) } slides.")

                def _update_upload_progress() -> None:
                    """Update the upload progress for each file."""
                    if not upload_message_queue.empty():
                        message = upload_message_queue.get()
                        if message and isinstance(message, dict) and "reference" in message:
                            for row in submit_form.metadata:
                                if row["reference"] == message["reference"]:
                                    if "file_upload_progress" in message:
                                        row["file_upload_progress"] = message["file_upload_progress"]
                                        break
                                    elif "platform_bucket_url" in message:
                                        row["platform_bucket_url"] = message["platform_bucket_url"]
                                        break
                        _upload_ui.refresh(submit_form.metadata)

                def _submit() -> None:
                    """Submit the application run."""
                    ui.notify("Application Run Submitted!")
                    run = service.application_run_submit_from_metadata(
                        submit_form.application_version_id,
                        submit_form.metadata,
                    )
                    ui.notify(f"Application run created with id '{run.application_run_id}'.")
                    ui.navigate.to(f"/application/run/{run.application_run_id}")

                with ui.step("Submission"):
                    _upload_ui([])
                    upload_message_queue = Manager().Queue()
                    ui.timer(0.1, callback=_update_upload_progress)

                    with ui.stepper_navigation():
                        ui.button(
                            "Upload",
                            on_click=lambda _: _upload(),
                            icon="check",
                        ).mark("BUTTON_SUBMISSION_UPLOAD")
                        submit_form.submission_submit_button = ui.button(
                            "Submit",
                            on_click=lambda _: _submit(),
                            icon="check",
                        )
                        submit_form.submission_submit_button.mark("BUTTON_SUBMISSION_SUBMIT").disable()
                        ui.button("Back", on_click=stepper.previous).props("flat")

        @ui.page("/application/run/{application_run_id}")
        def page_application_run_describe(application_run_id: str) -> None:
            """Describe Application."""
            service = Service()
            run, run_status = service.application_run(application_run_id)

            if run and run_status:
                _frame(
                    navigation_icon=_run_status_to_icon(run_status.status.value),
                    navigation_title=f"Run of {run_status.application_version_id} on {run_status.triggered_at.astimezone().strftime('%m-%d %H:%M')}",
                    left_sidebar=True,
                    args={"application_run_id": application_run_id},
                )
            else:
                _frame(
                    navigation_icon="bug_report",
                    navigation_title=f"Run {application_run_id}",
                    left_sidebar=True,
                    args={"application_run_id": application_run_id},
                )

            if run is None:
                ui.label(f"Failed to get run '{application_run_id}'").mark("LABEL_ERROR")
                return

            def _cancel(run_id: str) -> bool:
                """Cancel the application run.

                Args:
                    run_id (str): The ID of the run to cancel.

                Returns:
                    bool: True if the run was cancelled, False otherwise.
                """
                ui.notify(f"Canceling application run with id {run_id}...")
                try:
                    canceled = service.application_run_cancel(run_id)
                    if canceled:
                        ui.notify("Application Run Cancelled!")
                        return True
                    ui.notify("Application Run can not be cancelled!")
                    return False
                except Exception as e:
                    ui.notify(f"Failed to cancel application run: {e}.")
                    return False

            if run_status.status.value == "running":
                with ui.row().classes("w-full justify-end"):
                    ui.button(
                        "Cancel",
                        color="red",
                        on_click=lambda: _cancel(run.application_run_id),
                        icon="cancel",
                    ).mark("BUTTON_APPLICATION_RUN_CANCEL")

            ui.markdown(
                f"""
                Status: {run_status.status.value}
                Triggered at: {run_status.triggered_at.astimezone().strftime("%m-%d %H:%M")}
                """
            )

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
