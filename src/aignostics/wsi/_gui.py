"""WSI API."""

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
            """Serve a thumbnail for a given source reference.

            Args:
                source (str): The source of the slide pointing to a file on the filesystem.

            Returns:
                fastapi.Response: HTTP response containing the thumbnail image.

            Raises:
                HTTPException: If the file does not exist or if thumbnail generation fails.
            """
            try:
                return Response(content=Service().get_thumbnail_bytes(Path(source)), media_type="image/png")
            except ValueError as e:
                logger.warning("Error generating thumbnail on bad request or invalid image input")
                raise HTTPException(status_code=400, detail=f"Bad request or invalid image input: {e!s}") from e
            except RuntimeError as e:
                logger.exception("Internal server error when generating thumbnail")
                raise HTTPException(
                    status_code=500, detail=f"Internal server error when generating thumbnail: {e!s}"
                ) from e

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
                return Response(content=Service().get_tiff_as_jpg(url), media_type="image/jpeg")
            except ValueError as e:
                logger.warning("Error generating jpeg on bad request or invalid tiff input")
                raise HTTPException(status_code=400, detail=f"Bad request or invalid tiff input: {e!s}") from e
            except RuntimeError as e:
                logger.exception("Internal server error when generating jpeg")
                raise HTTPException(status_code=500, detail=f"Internal server error when generating jpeg: {e!s}") from e
