"""Base class for services."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic_settings import BaseSettings

from ._health import Health
from ._settings import load_settings

T = TypeVar("T", bound=BaseSettings)


class BaseService(ABC):
    """Base class for services."""

    _settings: BaseSettings

    def __init__(self, settings_class: type[T] | None = None) -> None:
        """
        Initialize service with optional settings.

        Args:
            settings_class: Optional settings class to load configuration.
        """
        if settings_class is not None:
            self._settings = load_settings(settings_class)

    def key(self) -> str:
        """Return the module name of the instance."""
        return self.__module__.split(".")[-2]

    @abstractmethod
    def health(self) -> Health:
        """Get health of this service. Override in subclass."""

    @abstractmethod
    def info(self) -> dict[str, Any]:
        """Get info of this service. Override in subclass."""
