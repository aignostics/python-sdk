"""WSI API."""

from pathlib import Path

from fastapi import Response
from fastapi.responses import RedirectResponse

from aignostics.utils import BasePageBuilder, get_logger

from ._service import Service

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app  # noqa: PLC0415

        app.add_static_files("/wsi_assets", Path(__file__).parent / "assets")

        @app.get("/thumbnail")
        def thumbnail(source: str) -> Response:
            """Serve a thumbnail for a given source reference.

            Args:
                source (str): The source of the slide pointing to a file on the filesystem.

            Returns:
                fastapi.Response: HTTP response containing the thumbnail or fallback image.
            """
            try:
                return Response(content=Service().get_thumbnail_bytes(Path(source)), media_type="image/png")
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
