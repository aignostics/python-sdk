"""Thumbnail API."""

from pathlib import Path

from fastapi import HTTPException, Response

from aignostics.utils import BasePageBuilder, get_logger

from ._service import Service

logger = get_logger(__name__)


class PageBuilder(BasePageBuilder):
    @staticmethod
    def register_pages() -> None:
        from nicegui import app  # noqa: PLC0415

        @app.get("/thumbnail")
        def thumbnail(source: str) -> Response:
            """Serve a thumbnail for a given reference.

            Args:
                source (str): The source of the slide.

            Returns:
                fastapi.Response: HTTP response containing the thumbnail image.

            Raises:
                HTTPException: If the file does not exist or if thumbnail generation fails.
            """
            try:
                return Response(content=Service().get_thumbnail_bytes(Path(source)), media_type="image/png")
            except Exception as e:
                logger.exception("Error generating thumbnail")
                raise HTTPException(status_code=500, detail=f"Error generating thumbnail: {e!s}") from e

        @app.get("/tiff")
        def tiff(url: str) -> Response:
            """Serve a tiff as jpg.

            Args:
                url (str): The URL of the tiff.

            Returns:
                fastapi.Response: HTTP response containing the thumbnail image.

            Raises:
                HTTPException: If the file does not exist or if thumbnail generation fails.
            """
            try:
                return Response(content=Service().get_tiff_as_jpg(url), media_type="application/jpg")
            except Exception as e:
                logger.exception("Error generating thumbnail")
                raise HTTPException(status_code=500, detail=f"Error generating jpg: {e!s}") from e
