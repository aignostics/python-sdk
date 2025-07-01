"""Layout including sidebar and menu."""

import contextlib
import platform
from collections.abc import Generator
from contextlib import contextmanager
from importlib.util import find_spec
from typing import Any

from humanize import naturaldelta

from aignostics.utils import __version__, open_user_data_directory

from ._theme import theme

FLAT_COLOR_WHITE = "flat color=white"

HEALTH_UPDATE_INTERVAL = 30
USERINFO_UPDATE_INTERVAL = 60 * 60

PROFILE_EDIT_URL = "https://platform.aignostics.com/dashboard/account/profile"


@contextmanager
def frame(  # noqa: C901, PLR0915
    navigation_title: str,
    navigation_icon: str | None = None,
    navigation_icon_color: str | None = None,
    navigation_icon_tooltip: str | None = None,
    left_sidebar: bool = False,
) -> Generator[Any, Any, Any]:
    """Custom page frame to share the same styling and behavior across all pages.

    Args:
        navigation_title (str): The title of the navigation bar.
        navigation_icon (str | None): The icon for the navigation bar.
        navigation_icon_color (str | None): The color of the navigation icon.
        navigation_icon_tooltip (str | None): The tooltip for the navigation icon.
        left_sidebar (bool): Whether to show the left sidebar or not.

    Yields:
        Generator[Any, Any, Any]: The context manager for the page frame.
    """
    from nicegui import app, background_tasks, context, run, ui  # noqa: PLC0415

    from aignostics.platform import Service as PlatformService  # noqa: PLC0415
    from aignostics.platform import UserInfo  # noqa: PLC0415
    from aignostics.system import Service as SystemService  # noqa: PLC0415

    theme()

    user_info: UserInfo | None = None
    launchpad_healthy: bool | None = None

    @ui.refreshable
    def _user_info_ui() -> None:
        spinner = ui.spinner().props("flat color=purple-400")
        if user_info and user_info.profile:
            spinner.set_visibility(False)
            icon = "img:" + user_info.profile.picture if user_info.profile.picture else "account_circle"
            with (
                ui.dropdown_button(icon=icon)
                .style("width: 30px; height: 30px; border-radius: 50%")
                .classes("mr-3")
                .props(FLAT_COLOR_WHITE),
                ui.card(),
            ):
                with ui.row():
                    if user_info.profile.picture:
                        ui.image(user_info.profile.picture).style("width: 90px; height: 90px")
                    else:
                        ui.icon("account_circle", size="90px").classes("text-gray-500")
                    with ui.column():
                        ui.label(f"{user_info.profile.name} ({user_info.profile.email})")
                        ui.label(f"{user_info.role.capitalize()} at {user_info.org_name or user_info.org_id}")
                        ui.label(f"Authentication valid for {naturaldelta(user_info.token.expires_in)}")
                ui.separator()
                with ui.row().classes("items-center justify-between full-width"):
                    ui.button("Re-authenticate now", icon="switch_account", on_click=_user_info_ui_relogin)
                    ui.space()
                    ui.button(
                        "Edit Profile",
                        icon="edit",
                        on_click=lambda _: ui.navigate.to(PROFILE_EDIT_URL, new_tab=True),
                    )

    async def _user_info_ui_load() -> None:
        nonlocal user_info
        with contextlib.suppress(Exception):
            user_info = await run.cpu_bound(PlatformService.get_user_info)
        await ui.context.client.connected()
        app.storage.tab["user_info"] = user_info
        _user_info_ui.refresh()

    ui.timer(interval=USERINFO_UPDATE_INTERVAL, callback=_user_info_ui_load, immediate=True)

    async def _user_info_ui_relogin() -> None:
        """Relogin to the platform."""
        nonlocal user_info
        user_info = None
        await ui.context.client.connected()
        app.storage.tab["user_info"] = user_info
        _user_info_ui.refresh()
        with contextlib.suppress(Exception):
            user_info = await run.io_bound(PlatformService.get_user_info, relogin=True)
            app.storage.tab["user_info"] = user_info
        ui.navigate.reload()

    @ui.refreshable
    def health_icon() -> None:
        if launchpad_healthy:
            ui.icon("settings", color="positive")
        elif launchpad_healthy is not None:
            ui.icon("settings", color="negative")

    @ui.refreshable
    def health_link() -> None:
        with (
            ui.link(target="/system").style(
                "background-color: white; text-decoration: none; color: black; padding-left: 10px"
            ),
            ui.row().classes("items-center"),
        ):
            ui.tooltip("Check Launchpad Status")
            if launchpad_healthy:
                ui.icon("check_circle", color="positive")
                ui.label("Launchpad is healthy")
            elif launchpad_healthy is not None:
                ui.icon("error", color="negative")
                ui.label("Launchpad is unhealthy")
            else:
                ui.spinner()

    async def _health_load_and_render() -> None:
        nonlocal launchpad_healthy
        with contextlib.suppress(Exception):
            launchpad_healthy = bool(await run.cpu_bound(SystemService.health_static))
        health_icon.refresh()
        health_link.refresh()

    def _update_health() -> None:
        background_tasks.create_lazy(
            coroutine=_health_load_and_render(),
            name="_health_load_and_render",
        )
        ui.run_javascript("document.getElementById('betterstack').src = document.getElementById('betterstack').src;")

    ui.timer(interval=HEALTH_UPDATE_INTERVAL, callback=_update_health, immediate=True)

    # Set background color based on dark mode
    ui.query("body").classes(
        replace="bg-aignostics-light dark:bg-aignostics-dark"
    )  # https://github.com/zauberzeug/nicegui/pull/448#issuecomment-1492442558

    # Create right_drawer reference before using it
    right_drawer = ui.right_drawer(fixed=True)
    right_drawer.hide()  # Hide by default

    with ui.header(elevated=True).classes("items-center justify-between"):
        with ui.link(target="/"):
            ui.image("/assets/logo.png").style("width: 110px; margin-left: 10px")
            ui.tooltip("Go to start page")
        ui.space()
        if navigation_icon is not None:
            if navigation_icon_tooltip:
                with ui.icon(navigation_icon, color=navigation_icon_color).classes("text-4xl"):
                    ui.tooltip(navigation_icon_tooltip)
            else:
                ui.icon(navigation_icon, color=navigation_icon_color).classes("text-4xl")
        ui.label(navigation_title).classes("text-xl font-bold")
        ui.space()

        dark = ui.dark_mode(app.storage.general.get("dark_mode", False))

        # Fix the dark mode toggle button callback
        def toggle_dark_mode() -> None:
            app.storage.general["dark_mode"] = not app.storage.general.get("dark_mode", False)
            dark.toggle()
            if dark.value:
                ui.query("body").classes(replace="bg-aignostics-dark")
            else:
                ui.query("body").classes(replace="bg-aignostics-light")

        ui.button(
            on_click=toggle_dark_mode,
            icon="dark_mode",
        ).set_visibility(False)

        _user_info_ui()

        with ui.button(icon="folder_special", on_click=lambda _: open_user_data_directory()).props(
            "flat color=purple-400"
        ):
            ui.tooltip("Open data directory of Launchpad")

        with ui.button(on_click=lambda _: right_drawer.toggle(), icon="menu").props(FLAT_COLOR_WHITE):
            ui.tooltip("Open menu")

    if left_sidebar:
        with ui.left_drawer(top_corner=True, bottom_corner=True, elevated=True).props("breakpoint=0"):
            yield
    else:
        yield

    # Populate the right_drawer we created earlier
    with right_drawer, ui.column(align_items="stretch").classes("h-full"):  # noqa: PLR1702
        with ui.list():
            with ui.item(on_click=lambda _: ui.navigate.to("/")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("biotech", color="primary")
                with ui.item_section():
                    ui.label("Run Applications").tailwind.font_weight(
                        "bold" if context.client.page.path == "/" else "normal"
                    )
            with ui.item(on_click=lambda _: ui.navigate.to("/dataset/idc")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("image", color="primary")
                with ui.item_section():
                    ui.label("Download Datasets").tailwind.font_weight(
                        "bold" if context.client.page.path == "/dataset/idc" else "normal"
                    )
        ui.space()
        with ui.list():
            if find_spec("ijson"):  # noqa: SIM102
                if not (platform.system() == "Linux" and platform.machine() == "aarch64"):
                    with ui.item(on_click=lambda _: ui.navigate.to("/qupath")).props("clickable"):
                        with ui.item_section().props("avatar"):
                            ui.icon("visibility", color="primary")
                        with ui.item_section():
                            ui.label("QuPath Extension").tailwind.font_weight(
                                "bold" if context.client.page.path == "/qupath" else "normal"
                            )
            if find_spec("marimo"):
                with ui.item(on_click=lambda _: ui.navigate.to("/notebook")).props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("difference", color="primary")
                    with ui.item_section():
                        ui.label("Marimo Extension").tailwind.font_weight(
                            "bold" if context.client.page.path == "/notebook" else "normal"
                        )
            with ui.item(on_click=lambda _: ui.navigate.to("/bucket")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("cloud", color="primary")
                with ui.item_section():
                    ui.label("Manage Cloud Bucket").tailwind.font_weight(
                        "bold" if context.client.page.path == "/bucket" else "normal"
                    )
            with ui.item(on_click=lambda _: ui.navigate.to("/system")).props("clickable"):
                with ui.item_section().props("avatar"):
                    health_icon()
                with ui.item_section():
                    ui.label("Info and Settings").tailwind.font_weight(
                        "bold" if context.client.page.path == "/system" else "normal"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("domain", color="primary")
                with ui.item_section():
                    ui.link("Go to Console", "https://platform.aignostics.com", new_tab=True).mark("LINK_PLATFORM")
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("local_library", color="primary")
                with ui.item_section():
                    ui.link("Read The Docs", "https://aignostics.readthedocs.org/", new_tab=True).mark(
                        "LINK_DOCUMENTATION"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("help", color="primary")
                with ui.item_section():
                    ui.link("Get Support", "https://platform.aignostics.com/support", new_tab=True).mark(
                        "LINK_DOCUMENTATION"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("check_circle", color="primary")
                with ui.item_section():
                    ui.link("Check Platform Status", "https://status.aignostics.com", new_tab=True).mark(
                        "LINK_DOCUMENTATION"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("handshake", color="primary")
                with ui.item_section():
                    ui.link(
                        "Attributions", "https://aignostics.readthedocs.io/en/latest/attributions.html", new_tab=True
                    ).mark("LINK_ATTRIBUTIONS")
            if app.native.main_window:
                ui.separator()
                with ui.item(on_click=app.shutdown).props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("logout", color="primary")
                    with ui.item_section():
                        ui.label("Quit Launcher")
    with (
        ui.footer().style("padding-top:0px; padding-left: 0px; height: 30px; background-color: white"),
        ui.row(align_items="center").classes("justify-start w-full"),
    ):
        health_link()
        with ui.row().style("padding: 0"):
            ui.html(
                '<iframe id="betterstack" src="https://status.aignostics.com/badge?theme=dark" '
                'width="250" height="30" frameborder="0" scrolling="no" '
                'style="color-scheme: dark"></iframe>'
            ).style("margin-left: 0px;")
            ui.tooltip("Check Platform Status")
        ui.space()
        with ui.row():
            ui.html(
                '🔬<a style="color: black; text-decoration: underline" target="_blank" href="https://github.com/aignostics/python-sdk/">'
                f"Aignostics Python SDK v{__version__}</a>"
                ' - built with love in <a style="color: black; text-decoration: underline" target="_blank"'
                ' href="https://www.aignostics.com/company/about">Berlin</A> 🐻'
            ).style("color: black")
            ui.tooltip("Visit GitHub repository of Aignostics Python SDK")
