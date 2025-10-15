from typing import Any

from nicegui import app, background_tasks, context, ui  # noq
from nicegui import run as nicegui_run

from aignostics.gui import frame
from aignostics.utils import get_logger

from .._service import Service  # noqa: TID252
from ._utils import application_id_to_icon, run_status_to_icon_and_color

logger = get_logger(__name__)

BORDERED_SEPARATOR = "bordered separator"
RUNS_LIMIT = 100
STORAGE_TAB_RUNS_HAS_OUTPUT = "runs_has_output"

service = Service()


class SearchInput:
    query: str = ""


search_input = SearchInput()


async def _frame(  # noqa: C901, PLR0913, PLR0915, PLR0917
    navigation_title: str,
    navigation_icon: str | None = None,
    navigation_icon_color: str | None = None,
    navigation_icon_tooltip: str | None = None,
    left_sidebar: bool = False,
    args: dict[str, Any] | None = None,
) -> None:
    if args is None:
        args = {}
    with frame(  # noqa: PLR1702
        navigation_title=navigation_title,
        navigation_icon=navigation_icon,
        navigation_icon_color=navigation_icon_color,
        navigation_icon_tooltip=navigation_icon_tooltip,
        left_sidebar=left_sidebar,
    ):
        with ui.list().props(BORDERED_SEPARATOR).classes("full-width"):
            ui.item_label("Applications").props("header")
            ui.separator()
            try:
                applications = await nicegui_run.io_bound(Service.applications_static)
                if applications is None:
                    message = (  # type: ignore[unreachable]
                        "nicegui_run.io_bound(Service.applications_static) returned None, "
                        "likely canceled by appliction shutdown."
                    )
                    logger.error(message)
                    raise RuntimeError(message)  # noqa: TRY301
                for application in applications:
                    with (
                        ui.item(
                            on_click=lambda app_id=application.application_id: ui.navigate.to(f"/application/{app_id}")
                        )
                        .mark(f"SIDEBAR_APPLICATION:{application.application_id}")
                        .props("clickable")
                    ):
                        with (
                            ui.item_section().props("avatar"),
                            ui.icon(application_id_to_icon(application.application_id), color="primary").classes(
                                "text-4xl"
                            ),
                        ):
                            ui.tooltip(application.application_id)
                        with ui.item_section():
                            ui.label(f"{application.name}").classes(
                                "font-bold"
                                if context.client.page.path == "/application/{application_id}"
                                and args
                                and args.get("application_id") == application.application_id
                                else "font-normal"
                            )
            except Exception as e:
                with ui.item():
                    with ui.item_section().props("avatar"):
                        ui.icon("error", color="red").classes("text-4xl")
                    with ui.item_section():
                        ui.label(f"Could not load applications: {e!s}").mark("LABEL_ERROR")
                        logger.exception("Could not load applications")

        async def application_runs_load_and_render(
            runs_column: ui.column, has_output: bool = False, note_query: str | None = None
        ) -> None:
            with runs_column:
                try:
                    runs = await nicegui_run.io_bound(
                        Service.application_runs_static,
                        limit=RUNS_LIMIT,
                        has_output=has_output,
                        note_regex=f".*{note_query}.*" if note_query else None,
                        note_query_case_insensitive=True,
                    )
                    if runs is None:
                        message = (  # type: ignore[unreachable]
                            "nicegui_run.io_bound(Service.application_runs_static) returned None, "
                            "likely canceled by shutdown."
                        )
                        logger.error(message)
                        raise RuntimeError(message)  # noqa: TRY301
                    runs_column.clear()
                    for index, run_data in enumerate(runs):
                        with (
                            ui.item(
                                on_click=lambda run_id=run_data["run_id"]: ui.navigate.to(f"/application/run/{run_id}")
                            )
                            .props("clickable")
                            .classes("w-full")
                            .mark(f"SIDEBAR_RUN_ITEM:{index}")
                        ):
                            with ui.item_section().props("avatar"):
                                icon, color = run_status_to_icon_and_color(
                                    run_data["state"],
                                    run_data["termination_reason"],
                                    run_data["item_count"],
                                    run_data["item_succeeded_count"],
                                )
                                with (
                                    ui.circular_progress(
                                        min=0,
                                        max=run_data["item_count"] if run_data["item_count"] > 0 else 1,
                                        value=run_data["item_succeeded_count"],
                                        color=color,
                                        show_value=False,
                                    ),
                                    ui.icon(icon, color=color).classes("text-4xl"),
                                ):
                                    tooltip_text = (
                                        f"{run_data['item_succeeded_count']} of {run_data['item_count']} succeeded, "
                                        f"status {run_data['state'].value.upper()}, "
                                    )
                                    if run_data["termination_reason"]:
                                        tooltip_text += f"{run_data['termination_reason']}, "
                                    tooltip_text += f"run id {run_data['run_id']}"
                                    ui.tooltip(tooltip_text)
                            with ui.item_section():
                                ui.label(f"{run_data['application_id']} ({run_data['version_number']})").classes(
                                    "font-bold"
                                    if context.client.page.path == "/application/run/{run_id}"
                                    and args
                                    and args.get("run_id") == run_data["run_id"]
                                    else "font-normal"
                                ).mark(f"LABEL_RUN_APPLICATION:{index}")
                                ui.label(f"submitted {run_data['submitted_at'].astimezone().strftime('%m-%d %H:%M')}")
                    if not runs:
                        with ui.item():
                            with ui.item_section().props("avatar"):
                                ui.icon("info")
                            with ui.item_section():
                                ui.label("You did not yet create a run.")
                except Exception as e:
                    runs_column.clear()
                    with ui.item():
                        with ui.item_section().props("avatar"):
                            ui.icon("error", color="red")
                        with ui.item_section():
                            ui.label(f"Could not load runs: {e!s}")
                    logger.exception("Could not load runs")

        @ui.refreshable
        async def _runs_list() -> None:
            with ui.column().classes("full-width justify-center") as runs_column:
                with ui.row().classes("w-full justify-center"):
                    ui.spinner(size="lg").classes("m-5")
                await ui.context.client.connected()
                background_tasks.create_lazy(
                    coroutine=application_runs_load_and_render(
                        runs_column=runs_column,
                        has_output=app.storage.tab.get(STORAGE_TAB_RUNS_HAS_OUTPUT, False),
                        note_query=search_input.query,
                    ),
                    name="_runs_list",
                )

        class RunFilterButton(ui.icon):
            _has_output: bool = False

            def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
                super().__init__(*args, **kwargs)
                self._has_output = app.storage.tab.get(STORAGE_TAB_RUNS_HAS_OUTPUT, False)
                self.on("click", self.toggle)

            def toggle(self) -> None:
                self._has_output = not self._has_output
                app.storage.tab[STORAGE_TAB_RUNS_HAS_OUTPUT] = self._has_output
                self.update()
                _runs_list.refresh()

            def update(self) -> None:
                self.props(f"color={'positive' if self._has_output else 'grey'}")
                super().update()

            def is_active(self) -> bool:
                return bool(self._has_output)

        try:
            with ui.list().props(BORDERED_SEPARATOR).classes("full-width"):
                with ui.row(align_items="center").classes("justify-between"):
                    ui.item_label("Runs").props("header")
                    await ui.context.client.connected()
                    ui.input(
                        placeholder="Filter by note",
                        on_change=_runs_list.refresh,
                    ).bind_value(search_input, "query").props("rounded outlined dense clearable").style(
                        "max-width: 15ch;"
                    ).classes("text-xs").mark("INPUT_RUNS_FILTER_NOTE")
                    with RunFilterButton("done_all", size="sm").classes("mr-3").mark("BUTTON_RUNS_FILTER_COMPLETED"):
                        ui.tooltip("Show completed runs only")
                ui.separator()
                await _runs_list()
        except Exception as e:  # noqa: BLE001
            ui.label(f"Failed to list application runs: {e!s}").mark("LABEL_ERROR")
