"""Theming."""

from pathlib import Path

from aignostics.utils import BasePageBuilder


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app  # noq  # noqa: PLC0415

        assets = Path(__file__).parent / "assets"
        app.add_static_files("/assets", assets)
