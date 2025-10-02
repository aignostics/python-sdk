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
STORAGE_TAB_RUNS_COMPLETED_ONLY = "runs_completed_only"

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
        try:
            with ui.list().props(BORDERED_SEPARATOR).classes("full-width"):
                ui.item_label("Applications").props("header")
                ui.separator()
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
                            ui.icon(application_id_to_icon(application.application_id), color="primary"),
                        ):
                            ui.tooltip(application.application_id)
                        with ui.item_section():
                            ui.label(f"{application.name}").tailwind.font_weight(
                                "bold"
                                if context.client.page.path == "/application/{application_id}"
                                and args
                                and args.get("application_id") == application.application_id
                                else "normal"
                            )
        except Exception as e:
            ui.label(f"Failed to list applications: {e!s}").mark("LABEL_ERROR")
            logger.exception("Failed to load applications")

        async def application_runs_load_and_render(
            runs_column: ui.column, completed_only: bool = False, note_query: str | None = None
        ) -> None:
            with runs_column:
                try:
                    runs = await nicegui_run.io_bound(
                        Service.application_runs_static,
                        limit=RUNS_LIMIT,
                        completed_only=completed_only,
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
                                on_click=lambda run_id=run_data["application_run_id"]: ui.navigate.to(
                                    f"/application/run/{run_id}"
                                )
                            )
                            .props("clickable")
                            .classes("w-full")
                            .mark(f"SIDEBAR_RUN_ITEM:{index}")
                        ):
                            with ui.item_section().props("avatar"):
                                icon, color = run_status_to_icon_and_color(run_data["status"])
                                with ui.icon(icon, color=color):
                                    ui.tooltip(
                                        f"Run {run_data['application_run_id']}, "
                                        f"status {run_data['status'].value.upper()}"
                                    )
                            with ui.item_section():
                                ui.label(f"{run_data['application_version_id']}").tailwind.font_weight(
                                    "bold"
                                    if context.client.page.path == "/application/run/{application_run_id}"
                                    and args
                                    and args.get("application_run_id") == run_data["application_run_id"]
                                    else "normal"
                                )
                                ui.label(
                                    f"triggered on {run_data['triggered_at'].astimezone().strftime('%m-%d %H:%M')}"
                                )
                    if not runs:
                        with ui.item():
                            with ui.item_section().props("avatar"):
                                ui.icon("info")
                            with ui.item_section():
                                ui.label("You did not yet create a run.")
                except Exception:
                    runs_column.clear()
                    with ui.item():
                        with ui.item_section().props("avatar"):
                            ui.icon("error")
                        with ui.item_section():
                            ui.label("Failed to load application runs.")
                    logger.exception("Failed to load application runs")

        @ui.refreshable
        async def _runs_list() -> None:
            with ui.column().classes("full-width justify-center") as runs_column:
                with ui.row().classes("w-full justify-center"):
                    ui.spinner(size="lg").classes("m-5")
                await ui.context.client.connected()
                background_tasks.create_lazy(
                    coroutine=application_runs_load_and_render(
                        runs_column=runs_column,
                        completed_only=app.storage.tab.get(STORAGE_TAB_RUNS_COMPLETED_ONLY, False),
                        note_query=search_input.query,
                    ),
                    name="_runs_list",
                )

        class RunFilterButton(ui.icon):
            def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
                super().__init__(*args, **kwargs)
                self._state = app.storage.tab.get(STORAGE_TAB_RUNS_COMPLETED_ONLY, False)
                self.on("click", self.toggle)

            def toggle(self) -> None:
                self._state = not self._state
                app.storage.tab[STORAGE_TAB_RUNS_COMPLETED_ONLY] = self._state
                self.update()
                _runs_list.refresh()

            def update(self) -> None:
                self.props(f"color={'positive' if self._state else 'grey'}")
                super().update()

            def is_active(self) -> bool:
                return bool(self._state)

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
