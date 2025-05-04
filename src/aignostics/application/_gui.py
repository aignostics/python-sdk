"""Homepage (index) of GUI."""

import time
from importlib.util import find_spec
from multiprocessing import Manager
from pathlib import Path
from typing import Any
from urllib.parse import quote as urlencode

import pandas as pd
from nicegui import app

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
            wsi_spinner: ui.spinner | None = None
            metadata: list[dict[str, Any]] | None = None
            metadata_grid: ui.aggrid | None = None
            metadata_exclude_button: ui.button | None = None
            metadata_next_button: ui.button | None = None
            submission_upload_button: ui.button | None = None
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
                case "canceled_user":
                    return "cancel"
                case "canceled_system":
                    return "sync_problem"
                case "completed":
                    return "done_all"
                case _:
                    return "bug_report"

        def _run_item_status_to_icon(run_status: str) -> str:  # noqa: PLR0911
            """Convert run item status to icon.

            Args:
                run_status (str): The run item status.

            Returns:
                str: The icon name.
            """
            match run_status:
                case "pending":
                    return "pending"
                case "canceled_user":
                    return "cancel"
                case "canceled_system":
                    return "sync_problem"
                case "error_user":
                    return "report"
                case "error_system":
                    return "error"
                case "succeeded":
                    return "check"
                case _:
                    return "bug_report"

        def _mime_type_to_icon(mime_type: str) -> str:
            """Convert mime type to icon.

            Args:
                mime_type (str): The mime type.

            Returns:
                str: The icon name.
            """
            match mime_type:
                case "image/tiff":
                    return "image"
                case "application/dicom":
                    return "image"
                case "text/csv":
                    return "table_rows"
                case "application/geo+json":
                    return "place"
                case "application/json":
                    return "data_object"
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
                try:
                    with ui.list().props("bordered separator").classes("full-width"):
                        ui.item_label("Applications").props("header")
                        ui.separator()
                        for application in service.applications():
                            with ui.item(
                                on_click=lambda app_id=application.application_id: ui.navigate.to(
                                    f"/application/{app_id}"
                                )
                            ).props("clickable"):
                                with ui.item_section().props("avatar"):
                                    ui.icon(_application_id_to_icon(application.application_id))
                                with ui.item_section():
                                    ui.label(f"{application.name}").mark("LABEL_APPLICATION").tailwind.font_weight(
                                        "bold"
                                        if context.client.page.path == "/application/{application_id}"
                                        and args.get("application_id") == application.application_id
                                        else "normal"
                                    )
                except Exception:  # noqa: BLE001
                    ui.label("Failed to list applications.").mark("LABEL_ERROR")

                try:
                    with ui.list().props("bordered separator").classes("full-width"):
                        ui.item_label("Runs").props("header")
                        ui.separator()
                        for run, run_status in service.application_runs_with_status():
                            with ui.item(
                                on_click=lambda _: ui.navigate.to(f"/application/run/{run.application_run_id}")
                            ).props("clickable"):
                                with ui.item_section().props("avatar"):
                                    ui.icon(_run_status_to_icon(run_status.status.value))
                                with ui.item_section():
                                    ui.label(
                                        f"{run_status.application_version_id}",
                                    ).tailwind.font_weight(
                                        "bold"
                                        if context.client.page.path == "/application/run/{application_run_id}"
                                        and args.get("application_run_id") == run.application_run_id
                                        else "normal"
                                    )
                                    ui.label(
                                        f"triggered on {run_status.triggered_at.astimezone().strftime('%m-%d %H:%M')}"
                                    )
                except Exception:  # noqa: BLE001
                    ui.label("Failed to list application runs.").mark("LABEL_ERROR")

        @ui.page("/")
        def page_index() -> None:
            """Homepage of Applications."""
            _frame("Run our AI Applications on your Whole Slide Images", left_sidebar=True)

            ui.markdown(
                """
                    ## Welcome to the Aignostics Platform Launcher!
                    1. Select an application from the left sidebar and use our wizard to submit a run on your whole slide
                    images.
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

            with (
                ui.row(align_items="center").classes("justify-center w-full"),
                ui.carousel(animated=True, arrows=True, navigation=True).props("height=312px"),
            ):
                with ui.carousel_slide().classes("p-0"):
                    ui.image("/assets/home-card-1.png").classes("w-[768px]")
                with ui.carousel_slide().classes("p-0"):
                    ui.image("/assets/home-card-2.png").classes("w-[768px]")

        @ui.page("/application/{application_id}")
        def page_application_describe(application_id: str) -> None:  # noqa: C901, PLR0915
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
            submit_form.application_version_id = latest_application_version_id

            with ui.dialog() as release_notes_dialog, ui.card().style("width: 1200px; max-width: none"):
                ui.label(f"Release notes of {application.name}").classes("text-h5")
                with ui.scroll_area().classes("w-full h-100"):
                    for application_version in application_versions:
                        ui.label(f"Version {application_version.version}").classes("text-h6")
                        ui.markdown(
                            f"""
                                > {application_version.changelog}
                            """
                        )
                with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
                    ui.button("Close", on_click=release_notes_dialog.close)

            with ui.row(align_items="start").classes("justify-center w-full"):
                with ui.column(), ui.expansion(application.name, icon="info").classes("full-width") as application_info:
                    ui.markdown(
                        f"""
                                > {application.description}
                            """
                    )
                ui.space()
                with ui.row(align_items="center"):
                    ui.button("Release Notes", icon="change_history", on_click=release_notes_dialog.open)
                    for regulatory_class in application.regulatory_classes:
                        if regulatory_class == "RUO":
                            with ui.link(
                                target="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/distribution-in-vitro-diagnostic-products-labeled-research-use-only-or-investigational-use-only",
                                new_tab=True,
                            ):
                                ui.image("/assets/ruo.png").style("width: 45px; height: 36px")
                        else:
                            ui.label(f"{regulatory_class}")
                    if not application.regulatory_classes:
                        with ui.link(
                            target="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/distribution-in-vitro-diagnostic-products-labeled-research-use-only-or-investigational-use-only",
                            new_tab=True,
                        ):
                            ui.image("/assets/ruo.png").style("width: 45px; height: 36px")

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
                        ) if submit_form.wsi_step_label else None
                        submit_form.wsi_next_button.disable() if submit_form.wsi_next_button else None
                        ui.notify(
                            "The selected path is not a directory. Please select a valid directory.", type="warning"
                        )
                    else:
                        submit_form.source = path
                        submit_form.wsi_step_label.set_text(
                            f"Selected folder {submit_form.source} to analyze"
                        ) if submit_form.wsi_step_label else None
                        submit_form.wsi_next_button.enable() if submit_form.wsi_next_button else None
                        ui.notify(f"You chose directory {submit_form.source}.", type="info")
                else:
                    submit_form.source = None
                    submit_form.wsi_step_label.set_text(
                        "Select a folder with whole slide images you want to analyze"
                    ) if submit_form.wsi_step_label else None
                    submit_form.wsi_next_button.disable() if submit_form.wsi_next_button else None
                    ui.notify(
                        "You did not make a selection. You must choose a source directory to upload from.",
                        type="warning",
                    )

            async def _on_wsi_next_click() -> None:
                """Handle the 'Next' button click in WSI step.

                This function:
                1. Generates metadata from the selected source directory
                2. Updates the metadata grid with the generated data
                3. Moves to the next step
                """
                if (
                    submit_form.source
                    and submit_form.metadata_grid
                    and submit_form.wsi_spinner
                    and submit_form.wsi_next_button
                ):
                    try:
                        ui.notify(f"Finding WSIs and generating metadata for {submit_form.source}...", type="info")
                        if submit_form.metadata_grid is None:
                            logger.error("Metadata grid is not initialized.")
                            return
                        submit_form.wsi_spinner.set_visibility(True)
                        submit_form.wsi_next_button.set_visibility(False)
                        submit_form.metadata_grid.options["rowData"] = await run.cpu_bound(
                            Service.generate_metadata_from_source_directory,
                            submit_form.source,
                        )
                        submit_form.wsi_next_button.set_visibility(True)
                        submit_form.wsi_spinner.set_visibility(False)
                        submit_form.metadata_grid.update()
                        ui.notify(
                            f"Found {len(submit_form.metadata_grid.options['rowData'])} slides for analysis.",
                            type="positive",
                        )
                        stepper.next()
                    except Exception as e:
                        ui.notify(f"Error generating metadata: {e!s}", type="warning")
                        raise
                else:
                    ui.notify("No source directory selected", type="warning")

            with ui.dialog() as info_dialog, ui.card().style("width: 1200px; max-width: none; height: 1000px"):  # noqa: PLR1702
                if submit_form.application_version_id is None:
                    return
                with ui.scroll_area().classes("w-full h-[calc(100vh-2rem)]"):
                    for application_version in application_versions:
                        if application_version.application_version_id == submit_form.application_version_id:
                            ui.label(f"Latest changes in v{application_version.version}").classes("text-h5")
                            ui.markdown(
                                f"""
                                > {application_version.changelog}
                                """
                            )
                            ui.label("Expected Input Artifacts:").classes("text-h5")
                            for artifact in application_version.input_artifacts:
                                with ui.expansion(artifact.name, icon=_mime_type_to_icon(artifact.mime_type)).classes(
                                    "w-full"
                                ):
                                    ui.label("Metadata")
                                    ui.json_editor({
                                        "content": {"json": artifact.metadata_schema},
                                        "mode": "tree",
                                        "readOnly": True,
                                        "mainMenuBar": False,
                                        "navigationBar": True,
                                        "statusBar": False,
                                    }).style("width: 100%")
                            ui.label("Generated output artifacts:").classes("text-h5")
                            for artifact in application_version.output_artifacts:
                                with ui.expansion(artifact.name, icon=_mime_type_to_icon(artifact.mime_type)).classes(
                                    "w-full"
                                ):
                                    ui.label(f"Scope: {artifact.scope}")
                                    ui.label(f"Mime Type: {artifact.mime_type}")
                                    ui.label("Metadata")
                                    ui.json_editor({
                                        "content": {"json": artifact.metadata_schema},
                                        "mode": "tree",
                                        "readOnly": True,
                                        "mainMenuBar": False,
                                        "navigationBar": True,
                                        "statusBar": False,
                                    }).style("width: 100%")
                            break
                with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
                    ui.button("Close", on_click=info_dialog.close)

            with ui.stepper().props("vertical").classes("w-full") as stepper:  # noqa: PLR1702
                with ui.step("Application Version"):
                    with ui.row().classes("w-full justify-center"):
                        with ui.column():
                            ui.label(f"Select the version of {application.name} you want to run.")
                            ui.select(
                                {version.application_version_id: version.version for version in application_versions},
                                value=latest_application_version_id,
                            ).bind_value(submit_form, "application_version_id")
                        ui.space()
                        with ui.column():
                            ui.button(icon="info", on_click=info_dialog.open)
                    with ui.stepper_navigation():
                        ui.button("Next", on_click=lambda: [application_info.close(), stepper.next()]).mark(
                            "BUTTON_APPLICATION_VERSION_NEXT"
                        )

                with ui.step("Whole Slide Images"):
                    submit_form.wsi_step_label = ui.label(
                        "Select a folder with whole slide images you want to analyze."
                    )
                    with ui.stepper_navigation():
                        ui.button("Select", on_click=_select_source, icon="folder").mark("BUTTON_WSI_SELECT")
                        submit_form.wsi_next_button = ui.button("Next", on_click=_on_wsi_next_click)
                        submit_form.wsi_next_button.mark("BUTTON_WSI_NEXT").disable()
                        submit_form.wsi_spinner = ui.spinner(size="lg")
                        submit_form.wsi_spinner.set_visibility(False)
                        ui.button("Back", on_click=stepper.previous).props("flat")

                with ui.step("Metadata"):
                    ui.markdown(
                        """
                        1. Check extracted and provide missing metadata.
                            Double click red cells to edit - you are done when all turned green.
                        2. You can exclude slides from the analysis by selecting them and clicking "Exclude slides".
                        3. You can revert to the original list by clicking the Back button.
                        """
                    )

                    async def _validate() -> None:
                        if submit_form.metadata_grid is None:
                            logger.error("Metadata grid is not initialized.")
                            return
                        rows = await submit_form.metadata_grid.get_client_data()
                        valid = True
                        for row in rows:
                            if (
                                row["tissue_type"]
                                not in {
                                    "adrenal gland",
                                    "bladder",
                                    "bone",
                                    "brain",
                                    "breast",
                                    "colon",
                                    "liver",
                                    "lung",
                                    "lymph node",
                                }
                            ) or (row["disease"] not in {"lung", "liver", "breast", "bladder", "colorectal"}):
                                valid = False
                                break
                        if submit_form.metadata_next_button is None:
                            logger.error("Metadata next button is not initialized.")
                            return
                        if not valid:
                            submit_form.metadata_next_button.disable()
                        else:
                            ui.notify(
                                "Your metadata is now valid. Feel free to continue to the next step.", type="positive"
                            )
                            submit_form.metadata_next_button.enable()
                        submit_form.metadata_grid.run_grid_method("autoSizeAllColumns")

                    async def _metadata_next() -> None:
                        if submit_form.metadata_grid is None or submit_form.submission_upload_button is None:
                            logger.error("Metadata grid is not initialized.")
                            return
                        submit_form.metadata = await submit_form.metadata_grid.get_client_data()
                        _upload_ui.refresh(submit_form.metadata)
                        submit_form.submission_upload_button.enable()
                        ui.notify("Prepared upload ui", type="info")
                        stepper.next()

                    async def _delete_selected() -> None:
                        if submit_form.metadata_grid is None or submit_form.metadata_exclude_button is None:
                            logger.error("Metadata grid is not initialized.")
                            return
                        selected_rows = await submit_form.metadata_grid.get_selected_rows()
                        if (selected_rows is None) or (len(selected_rows) == 0):
                            return
                        submit_form.metadata = await submit_form.metadata_grid.get_client_data()
                        submit_form.metadata[:] = [row for row in submit_form.metadata if row not in selected_rows]
                        submit_form.metadata_grid.options["rowData"] = submit_form.metadata
                        submit_form.metadata_grid.update()
                        submit_form.metadata_exclude_button.set_text("Exclude")
                        submit_form.metadata_exclude_button.disable()

                    async def _handle_grid_selection_changed() -> None:
                        if submit_form.metadata_grid is None or submit_form.metadata_exclude_button is None:
                            logger.error("Metadata grid or button is not initialized.")
                            return
                        rows = await submit_form.metadata_grid.get_selected_rows()
                        if rows:
                            submit_form.metadata_exclude_button.set_text(f"Exclude {len(rows)} slides")
                            submit_form.metadata_exclude_button.enable()
                        else:
                            submit_form.metadata_exclude_button.set_text("Exclude")
                            submit_form.metadata_exclude_button.disable()

                    thumbnail_renderer_js = """
                        class ThumbnailRenderer {
                            init(params) {
                                this.eGui = document.createElement('img');
                                this.eGui.setAttribute('src', `/thumbnail?source=${encodeURIComponent(params.data.source)}`);
                                this.eGui.setAttribute('style', 'height:70px; width: 70px');
                                this.eGui.setAttribute('alt', `${params.data.reference}`);
                            }
                            getGui() {
                                return this.eGui;
                            }
                        }
                    """

                    submit_form.metadata_grid = (
                        ui.aggrid({
                            "columnDefs": [
                                {"headerName": "Reference", "field": "reference", "checkboxSelection": True},
                                {
                                    "headerName": "Thumbnail",
                                    "field": "thumbnail",
                                    ":cellRenderer": thumbnail_renderer_js,
                                    "autoHeight": True,
                                },
                                {
                                    "headerName": "Tissue Type",
                                    "field": "tissue_type",
                                    "editable": True,
                                    "cellEditor": "agSelectCellEditor",
                                    "cellEditorParams": {
                                        "values": [
                                            "adrenal gland",
                                            "bladder",
                                            "bone",
                                            "brain",
                                            "breast",
                                            "colon",
                                            "liver",
                                            "lung",
                                            "lymph node",
                                        ],
                                        "valueListGap": 10,
                                    },
                                    "cellClassRules": {
                                        "bg-red-300": "!new Set(['adrenal gland', 'bladder', 'bone', 'brain',"
                                        "'breast', 'colon', 'liver', 'lung', 'lymph node']).has(x)",
                                        "bg-green-300": "new Set(['adrenal gland', 'bladder', 'bone', 'brain',"
                                        "'breast', 'colon', 'liver', 'lung', 'lymph node']).has(x)",
                                    },
                                },
                                {
                                    "headerName": "Disease",
                                    "field": "disease",
                                    "editable": True,
                                    "cellEditor": "agSelectCellEditor",
                                    "cellEditorParams": {
                                        "values": ["lung", "liver", "breast", "bladder", "colorectal"],
                                        "valueListGap": 10,
                                    },
                                    "cellClassRules": {
                                        "bg-red-300": "!new Set(['lung', 'liver', 'breast', 'bladder',"
                                        " 'colorectal']).has(x)",
                                        "bg-green-300": "new Set(['lung', 'liver', 'breast', 'bladder',"
                                        " 'colorectal']).has(x)",
                                    },
                                },
                                {"headerName": "File size", "field": "file_size_human"},
                                {"headerName": "MPP", "field": "mpp"},
                                {"headerName": "Width", "field": "width"},
                                {"headerName": "Height", "field": "height"},
                                {"headerName": "Staining", "field": "staining"},
                                {"headerName": "Source", "field": "source"},
                                {"headerName": "Checksum", "field": "checksum_crc32c"},
                                {"headerName": "Upload progress", "field": "file_upload_progress", "initialHide": True},
                                {
                                    "headerName": "Platform Bucket URL",
                                    "field": "platform_bucket_url",
                                    "initialHide": True,
                                },
                            ],
                            "rowData": [],
                            "rowSelection": "multiple",
                            "stopEditingWhenCellsLoseFocus": True,
                            "autoSizeStrategy": {
                                "type": "fitCellContents",
                                "defaultMinWidth": 10,
                                "columnLimits": [{"colId": "source", "minWidth": 150}],
                            },
                            "domLayout": "normal",
                        })
                        .style("height: 210px")
                        .classes(
                            "ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham"
                        )
                        .on("cellValueChanged", lambda _: _validate())
                        .on("selectionChanged", _handle_grid_selection_changed)
                        .mark("GRID_METADATA")
                    )
                    # .style("height: auto; width: 1000px")
                    # use ui timer to update the grid class depending on dark mode, with a frequency of once per second
                    ui.timer(
                        interval=1,
                        callback=lambda: submit_form.metadata_grid.classes(
                            add="ag-theme-balham-dark"
                            if app.storage.general.get("dark_mode", False)
                            else "ag-theme-balham",
                            remove="ag-theme-balham"
                            if app.storage.general.get("dark_mode", False)
                            else "ag-theme-balham-dark",
                        )
                        if submit_form.metadata_grid
                        else None,
                    )
                    with ui.stepper_navigation():
                        submit_form.metadata_exclude_button = ui.button(
                            "Exclude selected", on_click=_delete_selected
                        ).mark("BUTTON_DELETE_SELECTED")
                        submit_form.metadata_exclude_button.set_text("Exclude")
                        submit_form.metadata_exclude_button.disable()
                        submit_form.metadata_next_button = ui.button("Next", on_click=lambda _: _metadata_next())
                        submit_form.metadata_next_button.mark("BUTTON_METADATA_NEXT").disable()
                        ui.button("Back", on_click=stepper.previous).props("flat")

                async def _upload() -> None:
                    """Upload prepared slides."""
                    if submit_form.submission_submit_button is None or submit_form.submission_upload_button is None:
                        logger.error("Submission submit button is not initialized.")
                        return
                    ui.notify("Uploading slides to Aignostics Platform ...", type="info")
                    if upload_message_queue is None:
                        logger.error("Upload message queue is not initialized.")
                        return
                    await run.cpu_bound(
                        Service.upload_with_queue,
                        str(time.time() * 1000),
                        str(submit_form.application_version_id),
                        submit_form.metadata or [],
                        upload_message_queue,
                    )
                    ui.notify("Upload to Aignostics Platform completed.", type="positive")
                    submit_form.submission_submit_button.enable()
                    submit_form.submission_upload_button.disable()

                @ui.refreshable
                def _upload_ui(metadata: list[dict[str, Any]]) -> None:
                    """Upload UI."""
                    with ui.column(align_items="start"):
                        ui.label(f"1. Upload {len(metadata)} slides you prepared to the Aignostics Platform.")
                        upload_complete = True
                        for row in metadata or []:
                            upload_complete = upload_complete and row["file_upload_progress"] == 1
                            with ui.row(align_items="center"):
                                with ui.circular_progress(value=row["file_upload_progress"], show_value=False):
                                    ui.button(icon="cloud_upload").props("flat round").disable()
                                ui.label(f"{row['source']} ({row['file_size_human']})").classes("w-4/5")
                        if upload_complete:
                            ui.label(
                                f"2. All uploads completed successfully. Click submit to run {submit_form.application_version_id} on {len(metadata)} slides."
                            )

                def _update_upload_progress() -> None:
                    """Update the upload progress for each file."""
                    if submit_form.metadata is None:
                        return
                    if not upload_message_queue.empty():
                        message = upload_message_queue.get()
                        if message and isinstance(message, dict) and "reference" in message:
                            for row in submit_form.metadata:
                                if row["reference"] == message["reference"]:
                                    if "file_upload_progress" in message:
                                        row["file_upload_progress"] = message["file_upload_progress"]
                                        break
                                    if "platform_bucket_url" in message:
                                        row["platform_bucket_url"] = message["platform_bucket_url"]
                                        break
                        _upload_ui.refresh(submit_form.metadata)

                def _submit() -> None:
                    """Submit the application run."""
                    ui.notify("Submitting application run ...", type="info")
                    try:
                        run = service.application_run_submit_from_metadata(
                            str(submit_form.application_version_id),
                            submit_form.metadata or [],
                        )
                    except Exception as e:  # noqa: BLE001
                        ui.notify(f"Failed to submit application run: {e}.", type="warning")
                        return
                    ui.notify(f"Application run submitted with id '{run.application_run_id}'.", type="positive")
                    ui.navigate.to(f"/application/run/{run.application_run_id}")

                with ui.step("Submission"):
                    _upload_ui([])
                    upload_message_queue = Manager().Queue()
                    ui.timer(0.1, callback=_update_upload_progress)

                    with ui.stepper_navigation():
                        submit_form.submission_upload_button = ui.button(
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
        def page_application_run_describe(application_run_id: str) -> None:  # noqa: C901, PLR0912, PLR0915
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
                ui.notify(f"Canceling application run with id {run_id}...", type="info")
                try:
                    canceled = service.application_run_cancel(run_id)
                    if canceled:
                        ui.notify("Application run cancelled!", type="positive")
                        return True
                    ui.notify("Application run can not be cancelled!", type="negative")
                    return False
                except Exception as e:  # noqa: BLE001
                    ui.notify(f"Failed to cancel application run: {e}.", type="warning")
                    return False

            with ui.dialog() as download_run_dialog, ui.card().style("width: 1200px; max-width: none"):
                ui.button("Select download folder")
                with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
                    ui.button("Close", on_click=download_run_dialog.close)

            with ui.dialog() as qupath_project_create_dialog, ui.card().style("width: 1200px; max-width: none"):
                ui.button("Select QuPath folder")
                with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
                    ui.button("Close", on_click=download_run_dialog.close)

            @ui.refreshable
            def csv_view_dialog_content(title: str | None, url: str | None) -> None:
                if title:
                    ui.label(title).classes("text-h5")
                if url:
                    try:
                        csv_df = pd.read_csv(url, comment="#")
                    except Exception as e:
                        ui.notify(f"Failed to load CSV: {e!s}", type="negative")
                        csv_df = pd.DataFrame()  # Empty dataframe as fallback
                    ui.aggrid.from_pandas(csv_df)

            with ui.dialog() as csv_view_dialog, ui.card().style("width: 1200px; max-width: none"):
                csv_view_dialog_content(title=None, url=None)
                with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
                    ui.button("Close", on_click=csv_view_dialog.close)

            def csv_dialog_open(title: str, url: str) -> None:
                """Open the CSV dialog."""
                csv_view_dialog_content.refresh(title=title, url=url)
                csv_view_dialog.open()

            @ui.refreshable
            def tiff_view_dialog_content(title: str | None, url: str | None) -> None:
                if title:
                    ui.label(title).classes("text-h5")
                if url:
                    try:
                        with ui.scroll_area().classes("w-full h-[calc(100vh-2rem)]"):
                            ui.image("/tiff?url=" + urlencode(url))
                    except Exception as e:
                        ui.notify(f"Failed to load CSV: {e!s}", type="negative")

            with ui.dialog() as tiff_view_dialog, ui.card().style("width: 1200px; max-width: none"):
                tiff_view_dialog_content(title=None, url=None)
                with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
                    ui.button("Close", on_click=tiff_view_dialog.close)

            def tiff_dialog_open(title: str, url: str) -> None:
                """Open the TIFF dialog."""
                tiff_view_dialog_content.refresh(title=title, url=url)
                tiff_view_dialog.open()

            if run_status.status.value == "running":
                with ui.row().classes("w-full justify-end"):
                    ui.button(
                        "Cancel",
                        color="red",
                        on_click=lambda: _cancel(run.application_run_id),
                        icon="cancel",
                    ).mark("BUTTON_APPLICATION_RUN_CANCEL")

            if run_status.status.value == "completed":
                with ui.row().classes("w-full justify-end"):
                    if find_spec("paquo"):
                        ui.button(
                            "Open in QuPath Microscopy Viewer",
                            icon="zoom_in",
                            on_click=qupath_project_create_dialog.open,
                        )
                    if find_spec("marimo"):
                        ui.button(
                            "Open in Marimo Notebook",
                            icon="analytics",
                            on_click=lambda: ui.navigate.to(f"/marimo/{run.application_run_id}"),
                        )
                    ui.button("Download Results", icon="cloud_download", on_click=download_run_dialog.open)

            with ui.card():
                ui.markdown(
                    f"""
                    * Application Version: {run_status.application_version_id}
                    * Status: {run_status.status.value}
                    * Triggered at: {run_status.triggered_at.astimezone().strftime("%m-%d %H:%M")}
                    * Organization: {run_status.organization_id}
                    * Triggered by: {run_status.triggered_by}
                    """
                )

            with ui.list().props("bordered separator").classes("full-width"):  # noqa: PLR1702
                for item in run.results():
                    with ui.item().props("clickable"):
                        with ui.item_section().props("avatar"):
                            ui.icon(_run_item_status_to_icon(item.status.value))
                        with ui.item_section().classes("w-1/5"):
                            with ui.card():
                                ui.label(f"Item ID: {item.item_id}")
                                ui.label(f"Reference: {item.reference}")
                                ui.label(f"Status: {item.status.value}")
                                if item.error:
                                    ui.label(f"Error: {item.error!s}")
                            if item.output_artifacts:
                                with ui.expansion("Analysis", icon="description").classes("w-full"):
                                    for artifact in item.output_artifacts:
                                        with ui.expansion(
                                            str(artifact.name), icon=_mime_type_to_icon(artifact.mime_type)
                                        ).classes("w-full"):
                                            if artifact.download_url:
                                                url = artifact.download_url
                                                title = artifact.name
                                                with ui.row():
                                                    if artifact.mime_type == "image/tiff":
                                                        ui.button(
                                                            "Preview",
                                                            icon=_mime_type_to_icon(artifact.mime_type),
                                                            on_click=lambda _, url=url: tiff_dialog_open(title, url),
                                                        )
                                                    if artifact.mime_type == "text/csv":
                                                        ui.button(
                                                            "Preview",
                                                            icon=_mime_type_to_icon(artifact.mime_type),
                                                            on_click=lambda _, url=url: csv_dialog_open(title, url),
                                                        )

                                                    with ui.link(target=artifact.download_url, new_tab=True):
                                                        ui.button(text="Download", icon="cloud_download")
                                            if artifact.metadata:
                                                with ui.expansion("Schema", icon="schema").classes("w-full"):
                                                    ui.json_editor({
                                                        "content": {"json": artifact.metadata},
                                                        "mode": "tree",
                                                        "readOnly": True,
                                                        "mainMenuBar": False,
                                                        "navigationBar": True,
                                                        "statusBar": False,
                                                    }).style("width: 100%")
                                            ui.label(f"ID: {artifact.output_artifact_id!s}")
