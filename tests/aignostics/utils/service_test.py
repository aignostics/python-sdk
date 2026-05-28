"""Tests for BaseService.get_service() and settings() methods."""

import inspect
from typing import Any

import pytest

from aignostics_sdk.utils._health import Health
from aignostics_sdk.utils._service import BaseService


class _ConcreteService(BaseService):
    """Minimal concrete service for testing BaseService behaviour."""

    async def health(self) -> Health:  # noqa: PLR6301
        return Health(status=Health.Code.UP)

    async def info(self, mask_secrets: bool = True) -> dict[str, Any]:  # noqa: PLR6301
        return {}


class _AnotherConcreteService(BaseService):
    """A second concrete service to test per-class caching."""

    async def health(self) -> Health:  # noqa: PLR6301
        return Health(status=Health.Code.UP)

    async def info(self, mask_secrets: bool = True) -> dict[str, Any]:  # noqa: PLR6301
        return {}


@pytest.fixture(autouse=True)
def _clear_cached_dependencies() -> None:
    """Remove any cached dependency attributes between tests."""
    for cls in (_ConcreteService, _AnotherConcreteService):
        cache_attr = f"_cached_dependency_{cls.__name__}"
        if hasattr(cls, cache_attr):
            delattr(cls, cache_attr)


@pytest.mark.unit
def test_get_service_returns_callable(record_property) -> None:
    """get_service() returns a callable dependency factory."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    dep = _ConcreteService.get_service()
    assert callable(dep)


@pytest.mark.unit
def test_get_service_caching_returns_same_object(record_property) -> None:
    """Calling get_service() twice on the same class returns the identical function.

    FastAPI's dependency_overrides keying relies on object identity.
    """
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    dep1 = _ConcreteService.get_service()
    dep2 = _ConcreteService.get_service()
    assert dep1 is dep2


@pytest.mark.unit
def test_get_service_caching_is_per_class(record_property) -> None:
    """Two different subclasses receive different dependency functions."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    dep_a = _ConcreteService.get_service()
    dep_b = _AnotherConcreteService.get_service()
    assert dep_a is not dep_b


@pytest.mark.unit
def test_get_service_dependency_yields_instance(record_property) -> None:
    """Exhausting the dependency generator yields an instance of the service class."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    dep = _ConcreteService.get_service()
    gen = dep()
    instance = next(gen)
    assert isinstance(instance, _ConcreteService)


@pytest.mark.unit
def test_settings_accessor_returns_settings(record_property) -> None:
    """settings() returns the _settings object set during __init__."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    from pydantic_settings import BaseSettings as _BaseSettings

    class _MinimalSettings(_BaseSettings):
        pass

    class _ServiceWithSettings(BaseService):
        def __init__(self) -> None:
            super().__init__(_MinimalSettings)

        async def health(self) -> Health:  # noqa: PLR6301
            return Health(status=Health.Code.UP)

        async def info(self, mask_secrets: bool = True) -> dict[str, Any]:  # noqa: PLR6301
            return {}

    svc = _ServiceWithSettings()
    result = svc.settings()
    assert isinstance(result, _MinimalSettings)
    assert result is svc._settings


@pytest.mark.unit
def test_health_is_coroutine(record_property) -> None:
    """health() returns a coroutine when called."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    coro = _ConcreteService().health()
    assert inspect.iscoroutine(coro)
    coro.close()


@pytest.mark.unit
def test_info_is_coroutine(record_property) -> None:
    """info() returns a coroutine when called."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    coro = _ConcreteService().info()
    assert inspect.iscoroutine(coro)
    coro.close()
