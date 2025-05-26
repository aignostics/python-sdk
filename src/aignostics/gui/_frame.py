"""Layout including sidebar and menu."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from aignostics.utils import __version__

from ._theme import theme

FLAT_COLOR_WHITE = "flat color=white"


@contextmanager
def frame(  # noqa: PLR0915
    navigation_title: str, navigation_icon: str | None = None, left_sidebar: bool = False
) -> Generator[Any, Any, Any]:
    """Custom page frame to share the same styling and behavior across all pages.

    Args:
        navigation_title (str): The title of the navigation bar.
        navigation_icon (str | None): The icon for the navigation bar.
        left_sidebar (bool): Whether to show the left sidebar or not.

    Yields:
        Generator[Any, Any, Any]: The context manager for the page frame.
    """
    from nicegui import app, context, ui  # noqa: PLC0415

    theme()

    # Create right_drawer reference before using it
    right_drawer = ui.right_drawer(fixed=True)
    right_drawer.hide()  # Hide by default

    with ui.header(elevated=True).classes("items-center justify-between"):
        with ui.link(target="/"):
            ui.image("/assets/logo.png").style("width: 110px")
        ui.space()
        if navigation_icon is not None:
            ui.icon(navigation_icon)
        ui.label(navigation_title)
        ui.space()

        dark = ui.dark_mode(app.storage.general.get("dark_mode", False))

        # Fix the dark mode toggle button callback
        def toggle_dark_mode() -> None:
            app.storage.general["dark_mode"] = not app.storage.general.get("dark_mode", False)
            dark.toggle()

        ui.button(
            on_click=toggle_dark_mode,
            icon="dark_mode",
        ).props("flat color=black")

        with ui.link(target="https://aignostics.readthedocs.org/", new_tab=True):
            ui.button(icon="local_library").props(FLAT_COLOR_WHITE)

        with ui.link(target="https://platform.aignostics.com/support", new_tab=True):
            ui.button(icon="help").props(FLAT_COLOR_WHITE)

        ui.button(on_click=lambda _: right_drawer.toggle(), icon="menu").props(FLAT_COLOR_WHITE)

    if left_sidebar:
        with ui.left_drawer(top_corner=True, bottom_corner=True, elevated=True).props("breakpoint=0"):
            yield
    else:
        yield

    # Populate the right_drawer we created earlier
    with right_drawer, ui.column(align_items="stretch").classes("h-full"):
        with ui.list():
            with ui.item(on_click=lambda _: ui.navigate.to("/")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("biotech", color="#433D6B")
                with ui.item_section():
                    ui.label("Run Applications").tailwind.font_weight(
                        "bold" if context.client.page.path == "/" else "normal"
                    )
            with ui.item(on_click=lambda _: ui.navigate.to("/dataset/idc")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("image", color="#BA1F40")
                with ui.item_section():
                    ui.label("Download Datasets").tailwind.font_weight(
                        "bold" if context.client.page.path == "/dataset/idc" else "normal"
                    )
        ui.space()
        with ui.list():
            with ui.item(on_click=lambda _: ui.navigate.to("/bucket")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("cloud", color="#4185F4")
                with ui.item_section():
                    ui.label("Manage Cloud Bucket").tailwind.font_weight(
                        "bold" if context.client.page.path == "/bucket" else "normal"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("domain")
                with ui.item_section():
                    ui.link("Go to Console", "https://platform.aignostics.com", new_tab=True).mark("LINK_PLATFORM")
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("local_library")
                with ui.item_section():
                    ui.link("Read The Docs", "https://aignostics.readthedocs.org/", new_tab=True).mark(
                        "LINK_DOCUMENTATION"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("help")
                with ui.item_section():
                    ui.link("Get Support", "https://platform.aignostics.com/support", new_tab=True).mark(
                        "LINK_DOCUMENTATION"
                    )
            with ui.item().props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("check_circle")
                with ui.item_section():
                    ui.link("Platform Status", "https://status.aignostics.com", new_tab=True).mark("LINK_DOCUMENTATION")
            with ui.item(on_click=lambda _: ui.navigate.to("/system")).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("settings", color="positive")
                with ui.item_section():
                    ui.label("Inspector").tailwind.font_weight(
                        "bold" if context.client.page.path == "/system" else "normal"
                    )
            with ui.item(on_click=app.shutdown).props("clickable"):
                with ui.item_section().props("avatar"):
                    ui.icon("logout", color="negative")
                with ui.item_section():
                    ui.label("Quit Launcher")

    with (
        ui.footer().style("background-color: #EDEDE9").style("padding-top:0px; height: 30px;"),
        ui.row(align_items="center").classes("justify-center w-full"),
    ):
        ui.html(
            '<iframe src="https://status.aignostics.com/badge?theme=dark" '
            'width="250" height="30" frameborder="0" scrolling="no" '
            'style="color-scheme: dark"></iframe>'
        )
        ui.space()
        ui.html(
            '🔬<a style="color: black; text-decoration: underline" target="_blank" href="https://github.com/aignostics/python-sdk/">'
            f"Aignostics Python SDK v{__version__}</a>"
            ' - built with love in <a style="color: black; text-decoration: underline" target="_blank"'
            ' href="https://www.aignostics.com/company/about">Berlin</A> 🐻'
        ).style("color: black")
