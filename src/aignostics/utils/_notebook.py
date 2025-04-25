"""Notebook server utilities."""

from collections.abc import Callable
from typing import Any

from ..constants import NOTEBOOK_APP, NOTEBOOK_FOLDER  # noqa: TID252
from ._health import Health
from ._log import get_logger

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


def create_marimo_app() -> Any:  # noqa: ANN401
    """Create a FastAPI app with marimo notebook server.

    Returns:
        FastAPI: FastAPI app with marimo notebook server.

    Raises:
        ValueError: If the notebook directory does not exist.
    """
    # Import dependencies only when function is called
    import marimo  # noqa: PLC0415
    from fastapi import APIRouter, FastAPI  # noqa: PLC0415

    server = marimo.create_asgi_app(include_code=True)
    if not NOTEBOOK_FOLDER.is_dir():
        logger.critical(
            "Directory %s does not exist. Please create the directory and add your notebooks.",
            NOTEBOOK_FOLDER,
        )
        message = f"Directory {NOTEBOOK_FOLDER} does not exist. Please create and add your notebooks."
        raise ValueError(message)
    server = server.with_app(path="/", root=str(NOTEBOOK_APP))
    #            .with_dynamic_directory(path="/dashboard", directory=str(self._settings.directory))
    app = FastAPI()
    router = APIRouter(tags=["marimo"])
    register_health_endpoint(router)
    app.include_router(router)
    app.mount("/", server.build())
    return app
