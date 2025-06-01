"""GUI of bucket module."""

from pathlib import Path

from aignostics.gui import frame

from ..utils import BasePageBuilder  # noqa: TID252
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app, binding, ui  # noqa: PLC0415

        app.add_static_files("/bucket_assets", Path(__file__).parent / "assets")

        @binding.bindable_dataclass
        class BucketForm:
            """Bucket form."""

            grid: ui.aggrid | None = None
            delete_button: ui.button | None = None

        bucket_form = BucketForm()

        @ui.page("/bucket")
        async def page_index() -> None:  # noqa: RUF029
            """Index page of bucket module."""
            with frame("Manage Cloud Bucket on Aignostics Platform", left_sidebar=False):
                # Nothing to do here, just to show the page
                pass

            with ui.row(align_items="start").classes("w-full"):
                ui.markdown("""
                        ## Managing your cloud bucket
                        1. For analysis whole slide images are
                            temporarily stored in a cloud bucket of the Aignostics Platform.
                        3. The bucket is private and only accessible to you and restricted staff of Aignostics.
                        2. The bucket is securely hosted on Google Cloud in EU.
                        3. All data is encrypted in transit and at rest.
                        4. Any data is automatically deleted after 7 days.
                        5. You can manually delete data at any time using the form below.
                        """).classes("w-3/5")
                ui.space()
                ui.image("/bucket_assets/Google-Cloud-logo.png").classes("w-1/5").style("margin-top:1.25rem")

            def _get_rows() -> list[dict[str, str]]:
                objs = Service().find(detail=True)
                return [
                    {
                        "key": obj["key"],  # type: ignore
                        "last_modified": obj["last_modified"].astimezone().strftime("%x %X %Z"),  # type: ignore
                        "size": f"{obj['size'] / (1024 * 1024 * 1024):.2f} GB",  # type: ignore
                    }
                    for obj in objs
                ]

            async def _delete_selected() -> None:
                """Delete selected objects."""
                if bucket_form.grid is None or bucket_form.delete_button is None:
                    return
                selected_rows = await bucket_form.grid.get_selected_rows()
                if not selected_rows or selected_rows == []:
                    ui.notify("No objects selected.", type="warning")
                    return
                ui.notify(f"Deleting {len(selected_rows)} objects ...", type="info")
                try:
                    Service().delete_objects(
                        [row["key"] for row in selected_rows],
                    )
                except Exception as e:  # noqa: BLE001
                    ui.notify(f"Error deleting objects: {e}", color="red", type="warning")
                    return
                ui.notify(f"Deleted {len(selected_rows)} objects.", type="positive")
                bucket_form.delete_button.set_text("Delete")
                bucket_form.delete_button.disable()
                bucket_form.grid.options["rowData"] = _get_rows()
                bucket_form.grid.update()

            async def _handle_grid_selection_changed() -> None:
                if bucket_form.grid is None or bucket_form.delete_button is None:
                    return
                rows = await bucket_form.grid.get_selected_rows()
                if rows:
                    bucket_form.delete_button.set_text(f"Delete {len(rows)} objects")
                    bucket_form.delete_button.enable()
                else:
                    bucket_form.delete_button.set_text("Delete")
                    bucket_form.delete_button.disable()

            bucket_form.grid = (
                ui.aggrid({
                    "columnDefs": [
                        {
                            "object": "Key",
                            "field": "key",
                            "checkboxSelection": True,
                            "filter": "agTextColumnFilter",
                        },
                        {
                            "headerName": "Last modified",
                            "field": "last_modified",
                            "filter": "agTextColumnFilter",
                        },
                        {
                            "headerName": "Size",
                            "field": "size",
                        },
                    ],
                    "rowData": _get_rows(),
                    "rowSelection": "multiple",
                    "enableCellTextSelection": "true",
                    "autoSizeStrategy": {
                        "type": "fitCellContents",
                        "defaultMinWidth": 10,
                    },
                    "domLayout": "normal",
                })
                .classes("ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham")
                .classes("full-width")
                .style("height: 310px")
                .mark("GRID_BUCKET")
                .on("selectionChanged", _handle_grid_selection_changed)
            )

            bucket_form.delete_button = (
                ui.button(
                    "Delete",
                    on_click=_delete_selected,
                )
                .mark("BUTTON_DELETE_OBJECTS")
                .props("color=red")
                .classes("w-1/5")
            )
            bucket_form.delete_button.disable()

            ui.timer(
                interval=1,
                callback=lambda: bucket_form.grid.classes(
                    add="ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham",
                    remove="ag-theme-balham" if app.storage.general.get("dark_mode", False) else "ag-theme-balham-dark",
                )
                if bucket_form.grid
                else None,
            )
