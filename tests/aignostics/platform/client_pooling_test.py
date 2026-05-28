"""Tests for API client connection pooling."""

import pytest
from aignostics_sdk.platform._client import Client


@pytest.mark.unit
def test_api_client_cached_is_shared() -> None:
    """Test that get_api_client with cache_token=True returns the same instance.

    This ensures connection pooling is shared across all Client instances using cached tokens.
    """
    # Get API client with cached token
    api1 = Client.get_api_client(cache_token=True)
    api2 = Client.get_api_client(cache_token=True)

    # Verify both calls return the same instance
    assert api1 is api2, "get_api_client(cache_token=True) should return the same instance"


@pytest.mark.unit
def test_api_client_uncached_is_shared() -> None:
    """Test that get_api_client with cache_token=False returns the same instance.

    This ensures connection pooling is shared across all Client instances using uncached tokens.
    """
    # Get API client with uncached token
    api1 = Client.get_api_client(cache_token=False)
    api2 = Client.get_api_client(cache_token=False)

    # Verify both calls return the same instance
    assert api1 is api2, "get_api_client(cache_token=False) should return the same instance"


@pytest.mark.unit
def test_api_client_cached_vs_uncached_are_different() -> None:
    """Test that cached and uncached API clients are separate instances.

    This ensures that cached and uncached token workflows don't interfere with each other.
    """
    # Get both types of API clients
    cached_api = Client.get_api_client(cache_token=True)
    uncached_api = Client.get_api_client(cache_token=False)

    # Verify they are different instances
    assert cached_api is not uncached_api, "Cached and uncached API clients should be different instances"


@pytest.mark.unit
def test_client_instances_share_api_client() -> None:
    """Test that multiple Client instances share the same underlying API client.

    This ensures efficient connection pooling across the entire application.
    """
    # Create multiple Client instances with cached tokens
    client1 = Client(cache_token=True)
    client2 = Client(cache_token=True)

    # Verify they use the same underlying API client
    assert client1._api is client2._api, "Client instances with cache_token=True should share the same API client"

    # Create Client instances with uncached tokens
    client3 = Client(cache_token=False)
    client4 = Client(cache_token=False)

    # Verify they use the same underlying API client
    assert client3._api is client4._api, "Client instances with cache_token=False should share the same API client"

    # Verify cached and uncached clients use different API clients
    assert client1._api is not client3._api, "Cached and uncached Client instances should use different API clients"
