"""Notebook server utilities."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ._health import Health
from ._log import get_logger
from ._fs import get_user_data_directory
import shutil

logger = get_logger(__name__)


def register_health_endpoint(router: Any) -> Callable[..., Health]:  # noqa: ANN401
    """Register health endpoint to the given router.

    Args:
        router: The router to register the health endpoint to.

    Returns:
        Callable[..., Health]: The health endpoint function.
    """
    # We accept 'Any' instead of APIRouter to avoid importing fastapi at module level

    @router.get("/healthz")
    def health_endpoint() -> Health:
        """Determine health of the app.

        Returns:
            Health: Health.
        """
        return Health(status=Health.Code.UP)

    # Explicitly type the return value to satisfy mypy
    result: Callable[..., Health] = health_endpoint
    return result


def create_marimo_app(notebook: Path, override_if_exists: bool) -> Any:  # noqa: ANN401
    """Create a FastAPI app with marimo notebook server.

    Args:
        notebook (Path): Path to the notebook. Notebook will be copied into the user data directory.
        override_if_exists (bool): Whether to override the notebook in the user data directory if it already exists.

    Returns:
        FastAPI: FastAPI app with marimo notebook server.

    Raises:
        ValueError: If the notebook directory does not exist.
    """
    # Import dependencies only when function is called
    import marimo  # noqa: PLC0415
    from fastapi import APIRouter, FastAPI  # noqa: PLC0415

    server = marimo.create_asgi_app(include_code=True)
    directory = get_user_data_directory("notebooks")
    notebook_destination = directory / notebook.name
    if notebook_destination.exists() and not override_if_exists:
        logger.debug(f"Notebook already exists at {notebook_destination}, using existing file")
    else:
        notebook_destination.write_bytes(notebook.read_bytes())
        logger.info(f"Copied notebook from {notebook} to {notebook_destination}")
    server = server.with_app(path="/", root=str(notebook_destination.resolve()))
    app = FastAPI()
    router = APIRouter(tags=["marimo"])
    register_health_endpoint(router)
    app.include_router(router)
    app.mount("/", server.build())
    return app
