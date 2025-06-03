"""Application describe page, including submission stepper."""

import sys
import time
from multiprocessing import Manager
from pathlib import Path
from typing import Any

from nicegui import app, binding, ui  # noq
from nicegui import run as nicegui_run

from aignostics.system import Service as SystemService
from aignostics.utils import GUILocalFilePicker, get_logger

from .._service import Service  # noqa: TID252
from .._utils import get_mime_type_for_artifact  # noqa: TID252
from ._frame import _frame
from ._utils import (
    application_id_to_icon,
    mime_type_to_icon,
)

logger = get_logger(__name__)

WIDTH_100 = "width: 100%"
WIDTH_1200px = "width: 1200px; max-width: none"
MESSAGE_METADATA_GRID_IS_NOT_INITIALIZED = "Metadata grid is not initialized."


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

upload_message_queue = Manager().Queue()


async def _page_application_describe(application_id: str) -> None:  # noqa: C901, PLR0912, PLR0915
    """Describe Application.

    Args:
        application_id (str): The application ID.
    """
    service = Service()
    application = service.application(application_id)

    if application is None:
        await _frame(
            navigation_title=f"{application_id}",
            navigation_icon="bug_report",
            navigation_icon_color="negative",
            navigation_icon_tooltip="Could not load application",
            left_sidebar=True,
            args={"application_id": application_id},
        )
        ui.label(f"Failed to get application '{application_id}'").mark("LABEL_ERROR")
        return

    await _frame(
        navigation_title=f"{application.name if application else ''}",
        navigation_icon=application_id_to_icon(application_id),
        navigation_icon_color="primary",
        navigation_icon_tooltip=application_id,
        left_sidebar=True,
        args={"application_id": application_id},
    )

    application_versions = service.application_versions(application)
    latest_application_version = application_versions[0]
    latest_application_version_id = latest_application_version.application_version_id
    submit_form.application_version_id = latest_application_version_id

    with ui.dialog() as release_notes_dialog, ui.card().style(WIDTH_1200px):
        ui.label(f"Release notes of {application.name}").classes("text-h5")
        with ui.scroll_area().classes("w-full h-100"):
            for application_version in application_versions:
                ui.label(f"Version {application_version.version}").classes("text-h6")
                ui.markdown(application_version.changelog)
        with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
            ui.button("Close", on_click=release_notes_dialog.close)

    with ui.row(align_items="start").classes("justify-center w-full"):
        with ui.column(), ui.expansion(application.name, icon="info").classes("full-width") as application_info:
            ui.markdown(application.description.replace("\n", "\n\n"))
        ui.space()
        with ui.row(align_items="center"):
            with ui.button("Release Notes", icon="change_history", on_click=release_notes_dialog.open):
                ui.tooltip("Show change notes of this application.")
            for regulatory_class in application.regulatory_classes:
                if regulatory_class in {"RUO", "RuO"}:
                    with ui.link(
                        target="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/distribution-in-vitro-diagnostic-products-labeled-research-use-only-or-investigational-use-only",
                        new_tab=True,
                    ):
                        ui.image("/application_assets/ruo.png").style("width: 70px; height: 36px")
                        ui.tooltip("Go to explanation of this regulatory class")

                elif regulatory_class == "demo":
                    with ui.icon("network_check", size="lg", color="orange"):
                        ui.tooltip("For testing only.")
                else:
                    ui.label(f"{regulatory_class}")
            if not application.regulatory_classes:
                with ui.link(
                    target="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/distribution-in-vitro-diagnostic-products-labeled-research-use-only-or-investigational-use-only",
                    new_tab=True,
                ):
                    ui.image("/application_assets/ruo.png").style("width: 70px; height: 36px")

    async def _select_source(data: bool = False) -> None:
        """Open a file picker dialog and show notifier when closed again."""
        from nicegui import ui  # noqa: PLC0415

        result = await GUILocalFilePicker(
            str(SystemService.get_user_data_directory("datasets") if data else Path.home()), multiple=False
        )  # type: ignore
        if result and len(result) > 0:
            path = Path(result[0])
            if not path.is_dir():
                submit_form.source = None
                submit_form.wsi_step_label.set_text(
                    "Select a folder with whole slide images you want to analyze"
                ) if submit_form.wsi_step_label else None
                submit_form.wsi_next_button.disable() if submit_form.wsi_next_button else None
                ui.notify("The selected path is not a directory. Please select a valid directory.", type="warning")
            else:
                submit_form.source = path
                submit_form.wsi_step_label.set_text(
                    f"Selected folder {submit_form.source} to analyze."
                ) if submit_form.wsi_step_label else None
                submit_form.wsi_next_button.enable() if submit_form.wsi_next_button else None
                ui.notify(
                    f"You chose directory {submit_form.source}. Feel free to continue to the next step.",
                    type="positive",
                )
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

    async def _pytest_home() -> None:  # noqa: RUF029
        """Select home folder."""
        from nicegui import ui  # noqa: PLC0415

        submit_form.source = Path.home()
        submit_form.wsi_step_label.set_text(
            f"Selected folder {submit_form.source} to analyze."
        ) if submit_form.wsi_step_label else None
        submit_form.wsi_next_button.enable() if submit_form.wsi_next_button else None
        ui.notify(
            f"You chose directory {submit_form.source}. Feel free to continue to the next step.",
            type="positive",
        )

    async def _on_wsi_next_click() -> None:
        """Handle the 'Next' button click in WSI step.

        This function:
        1. Generates metadata from the selected source directory
        2. Updates the metadata grid with the generated data
        3. Moves to the next step

        Raises:
            RuntimeError: If the metadata grid is not initialized or if the generated metadata is None.
        """
        if submit_form.source and submit_form.metadata_grid and submit_form.wsi_spinner and submit_form.wsi_next_button:
            try:
                ui.notify(f"Finding WSIs and generating metadata for {submit_form.source}...", type="info")
                if submit_form.metadata_grid is None:
                    logger.error(MESSAGE_METADATA_GRID_IS_NOT_INITIALIZED)  # type: ignore[unreachable]
                    return
                submit_form.wsi_spinner.set_visibility(True)
                submit_form.wsi_next_button.set_visibility(False)
                submit_form.metadata_grid.options["rowData"] = await nicegui_run.cpu_bound(
                    Service.generate_metadata_from_source_directory,
                    str(submit_form.application_version_id),
                    submit_form.source,
                    True,
                    [".*:staining_method=H&E"],
                )
                if submit_form.metadata_grid.options["rowData"] is None:
                    msg = "nicegui_run.cpu_bound(Service.generate_metadata_from_source_directory) returned None"
                    logger.error(msg)
                    raise RuntimeError(msg)  # noqa: TRY301
                submit_form.wsi_next_button.set_visibility(True)
                submit_form.wsi_spinner.set_visibility(False)
                submit_form.metadata_grid.update()
                ui.notify(
                    f"Found {len(submit_form.metadata_grid.options['rowData'])} slides for analysis."
                    "Please provide missing metadata.",
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
                    ui.markdown(application_version.changelog)
                    ui.label("Expected Input Artifacts:").classes("text-h5")
                    for artifact in application_version.input_artifacts:
                        with ui.expansion(
                            artifact.name, icon=mime_type_to_icon(get_mime_type_for_artifact(artifact))
                        ).classes("w-full"):
                            ui.label("Metadata")
                            ui.json_editor({
                                "content": {"json": artifact.metadata_schema},
                                "mode": "tree",
                                "readOnly": True,
                                "mainMenuBar": False,
                                "navigationBar": True,
                                "statusBar": False,
                            }).style(WIDTH_100)
                    ui.label("Generated output artifacts:").classes("text-h5")
                    for artifact in application_version.output_artifacts:
                        with ui.expansion(
                            artifact.name, icon=mime_type_to_icon(get_mime_type_for_artifact(artifact))
                        ).classes("w-full"):
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
                            }).style(WIDTH_100)
                    break
        with ui.row(align_items="end").classes("w-full"), ui.column(align_items="end").classes("w-full"):
            ui.button("Close", on_click=info_dialog.close)

    with ui.stepper().props("vertical").classes("w-full") as stepper:  # noqa: PLR1702
        with ui.step("Select Application Version"):
            with ui.row().classes("w-full justify-center"):
                with ui.column():
                    ui.label(
                        f"Select the version of {application.name} you want to run. Not sure? "
                        "Click “Next” to auto-select the latest version"
                    )
                    ui.select(
                        {version.application_version_id: version.version for version in application_versions},
                        value=latest_application_version_id,
                    ).bind_value(submit_form, "application_version_id")
                ui.space()
                with ui.column(), ui.button(icon="info", on_click=info_dialog.open):
                    ui.tooltip(
                        "Show technical information about expected input and output of this application version."
                    )
            with ui.stepper_navigation():
                ui.button("Next", on_click=lambda: (application_info.close(), stepper.next())).mark(  # type: ignore[func-returns-value]
                    "BUTTON_APPLICATION_VERSION_NEXT"
                )

        with ui.step("Select Whole Slide Images"):
            submit_form.wsi_step_label = ui.label(
                "Select the folder with the whole slide images you want to analyze then click Next."
            )
            with ui.stepper_navigation():
                if "pytest" in sys.modules:
                    ui.button("Home", on_click=_pytest_home, icon="folder").mark("BUTTON_PYTEST_HOME")
                with ui.button(
                    "Data", on_click=lambda _: _select_source(True), icon="folder_special", color="purple-400"
                ).mark("BUTTON_WSI_SELECT_DATA"):
                    ui.tooltip("Select folder within Launchpad datasets directory")
                with ui.button("Custom", on_click=_select_source, icon="folder").mark("BUTTON_WSI_SELECT_CUSTOM"):
                    ui.tooltip("Select custom folder starting at your home directory")
                submit_form.wsi_next_button = ui.button("Next", on_click=_on_wsi_next_click)
                submit_form.wsi_next_button.mark("BUTTON_WSI_NEXT").disable()
                submit_form.wsi_spinner = ui.spinner(size="lg")
                submit_form.wsi_spinner.set_visibility(False)
                ui.button("Back", on_click=stepper.previous).props("flat")

        with ui.step("Choose Images and Edit Metadata"):
            ui.markdown(
                """
                The Launchpad has found all compatible slide files in your selected folder.

                1. Check the slides that have been found.
                    If you wish to exclude any from analysis at this point, check the boxes next to those slides
                    and click “Exclude” to remove them.
                2. For the slides you wish to analyze,
                    provide the missing metadata to finalize the upload.
                    Double click red cells to edit the missing data with the available options.
                3. Once all the metadata has been added and your slide selection has been finalized,
                    click “Next”.

                You can revert to the previous step and reupload at any point by clicking “Back”.
                """
            )

            async def _pytest_meta() -> None:  # noqa: RUF029
                if submit_form.metadata_grid is None:
                    logger.error(MESSAGE_METADATA_GRID_IS_NOT_INITIALIZED)
                    return
                if submit_form.metadata_next_button is None:
                    logger.error("Metadata next button is not initialized.")
                    return
                submit_form.metadata_next_button.enable()
                ui.notify("Your metadata is now valid! Feel free to continue to the next step.", type="positive")

            async def _validate() -> None:
                if submit_form.metadata_grid is None:
                    logger.error(MESSAGE_METADATA_GRID_IS_NOT_INITIALIZED)
                    return
                rows = await submit_form.metadata_grid.get_client_data()
                valid = True
                for row in rows:
                    if (
                        row["tissue"]
                        not in {
                            "ADRENAL_GLAND",
                            "BLADDER",
                            "BONE",
                            "BRAIN",
                            "BREAST",
                            "COLON",
                            "LIVER",
                            "LUNG",
                            "LYMPH_NODE",
                        }
                    ) or (
                        row["disease"]
                        not in {
                            "BREAST_CANCER",
                            "BLADDER_CANCER",
                            "COLORECTAL_CANCER",
                            "LIVER_CANCER",
                            "LUNG_CANCER",
                        }
                    ):
                        valid = False
                        break
                if submit_form.metadata_next_button is None:
                    logger.error("Metadata next button is not initialized.")
                    return
                if not valid:
                    submit_form.metadata_next_button.disable()
                else:
                    submit_form.metadata_next_button.enable()
                    ui.notify("Your metadata is now valid. Feel free to continue to the next step.", type="positive")
                submit_form.metadata_grid.run_grid_method("autoSizeAllColumns")

            async def _metadata_next() -> None:
                if submit_form.metadata_grid is None or submit_form.submission_upload_button is None:
                    logger.error(MESSAGE_METADATA_GRID_IS_NOT_INITIALIZED)
                    return
                if "pytest" in sys.modules:
                    rows = submit_form.metadata_grid.options["rowData"]
                    for row in rows:
                        row["tissue"] = "LUNG"
                        row["disease"] = "LUNG_CANCER"
                    submit_form.metadata = rows
                else:
                    submit_form.metadata = await submit_form.metadata_grid.get_client_data()
                _upload_ui.refresh(submit_form.metadata)
                submit_form.submission_upload_button.enable()
                if "pytest" in sys.modules:
                    ui.notify("Prepared upload UI.", type="info")
                stepper.next()

            async def _delete_selected() -> None:
                if submit_form.metadata_grid is None or submit_form.metadata_exclude_button is None:
                    logger.error(MESSAGE_METADATA_GRID_IS_NOT_INITIALIZED)
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
                        {"headerName": "Reference", "field": "reference_short", "checkboxSelection": True},
                        {
                            "headerName": "Thumbnail",
                            "field": "thumbnail",
                            ":cellRenderer": thumbnail_renderer_js,
                            "autoHeight": True,
                        },
                        {
                            "headerName": "Tissue",
                            "field": "tissue",
                            "editable": True,
                            "cellEditor": "agSelectCellEditor",
                            "cellEditorParams": {
                                "values": [
                                    "ADRENAL_GLAND",
                                    "BLADDER",
                                    "BONE",
                                    "BRAIN",
                                    "BREAST",
                                    "COLON",
                                    "LIVER",
                                    "LUNG",
                                    "LYMPH_NODE",
                                ],
                                "valueListGap": 10,
                            },
                            "cellClassRules": {
                                "bg-red-300": "!new Set(['ADRENAL_GLAND', 'BLADDER', 'BONE', 'BRAIN',"
                                "'BREAST', 'COLON', 'LIVER', 'LUNG', 'LYMPH_NODE']).has(x)",
                                "bg-green-300": "new Set(['ADRENAL_GLAND', 'BLADDER', 'BONE', 'BRAIN',"
                                "'BREAST', 'COLON', 'LIVER', 'LUNG', 'LYMPH_NODE']).has(x)",
                            },
                        },
                        {
                            "headerName": "Disease",
                            "field": "disease",
                            "editable": True,
                            "cellEditor": "agSelectCellEditor",
                            "cellEditorParams": {
                                "values": [
                                    "BREAST_CANCER",
                                    "BLADDER_CANCER",
                                    "COLORECTAL_CANCER",
                                    "LIVER_CANCER",
                                    "LUNG_CANCER",
                                ],
                                "valueListGap": 10,
                            },
                            "cellClassRules": {
                                "bg-red-300": "!new Set(['BREAST_CANCER', 'BLADDER_CANCER', "
                                "'COLORECTAL_CANCER', 'LIVER_CANCER', 'LUNG_CANCER']).has(x)",
                                "bg-green-300": "new Set(['BREAST_CANCER', 'BLADDER_CANCER', "
                                "'COLORECTAL_CANCER', 'LIVER_CANCER', 'LUNG_CANCER']).has(x)",
                            },
                        },
                        {"headerName": "File size", "field": "file_size_human"},
                        {"headerName": "MPP", "field": "resolution_mpp"},
                        {"headerName": "Width", "field": "width_px"},
                        {"headerName": "Height", "field": "height_px"},
                        {"headerName": "Staining", "field": "staining_method"},
                        {"headerName": "Source", "field": "source"},
                        {"headerName": "Checksum", "field": "checksum_base64_crc32c"},
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
                    "enableCellTextSelection": "true",
                    "autoSizeStrategy": {
                        "type": "fitCellContents",
                        "defaultMinWidth": 10,
                        "columnLimits": [{"colId": "source", "minWidth": 150}],
                    },
                    "domLayout": "normal",
                })
                .style("height: 210px")
                .classes("ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham")
                .on("cellValueChanged", lambda _: _validate())
                .on("selectionChanged", _handle_grid_selection_changed)
                .mark("GRID_METADATA")
            )
            # use ui timer to update the grid class depending on dark mode, with a frequency of once per second
            ui.timer(
                interval=1,
                callback=lambda: submit_form.metadata_grid.classes(
                    add="ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham",
                    remove="ag-theme-balham" if app.storage.general.get("dark_mode", False) else "ag-theme-balham-dark",
                )
                if submit_form.metadata_grid
                else None,
            )
            with ui.stepper_navigation():
                if "pytest" in sys.modules:
                    ui.button("Select", on_click=_pytest_meta, icon="folder").mark("BUTTON_PYTEST_META")
                submit_form.metadata_next_button = ui.button("Next", on_click=_metadata_next)
                submit_form.metadata_next_button.mark("BUTTON_METADATA_NEXT").disable()
                with ui.button("Exclude selected", on_click=_delete_selected).mark(
                    "BUTTON_DELETE_SELECTED"
                ) as exclude_button:
                    ui.tooltip("Exclude selected slides from analysis")
                submit_form.metadata_exclude_button = exclude_button
                submit_form.metadata_exclude_button.set_text("Exclude")
                submit_form.metadata_exclude_button.disable()
                ui.button("Back", on_click=stepper.previous).props("flat")

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
            ui.notify(
                f"Application run submitted with id '{run.application_run_id}'. Navigating to application run ...",
                type="positive",
            )
            ui.navigate.to(f"/application/run/{run.application_run_id}")

        async def _upload() -> None:
            """Upload prepared slides."""
            global upload_message_queue  # noqa: PLW0602
            if submit_form.submission_submit_button is None or submit_form.submission_upload_button is None:
                logger.error("Submission submit button is not initialized.")
                return
            ui.notify("Uploading whole slide images to Aignostics Platform ...", type="info")

            await nicegui_run.cpu_bound(
                Service.application_run_upload,
                str(submit_form.application_version_id),
                submit_form.metadata or [],
                str(time.time() * 1000),
                upload_message_queue,
            )
            ui.notify("Upload to Aignostics Platform completed.", type="positive")
            submit_form.submission_submit_button.enable()
            submit_form.submission_upload_button.disable()
            _submit()

        @ui.refreshable
        def _upload_ui(metadata: list[dict[str, Any]]) -> None:
            """Upload UI."""
            with ui.column(align_items="start"):
                ui.label(f"Upload and submit your {len(metadata)} slide(s) for analysis.")
                upload_complete = True
                for row in metadata or []:
                    upload_complete = upload_complete and row["file_upload_progress"] == 1
                    with ui.row(align_items="center"):
                        with ui.circular_progress(value=row["file_upload_progress"], show_value=False):
                            ui.button(icon="cloud_upload").props("flat round").disable()
                        ui.label(f"{row['source']} ({row['file_size_human']})").classes("w-4/5")

        def _update_upload_progress() -> None:
            """Update the upload progress for each file."""
            global upload_message_queue  # noqa: PLW0602
            if submit_form.metadata is None:
                return
            while not upload_message_queue.empty():
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

        with ui.step("Slide Submission"):
            _upload_ui([])
            ui.timer(0.1, callback=_update_upload_progress)

            with ui.stepper_navigation():
                with ui.button(
                    "Upload and Submit",
                    on_click=_upload,
                    icon="check",
                ).mark("BUTTON_SUBMISSION_UPLOAD") as submission_upload_button:
                    ui.tooltip(
                        "Upload selected slides to Aignostics platform bucket, "
                        "and submit application run when uploaded."
                    )
                submit_form.submission_upload_button = submission_upload_button
                submit_form.submission_submit_button = ui.button(
                    "Submit",
                    on_click=_submit,
                    icon="check",
                )
                submit_form.submission_submit_button.set_visibility(False)
                submit_form.submission_submit_button.mark("BUTTON_SUBMISSION_SUBMIT").disable()
                ui.button("Back", on_click=stepper.previous).props("flat")
