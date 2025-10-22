"""Tests for authentication-aware caching in Client class.

This module tests the caching mechanism that:
1. Caches operation results based on authentication token
2. Respects TTL (time-to-live) for cached values
3. Invalidates cache when token changes
4. Properly handles cache keys with different method arguments
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from aignostics.platform._client import Client
from aignostics.platform._operation_cache import _operation_cache, cache_key_with_token


class TestCacheKeyGeneration:
    """Test cases for cache key generation."""

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_includes_token_hash() -> None:
        """Test that cache key includes a hash of the token.

        This ensures different tokens produce different cache keys.
        """
        key1 = cache_key_with_token("token-123", "method_name")
        key2 = cache_key_with_token("token-456", "method_name")

        assert key1 != key2
        assert ":" in key1
        assert ":" in key2

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_includes_method_name() -> None:
        """Test that cache key includes the method name.

        This ensures different methods produce different cache keys even with same token.
        """
        key1 = cache_key_with_token("token-123", "method_a")
        key2 = cache_key_with_token("token-123", "method_b")

        assert key1 != key2
        assert "method_a" in key1
        assert "method_b" in key2

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_includes_args() -> None:
        """Test that cache key includes positional arguments.

        This ensures different args produce different cache keys.
        """
        key1 = cache_key_with_token("token-123", "method", "arg1", "arg2")
        key2 = cache_key_with_token("token-123", "method", "arg1", "arg3")

        assert key1 != key2

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_includes_kwargs() -> None:
        """Test that cache key includes keyword arguments.

        This ensures different kwargs produce different cache keys.
        """
        key1 = cache_key_with_token("token-123", "method", param1="value1")
        key2 = cache_key_with_token("token-123", "method", param1="value2")

        assert key1 != key2

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_consistent_for_same_inputs() -> None:
        """Test that cache key is consistent for identical inputs.

        This ensures the cache can find previously stored values.
        """
        key1 = cache_key_with_token("token-123", "method", "arg1", param1="value1")
        key2 = cache_key_with_token("token-123", "method", "arg1", param1="value1")

        assert key1 == key2

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_handles_empty_token() -> None:
        """Test that cache key handles empty or None token gracefully."""
        key1 = cache_key_with_token("", "method")
        key2 = cache_key_with_token("", "method")

        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) > 0

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_kwargs_order_independent() -> None:
        """Test that cache key is independent of kwargs order.

        Since kwargs are sorted in the cache key generation, the order should not matter.
        """
        key1 = cache_key_with_token("token-123", "method", a=1, b=2, c=3)
        key2 = cache_key_with_token("token-123", "method", c=3, a=1, b=2)

        assert key1 == key2


class TestCacheBasicFunctionality:
    """Test cases for basic cache functionality."""

    @pytest.mark.unit
    @staticmethod
    def test_me_caches_result_on_first_call(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that me() caches the result on first call.

        The second call should return the cached value without calling the API.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call - should hit API
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second call - should use cache
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1  # Still 1, not 2

        # Results should be identical
        assert result1 == result2

    @pytest.mark.unit
    @staticmethod
    def test_cache_stores_value_in_operation_cache(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cached values are stored in _operation_cache.

        Verify the cache structure and that values are properly stored.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # Initially cache should be empty
        assert len(_operation_cache) == 0

        # Call me()
        client_with_mock_api.me()

        # Cache should now have one entry
        assert len(_operation_cache) == 1

        # Verify cache structure: key -> (value, expiry_timestamp)
        cache_entry = next(iter(_operation_cache.values()))
        assert isinstance(cache_entry, tuple)
        assert len(cache_entry) == 2
        assert cache_entry[0] == mock_me_response
        assert isinstance(cache_entry[1], float)
        assert cache_entry[1] > time.time()  # Expiry should be in the future

    @pytest.mark.unit
    @staticmethod
    def test_cache_returns_none_when_api_returns_none(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache properly handles and returns None values.

        None is a valid API response and should be cached like any other value.
        """
        mock_api_client.get_me_v1_me_get.return_value = None

        # First call
        result1 = client_with_mock_api.me()
        assert result1 is None
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second call should use cache
        result2 = client_with_mock_api.me()
        assert result2 is None
        assert mock_api_client.get_me_v1_me_get.call_count == 1  # Still 1


class TestCacheTTL:
    """Test cases for cache TTL (time-to-live) functionality."""

    @pytest.mark.unit
    @staticmethod
    def test_cache_expires_after_ttl(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache expires after the configured TTL.

        The me() method uses ttl=60, so after 60 seconds the cache should expire.
        """
        mock_me_response_1 = {"user_id": "test-user-1", "org_id": "test-org-1"}
        mock_me_response_2 = {"user_id": "test-user-2", "org_id": "test-org-2"}

        # First call
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response_1
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second call immediately - should use cache
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response_1
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Manually expire the cache by setting expiry to the past
        cache_key = next(iter(_operation_cache.keys()))
        value, _ = _operation_cache[cache_key]
        _operation_cache[cache_key] = (value, time.time() - 1)  # Set expiry to 1 second ago

        # Third call after expiry - should hit API again
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2
        result3 = client_with_mock_api.me()
        assert result3 == mock_me_response_2
        assert mock_api_client.get_me_v1_me_get.call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_expired_cache_entry_removed(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that expired cache entries are removed when accessed.

        When an expired entry is accessed, it should be removed from the cache.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call - creates cache entry
        client_with_mock_api.me()
        assert len(_operation_cache) == 1

        # Expire the cache entry
        cache_key = next(iter(_operation_cache.keys()))
        value, _ = _operation_cache[cache_key]
        _operation_cache[cache_key] = (value, time.time() - 1)

        # Second call - should remove expired entry and create new one
        client_with_mock_api.me()
        assert len(_operation_cache) == 1

        # The new entry should not be expired
        cache_entry = _operation_cache[cache_key]
        assert cache_entry[1] > time.time()

    @pytest.mark.unit
    @staticmethod
    def test_cache_ttl_is_60_seconds_for_me(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that the me() method uses a 60-second TTL.

        Verify that the cache entry expires around 60 seconds from creation.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        current_time = time.time()
        client_with_mock_api.me()

        # Get the cache entry
        cache_entry = next(iter(_operation_cache.values()))
        expiry_time = cache_entry[1]

        # Expiry should be approximately 60 seconds in the future
        time_to_expiry = expiry_time - current_time
        assert 59 <= time_to_expiry <= 61, f"Expected TTL ~60s, got {time_to_expiry:.2f}s"


class TestCacheWithDifferentTokens:
    """Test cases for cache behavior with different authentication tokens."""

    @pytest.mark.unit
    @staticmethod
    def test_different_tokens_use_different_cache_entries(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that different tokens create separate cache entries.

        Each token should have its own cached values.
        """
        mock_me_response_1 = {"user_id": "user-1", "org_id": "org-1"}
        mock_me_response_2 = {"user_id": "user-2", "org_id": "org-2"}

        # Client with token-1
        with (
            patch("aignostics.platform._operation_cache.get_token", return_value="token-1"),
            patch("aignostics.platform._client.get_token", return_value="token-1"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            client1 = Client(cache_token=False)
            client1._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1

            result1 = client1.me()
            assert result1 == mock_me_response_1
            assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Client with token-2
        with (
            patch("aignostics.platform._operation_cache.get_token", return_value="token-2"),
            patch("aignostics.platform._client.get_token", return_value="token-2"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            client2 = Client(cache_token=False)
            client2._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

            result2 = client2.me()
            assert result2 == mock_me_response_2
            assert mock_api_client.get_me_v1_me_get.call_count == 2  # New API call

        # Cache should have two entries
        assert len(_operation_cache) == 2

    @pytest.mark.unit
    @staticmethod
    def test_token_change_invalidates_cache(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that changing token invalidates the cache.

        When the authentication token changes, cached values should not be used.
        """
        mock_me_response_1 = {"user_id": "user-1", "org_id": "org-1"}
        mock_me_response_2 = {"user_id": "user-2", "org_id": "org-2"}

        # First call with token-1
        with (
            patch("aignostics.platform._operation_cache.get_token") as mock_get_token,
            patch("aignostics.platform._client.get_token", return_value="token-1"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            mock_get_token.return_value = "token-1"
            client = Client(cache_token=False)
            client._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1

            result1 = client.me()
            assert result1 == mock_me_response_1
            assert mock_api_client.get_me_v1_me_get.call_count == 1

            # Second call with token-2 (simulating token refresh)
            mock_get_token.return_value = "token-2"
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

            result2 = client.me()
            assert result2 == mock_me_response_2
            assert mock_api_client.get_me_v1_me_get.call_count == 2  # New API call, cache not used

    @pytest.mark.unit
    @staticmethod
    def test_same_token_reuses_cache(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that using the same token reuses cached values.

        Multiple clients with the same token should share cached values.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        # First client with token-123
        with (
            patch("aignostics.platform._operation_cache.get_token", return_value="token-123"),
            patch("aignostics.platform._client.get_token", return_value="token-123"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            client1 = Client(cache_token=False)
            client1._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response

            result1 = client1.me()
            assert result1 == mock_me_response
            assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second client with same token-123
        with (
            patch("aignostics.platform._operation_cache.get_token", return_value="token-123"),
            patch("aignostics.platform._client.get_token", return_value="token-123"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            client2 = Client(cache_token=False)
            client2._api = mock_api_client

            result2 = client2.me()
            assert result2 == mock_me_response
            assert mock_api_client.get_me_v1_me_get.call_count == 1  # Still 1, used cache

        # Results should be identical
        assert result1 == result2


class TestCacheWithRetries:
    """Test cases for cache interaction with retry mechanism."""

    @pytest.mark.unit
    @staticmethod
    def test_cache_not_populated_on_failure(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache is not populated when API call fails.

        Failed calls should not be cached.
        """
        from http import HTTPStatus

        from aignx.codegen.exceptions import ServiceException

        # First call fails
        def side_effect(*args, **kwargs):
            raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")

        mock_api_client.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(ServiceException):
            client_with_mock_api.me()

        # Cache should be empty after failed call
        assert len(_operation_cache) == 0

    @pytest.mark.unit
    @staticmethod
    def test_exceptions_not_cached_subsequent_call_retries(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that exceptions are not cached and subsequent calls retry the API.

        When an API call fails completely (exhausts all retries), the failure should not
        be cached. A subsequent call should attempt the API call again, not return a
        cached exception.
        """
        from http import HTTPStatus

        from aignx.codegen.exceptions import ServiceException

        call_count = 0
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                # First three calls (first me() attempt with retries) fail
                raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")
            # Fourth call onwards succeed
            return mock_me_response

        mock_api_client.get_me_v1_me_get.side_effect = side_effect

        # First call fails after exhausting all retries (3 attempts)
        with pytest.raises(ServiceException):
            client_with_mock_api.me()

        assert call_count == 3  # Should have tried 3 times (max attempts)
        assert len(_operation_cache) == 0  # No cache entry for failures

        # Second call should retry the API (not use cached exception) and succeed
        result = client_with_mock_api.me()
        assert result == mock_me_response
        assert call_count == 4  # API was called again (one more attempt, which succeeded)

        # Third call should use cache from successful second call
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response
        assert call_count == 4  # Still 4, used cache

    @pytest.mark.unit
    @staticmethod
    def test_cache_populated_after_successful_retry(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache is populated after a successful retry.

        If the call eventually succeeds after retries, the result should be cached.
        """
        from urllib3.exceptions import TimeoutError as Urllib3TimeoutError

        call_count = 0
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                time.sleep(0.5)
                msg = "Timeout"
                raise Urllib3TimeoutError(msg)
            return mock_me_response

        mock_api_client.get_me_v1_me_get.side_effect = side_effect

        # First call succeeds after retry
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response
        assert call_count == 2

        # Second call should use cache
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response
        assert call_count == 2  # Still 2, used cache

    @pytest.mark.unit
    @staticmethod
    def test_cache_used_before_retry_logic(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache is checked before retry logic is invoked.

        If a cached value exists, the retry logic should not be executed at all.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call - populates cache
        client_with_mock_api.me()
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Configure API to fail on subsequent calls
        from http import HTTPStatus

        from aignx.codegen.exceptions import ServiceException

        mock_api_client.get_me_v1_me_get.side_effect = ServiceException(
            status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error"
        )

        # Second call should return cached value without triggering the error
        result = client_with_mock_api.me()
        assert result == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1  # Still 1, error never called


class TestCacheConcurrency:
    """Test cases for cache behavior in concurrent scenarios."""

    @pytest.mark.unit
    @staticmethod
    def test_cache_is_class_level(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that cache is shared across all Client instances.

        The _operation_cache should be a class variable, not an instance variable.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        with (
            patch("aignostics.platform._operation_cache.get_token", return_value="token-123"),
            patch("aignostics.platform._client.get_token", return_value="token-123"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            # Create first client and call me()
            client1 = Client(cache_token=False)
            client1._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response

            client1.me()
            assert mock_api_client.get_me_v1_me_get.call_count == 1

            # Create second client with same token
            client2 = Client(cache_token=False)
            client2._api = mock_api_client

            # Second client should use cached value
            result = client2.me()
            assert result == mock_me_response
            assert mock_api_client.get_me_v1_me_get.call_count == 1  # Still 1

    @pytest.mark.unit
    @staticmethod
    def test_cache_cleared_affects_all_clients(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that clearing cache affects all Client instances.

        Since cache is class-level, clearing it should affect all instances.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        with (
            patch("aignostics.platform._operation_cache.get_token", return_value="token-123"),
            patch("aignostics.platform._client.get_token", return_value="token-123"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            client1 = Client(cache_token=False)
            client1._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response

            # Populate cache with client1
            client1.me()
            assert len(_operation_cache) == 1

            # Clear cache
            _operation_cache.clear()
            assert len(_operation_cache) == 0

            # client2 should not find cached value
            client2 = Client(cache_token=False)
            client2._api = mock_api_client

            client2.me()
            assert mock_api_client.get_me_v1_me_get.call_count == 2  # New call


class TestCacheEdgeCases:
    """Test cases for edge cases and unusual scenarios."""

    @pytest.mark.unit
    @staticmethod
    def test_cache_handles_complex_response_objects(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache handles complex nested response objects.

        The cache should be able to store and retrieve complex data structures.
        """
        mock_me_response = {
            "user_id": "test-user",
            "org_id": "test-org",
            "metadata": {"role": "admin", "permissions": ["read", "write"]},
            "nested": {"deep": {"value": 123}},
        }
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response

        # Second call should return identical structure
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response
        assert result1 == result2

    @pytest.mark.unit
    @staticmethod
    def test_cache_handles_empty_dict(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that cache properly handles empty dict responses."""
        mock_api_client.get_me_v1_me_get.return_value = {}

        result1 = client_with_mock_api.me()
        assert result1 == {}

        result2 = client_with_mock_api.me()
        assert result2 == {}
        assert mock_api_client.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_cache_with_rapid_successive_calls(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test cache behavior with rapid successive calls.

        Multiple rapid calls should all use the same cached value.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # Make 10 rapid calls
        results = [client_with_mock_api.me() for _ in range(10)]

        # All should return the same value
        assert all(r == mock_me_response for r in results)

        # API should only be called once
        assert mock_api_client.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_cache_key_with_unicode_args(mock_settings: MagicMock) -> None:
        """Test that cache key generation handles unicode characters correctly."""
        key1 = cache_key_with_token("token-123", "method", "arg-ü-ö-ä", param="value-é-ñ")
        key2 = cache_key_with_token("token-123", "method", "arg-ü-ö-ä", param="value-é-ñ")

        # Should be consistent
        assert key1 == key2
        assert isinstance(key1, str)

    @pytest.mark.unit
    @staticmethod
    def test_cache_with_very_long_token(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that cache handles very long authentication tokens.

        Cache key should hash long tokens to keep key size manageable.
        """
        long_token = "x" * 10000  # Very long token

        with (
            patch("aignostics.platform._operation_cache.get_token", return_value=long_token),
            patch("aignostics.platform._client.get_token", return_value=long_token),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            client = Client(cache_token=False)
            client._api = mock_api_client
            mock_api_client.get_me_v1_me_get.return_value = {"user_id": "test"}

            client.me()

            # Cache key should be reasonable length (token is hashed)
            cache_key = next(iter(_operation_cache.keys()))
            assert len(cache_key) < 200  # Much shorter than the 10000 char token


class TestCacheIntegrationWithAuthentication:
    """Test cases for cache integration with authentication system."""

    @pytest.mark.unit
    @staticmethod
    def test_cache_uses_current_token_from_get_token(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test that cache always uses the current token from get_token().

        The cache should call get_token() on each operation to get the current token.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        with (
            patch("aignostics.platform._operation_cache.get_token") as mock_get_token,
            patch("aignostics.platform._client.get_token", return_value="token-1"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            mock_get_token.return_value = "token-1"
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response

            client = Client(cache_token=False)
            client._api = mock_api_client

            # First call with token-1
            client.me()
            assert mock_get_token.call_count >= 1

            # Change token
            mock_get_token.return_value = "token-2"
            mock_me_response_2 = {"user_id": "test-user-2", "org_id": "test-org-2"}
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

            # Second call should detect new token and not use cache
            result = client.me()
            assert result == mock_me_response_2
            assert mock_api_client.get_me_v1_me_get.call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_cache_with_token_refresh_scenario(mock_settings: MagicMock, mock_api_client: MagicMock) -> None:
        """Test cache behavior in a token refresh scenario.

        This simulates a common scenario where the token is refreshed mid-session.
        """
        mock_me_response_1 = {"user_id": "user-1", "org_id": "org-1"}
        mock_me_response_2 = {"user_id": "user-2", "org_id": "org-2"}

        with (
            patch("aignostics.platform._operation_cache.get_token") as mock_get_token,
            patch("aignostics.platform._client.get_token", return_value="token-initial"),
            patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
        ):
            # Initial token
            mock_get_token.return_value = "token-initial"
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1

            client = Client(cache_token=False)
            client._api = mock_api_client

            # Call 1: Populates cache with token-initial
            result1 = client.me()
            assert result1 == mock_me_response_1
            assert mock_api_client.get_me_v1_me_get.call_count == 1

            # Call 2: Uses cached value with token-initial
            result2 = client.me()
            assert result2 == mock_me_response_1
            assert mock_api_client.get_me_v1_me_get.call_count == 1

            # Token refresh happens
            mock_get_token.return_value = "token-refreshed"
            mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

            # Call 3: New token means cache miss, fetches new data
            result3 = client.me()
            assert result3 == mock_me_response_2
            assert mock_api_client.get_me_v1_me_get.call_count == 2

            # Call 4: Uses cached value with token-refreshed
            result4 = client.me()
            assert result4 == mock_me_response_2
            assert mock_api_client.get_me_v1_me_get.call_count == 2

            # Should now have 2 cache entries (one for each token)
            assert len(_operation_cache) == 2
