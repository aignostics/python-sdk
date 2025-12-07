"""WSI API."""

from __future__ import annotations

from pathlib import Path

from fastapi import Response
from loguru import logger

from aignostics.utils import BasePageBuilder

from ._openslide_handler import DEFAULT_MAX_SAFE_DIMENSION
from ._service import Service


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from fastapi.responses import RedirectResponse  # noqa: PLC0415
        from nicegui import app  # noqa: PLC0415

        app.add_static_files("/wsi_assets", Path(__file__).parent / "assets")

        @app.get("/thumbnail")
        def thumbnail(
            source: str,
            max_safe_dimension: int = DEFAULT_MAX_SAFE_DIMENSION,
        ) -> Response:
            """Serve a thumbnail for a given source reference.

            Args:
                source (str): The source of the slide pointing to a file on the filesystem.
                max_safe_dimension (int): Maximum dimension (width or height) of smallest pyramid level
                    before considering the pyramid incomplete.

            Returns:
                fastapi.Response: HTTP response containing the thumbnail or fallback image.
            """
            try:
                return Response(
                    content=Service().get_thumbnail_bytes(Path(source), max_safe_dimension=max_safe_dimension),
                    media_type="image/png",
                )
            except ValueError:
                logger.warning("Error generating thumbnail on bad request or invalid image input")
                return RedirectResponse("/wsi_assets/fallback.png")
            except RuntimeError:
                logger.exception("Internal server error when generating thumbnail")
                return RedirectResponse("/wsi_assets/fallback.png")

        @app.get("/tiff")
        def tiff(url: str) -> Response:
            """Serve a tiff as jpg.

            Args:
                url (str): The URL of the tiff.

            Returns:
                fastapi.Response: HTTP response containing the converted tiff or fallback image
            """
            try:
                return Response(content=Service().get_tiff_as_jpg(url), media_type="image/jpeg")
            except ValueError:
                logger.warning("Error generating jpeg on bad request or invalid tiff input")
                return RedirectResponse("/wsi_assets/fallback.png")
            except RuntimeError:
                logger.exception("Internal server error when generating jpeg")
                return RedirectResponse("/wsi_assets/fallback.png")
