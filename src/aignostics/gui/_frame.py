from contextlib import contextmanager

from aignostics.utils import __version__


@contextmanager
def frame(navigation_title: str, navigation_icon: str | None = None, left_sidebar: bool = False):  # noqa: ANN202
    """Custom page frame to share the same styling and behavior across all pages."""
    from nicegui import context, ui  # noqa: PLC0415

    ui.colors(primary="#6E93D6", secondary="#53B689", accent="#111B1E", positive="#53B689")
    with ui.header(elevated=True).style("background-color: #3874c8").classes("items-center justify-between"):
        ui.space()
        if navigation_icon is not None:
            ui.icon(navigation_icon)
        ui.label(navigation_title)
        ui.space()
        dark = ui.dark_mode()
        ui.button(on_click=dark.toggle, icon="dark_mode").props("flat color=black")
        with ui.link(target="https://platform.aignostics.com/support", new_tab=True):
            ui.button(icon="help").props("flat color=white")

        ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props("flat color=white")
    if left_sidebar:
        with ui.left_drawer(top_corner=True, bottom_corner=True).style("background-color: #d7e3f4"):
            yield
    else:
        yield
    with ui.right_drawer(fixed=True).style("background-color: #ebf1fa").props("bordered") as right_drawer:
        ui.link("Aignostics Applications", "/").mark("LINK_APPLICATIONS").tailwind.font_weight(
            "bold" if context.client.page.path == "/" else "normal"
        )
        ui.link("Image Data Commons by NCI", "/idc").mark("LINK_IDC").tailwind.font_weight(
            "bold" if context.client.page.path == "/idc" else "normal"
        )
        #  if context.client.page.path == "/" else "font-weight: normal"
        ui.link("System", "/system").mark("LINK_SYSTEM").tailwind.font_weight(
            "bold" if context.client.page.path == "/system" else "normal"
        )
        ui.separator()
        ui.link("⎘ Platform", "https://platform.aignostics.com", new_tab=True).mark("LINK_PLATFORM")
        ui.link("⎘ Documentation", "https://aignostics.readthedocs.org/", new_tab=True).mark("LINK_DOCUMENTATION")
    with ui.footer().style("background-color: #3874c8"):
        with ui.row(align_items="center").classes("justify-center w-full"):
            ui.html(
                '<iframe src="https://status.aignostics.com/badge?theme=dark" '
                'width="250" height="30" frameborder="0" scrolling="no" '
                'style="color-scheme: dark"></iframe>'
            )
            ui.space()
            ui.label(f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻")
    right_drawer.hide()
