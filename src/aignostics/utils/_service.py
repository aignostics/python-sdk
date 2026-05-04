"""Base class for services."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from typing import Any, ClassVar, Self, TypeVar, cast

from pydantic_settings import BaseSettings

from ._health import Health
from ._settings import load_settings

T = TypeVar("T", bound=BaseSettings)


class BaseService(ABC):
    """Base class for services."""

    _settings: BaseSettings
    _cached_dependency: ClassVar[Callable[[], Generator[Any]] | None] = None

    def __init__(self, settings_class: type[T] | None = None) -> None:
        """
        Initialize service with optional settings.

        Args:
            settings_class: Optional settings class to load configuration.
        """
        if settings_class is not None:
            self._settings = load_settings(settings_class)

    @classmethod
    def get_service(cls) -> Callable[[], Generator[Self]]:
        """Create a FastAPI dependency that yields an instance of this service.

        This is a factory method that returns a cached dependency function suitable
        for use with FastAPI's Depends(). It eliminates boilerplate code by providing
        a standard pattern for service injection.

        The dependency function is cached per-class to ensure the same function object
        is returned each time, which is necessary for FastAPI's dependency_overrides
        to work correctly in tests.

        Returns:
            Callable: A dependency function that yields the service instance.

        Example:
            ```python
            from aignostics.my_module._service import Service


            @router.get("/endpoint")
            async def endpoint(service: Annotated[Service, Depends(Service.get_service())]):
                return await service.do_something()
            ```
        """
        # Check if this specific class already has a cached dependency.
        # We use a class-specific cache key to avoid inheritance issues.
        cache_attr = f"_cached_dependency_{cls.__name__}"
        cached = getattr(cls, cache_attr, None)
        if cached is not None:
            return cast("Callable[[], Generator[Self]]", cached)

        def dependency() -> Generator[Self]:
            yield cls()

        setattr(cls, cache_attr, dependency)
        return dependency

    def key(self) -> str:
        """Return the module name of the instance."""
        return self.__module__.split(".")[-2]

    @abstractmethod
    async def health(self) -> Health:
        """Get health of this service. Override in subclass.

        Returns:
            Health: Health status of the service.
        """

    @abstractmethod
    async def info(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Get info of this service. Override in subclass.

        Args:
            mask_secrets: Whether to mask sensitive information in the output.

        Returns:
            dict[str, Any]: Information about the service.
        """

    def settings(self) -> BaseSettings:
        """Get the settings of this service.

        Returns:
            BaseSettings: The settings of the service.
        """
        return self._settings
