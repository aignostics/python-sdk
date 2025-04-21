"""System service."""

from collections.abc import Callable

import marimo
from fastapi import APIRouter, FastAPI

from ..constants import NOTEBOOK_APP, NOTEBOOK_FOLDER  # noqa: TID252
from ._health import Health
from ._log import get_logger

logger = get_logger(__name__)


def register_health_endpoint(router: APIRouter) -> Callable[..., Health]:
    """Register health endpoint to the given router.

    Args:
        router: The router to register the health endpoint to.

    Returns:
        Callable[..., Health]: The health endpoint function.
    """

    @router.get("/healthz")
    def health_endpoint() -> Health:
        """Determine health of the app.

        Returns:
            Health: Health.
        """
        return Health(status=Health.Code.UP)

    return health_endpoint


def create_marimo_app() -> FastAPI:
    """Create a FastAPI app with marimo notebook server.

    Returns:
        FastAPI: FastAPI app with marimo notebook server.

    Raises:
        ValueError: If the notebook directory does not exist.
    """
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
