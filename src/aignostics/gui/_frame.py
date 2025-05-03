from contextlib import contextmanager

from aignostics.utils import __version__


@contextmanager
def frame(navigation_title: str, navigation_icon: str | None = None, left_sidebar: bool = False):  # noqa: ANN202, PLR0915
    """Custom page frame to share the same styling and behavior across all pages."""
    from nicegui import app, context, ui  # noqa: PLC0415

    ui.colors(primary="#433D6B", secondary="#B9B1DF", accent="#111B1E", positive="#B0CCDA", negative="#EBB8C7")

    ui.add_head_html("""
        <style type="text/tailwindcss">
            @layer components {
                .blue-box {
                    @apply bg-blue-500 p-12 text-center shadow-lg rounded-lg text-white;
                }
            }
            ::-webkit-scrollbar {
                display: none;
            }
            .bg-red-300 {
                background-color: #E9B9C7 !important;
            }
            .bg-green-300 {
                background-color: #B3CCD9 !important;
            }
        </style>
    """)

    with ui.header(elevated=True).classes("items-center justify-between"):
        ui.image("/assets/logo.png").style("width: 110px")
        ui.space()
        if navigation_icon is not None:
            ui.icon(navigation_icon)
        ui.label(navigation_title)
        ui.space()

        dark = ui.dark_mode(app.storage.general.get("dark_mode", False))
        ui.button(
            on_click=lambda: [
                app.storage.general.__setitem__("dark_mode", not app.storage.general.get("dark_mode", False)),
                dark.toggle(),
            ],
            icon="dark_mode",
        ).props("flat color=black")

        with ui.link(target="https://aignostics.readthedocs.org/", new_tab=True):
            ui.button(icon="local_library").props("flat color=white")

        with ui.link(target="https://platform.aignostics.com/support", new_tab=True):
            ui.button(icon="help").props("flat color=white")

        ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props("flat color=white")  # noqa: PLW0108

    if left_sidebar:
        with ui.left_drawer(top_corner=True, bottom_corner=True, elevated=True).props("breakpoint=0"):
            yield
    else:
        yield

    with ui.right_drawer(fixed=True).style("background-color: #EDEDE9") as right_drawer:  # noqa: SIM117
        with ui.column(align_items="stretch").classes("h-full"):
            with ui.list():
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("biotech", color="#433D6B")
                    with ui.item_section():
                        ui.link("Run Applications", "/").mark("LINK_APPLICATIONS").tailwind.font_weight(
                            "bold" if context.client.page.path == "/" else "normal"
                        )
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("cloud", color="#4185F4")
                    with ui.item_section():
                        ui.link("Manage Cloud Bucket", "/bucket").mark("LINK_BUCKET").tailwind.font_weight(
                            "bold" if context.client.page.path == "/bucket" else "normal"
                        )
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("image", color="#BA1F40")
                    with ui.item_section():
                        ui.link("Download Datasets", "/idc").mark("LINK_IDC").tailwind.font_weight(
                            "bold" if context.client.page.path == "/idc" else "normal"
                        )
            ui.space()
            with ui.list():
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("settings", color="black")
                    with ui.item_section():
                        ui.link("Diagnose System", "/system").mark("LINK_SYSTEM").tailwind.font_weight(
                            "bold" if context.client.page.path == "/system" else "normal"
                        )
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("domain", color="black")
                    with ui.item_section():
                        ui.link("Go to Management UI", "https://platform.aignostics.com", new_tab=True).mark(
                            "LINK_PLATFORM"
                        )
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("local_library", color="black")
                    with ui.item_section():
                        ui.link("Read The Docs", "https://aignostics.readthedocs.org/", new_tab=True).mark(
                            "LINK_DOCUMENTATION"
                        )
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("help", color="black")
                    with ui.item_section():
                        ui.link("Get Support", "https://platform.aignostics.com/support", new_tab=True).mark(
                            "LINK_DOCUMENTATION"
                        )
                with ui.item().props("clickable"):
                    with ui.item_section().props("avatar"):
                        ui.icon("check_circle", color="black")
                    with ui.item_section():
                        ui.link("Platform Status", "https://status.aignostics.com", new_tab=True).mark(
                            "LINK_DOCUMENTATION"
                        )

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
    # Boot
    right_drawer.hide()
    ui.dark_mode(app.storage.general.get("dark_mode", False))
