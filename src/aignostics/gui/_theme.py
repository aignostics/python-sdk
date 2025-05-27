"""Theming."""

from pathlib import Path

from aignostics.utils import BasePageBuilder


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app  # noq  # noqa: PLC0415

        assets = Path(__file__).parent / "assets"
        app.add_static_files("/assets", assets)


def theme() -> None:
    """Set theme."""
    from nicegui import app, ui  # noqa: PLC0415

    ui.colors(
        primary="#1C1242",
        secondary="#B9B1DF",
        accent="#111B1E",
        dark="#1d1d1d1d",
        dark_page="#12121212",
        positive="#0CA57B",
        negative="#D4313C",
        info="#261C8D",
        warning="#FFCC00",
        brand_white="#EFF0F1",
        brand_background_light="#E7E6E8",
    )

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
            .q-drawer-container {
                background-color: red
            }
            .bg-red-300 {
                background-color: #EEADB1 !important;
            }
            .bg-green-300 {
                background-color: #9EDBCA !important;
            }
            .bg-aignostics-light {
                background-color: #ECEDE9 !important;
            }
            .bg-aignostics-dark {
                background-color: #000000 !important;
            }
            .q-stepper, .q-drawer, .q-footer {
                background-color: #F0F0F0 !important;
            }
            .q-drawer.q-dark {
                background-color: #000000 !important;
            }
            html *
            {
                font-family: "Nexa Text", Arial, sans-serif;
            }
            header {
                color: white
            }
        </style>
    """)

    ui.dark_mode(app.storage.general.get("dark_mode", False))
