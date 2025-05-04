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

    ui.dark_mode(app.storage.general.get("dark_mode", False))
