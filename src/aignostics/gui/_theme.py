"""Theming."""

from pathlib import Path

from aignostics.utils import BasePageBuilder


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app, ui  # noq  # noqa: PLC0415

        ui.add_head_html("""
            <style type="text/tailwindcss">
                @layer components {
                    .blue-box {
                        @apply bg-blue-500 p-12 text-center shadow-lg rounded-lg text-white;
                    }
                }
            </style>
        """)

        assets = Path(__file__).parent / "assets"
        app.add_static_files("/assets", assets)
