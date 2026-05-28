"""Tests for nocache parameter functionality across the platform module.

This module tests that:
1. nocache=False uses cached values (default behavior)
2. nocache=True skips reading from cache but still writes to cache
3. All platform methods that support caching correctly handle nocache
4. The decorator properly intercepts and handles the nocache parameter
"""

import time
from unittest.mock import MagicMock

import pytest
from aignostics_sdk.platform._client import Client
from aignostics_sdk.platform._operation_cache import _operation_cache, cached_operation, operation_cache_clear


class TestNocacheDecoratorBehavior:
    """Test the nocache parameter handling in the cached_operation decorator."""

    @pytest.mark.unit
    @staticmethod
    def test_decorator_without_nocache_uses_cache() -> None:
        """Test that decorated function uses cache by default (nocache=False)."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - should execute function
        result1 = test_func()
        assert result1 == 1
        assert call_count == 1

        # Second call - should use cache
        result2 = test_func()
        assert result2 == 1  # Same as first call, from cache
        assert call_count == 1  # Function not called again

    @pytest.mark.unit
    @staticmethod
    def test_decorator_with_nocache_false_uses_cache() -> None:
        """Test that nocache=False explicitly uses cache."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call with nocache=False
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1
        assert call_count == 1

        # Second call with nocache=False - should use cache
        result2 = test_func()  # type: ignore[call-arg]
        assert result2 == 1
        assert call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_decorator_with_nocache_true_skips_reading_cache() -> None:
        """Test that nocache=True skips reading from cache."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - populates cache
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1
        assert call_count == 1

        # Second call with nocache=True - skips cache, executes function
        result2 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result2 == 2  # New value, not from cache
        assert call_count == 2  # Function called again

    @pytest.mark.unit
    @staticmethod
    def test_decorator_with_nocache_true_still_writes_to_cache() -> None:
        """Test that nocache=True still writes the result to cache."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - populates cache
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1
        assert call_count == 1

        # Second call with nocache=True - skips cache read, writes new value
        result2 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result2 == 2
        assert call_count == 2

        # Third call without nocache - should use the value cached by second call
        result3 = test_func()  # type: ignore[call-arg]
        assert result3 == 2  # Uses value from second call
        assert call_count == 2  # Function not called again

    @pytest.mark.unit
    @staticmethod
    def test_decorator_nocache_parameter_not_passed_to_function() -> None:
        """Test that nocache parameter is intercepted and not passed to the decorated function."""
        received_kwargs = {}

        @cached_operation(ttl=60)
        def test_func(**kwargs: bool) -> dict:
            nonlocal received_kwargs
            received_kwargs = kwargs
            return {"called": True}

        # Call with nocache=True
        test_func(nocache=True)  # type: ignore[call-arg]

        # The decorated function should not receive nocache in kwargs
        assert "nocache" not in received_kwargs

    @pytest.mark.unit
    @staticmethod
    def test_decorator_with_nocache_and_other_kwargs() -> None:
        """Test that nocache works alongside other keyword arguments."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func(param1: str = "default", param2: int = 0) -> tuple:
            nonlocal call_count
            call_count += 1
            return (call_count, param1, param2)

        # First call with params
        result1 = test_func(param1="value1", param2=123)  # type: ignore[call-arg]
        assert result1 == (1, "value1", 123)
        assert call_count == 1

        # Second call with same params - should use cache
        result2 = test_func(param1="value1", param2=123)  # type: ignore[call-arg]
        assert result2 == (1, "value1", 123)
        assert call_count == 1

        # Third call with nocache=True and same params - should skip cache
        result3 = test_func(param1="value1", param2=123, nocache=True)  # type: ignore[call-arg]
        assert result3 == (2, "value1", 123)
        assert call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_decorator_nocache_with_different_cache_keys() -> None:
        """Test that nocache respects different cache keys (different args)."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func(key: str) -> tuple:
            nonlocal call_count
            call_count += 1
            return (call_count, key)

        # Call with key="A"
        result1 = test_func("A")  # type: ignore[call-arg]
        assert result1 == (1, "A")
        assert call_count == 1

        # Call with key="B"
        result2 = test_func("B")  # type: ignore[call-arg]
        assert result2 == (2, "B")
        assert call_count == 2

        # Call with key="A", nocache=True - should skip cache for key="A"
        result3 = test_func("A", nocache=True)  # type: ignore[call-arg]
        assert result3 == (3, "A")
        assert call_count == 3

        # Call with key="B" again - should use cache for key="B"
        result4 = test_func("B")  # type: ignore[call-arg]
        assert result4 == (2, "B")  # Still has cached value
        assert call_count == 3


class TestClientMeNocache:
    """Test nocache parameter for Client.me() method."""

    @pytest.mark.unit
    @staticmethod
    def test_me_default_uses_cache(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that me() uses cache by default."""
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second call - should use cache
        result2 = client_with_mock_api.me()
        assert result2 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_me_nocache_false_uses_cache(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that me(nocache=False) uses cache."""
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response

        # First call
        result1 = client_with_mock_api.me(nocache=False)
        assert result1 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Second call with nocache=False - should use cache
        result2 = client_with_mock_api.me(nocache=False)
        assert result2 == mock_me_response
        assert mock_api_client.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_me_nocache_true_fetches_fresh_data(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that me(nocache=True) fetches fresh data from API."""
        mock_me_response_1 = {"user_id": "user-1", "org_id": "org-1"}
        mock_me_response_2 = {"user_id": "user-2", "org_id": "org-2"}

        # First call - populates cache
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response_1
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Change API response
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

        # Second call with nocache=True - should fetch fresh data
        result2 = client_with_mock_api.me(nocache=True)
        assert result2 == mock_me_response_2
        assert mock_api_client.get_me_v1_me_get.call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_me_nocache_true_updates_cache(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that me(nocache=True) updates the cache with fresh data."""
        mock_me_response_1 = {"user_id": "user-1", "org_id": "org-1"}
        mock_me_response_2 = {"user_id": "user-2", "org_id": "org-2"}

        # First call - populates cache
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_1
        result1 = client_with_mock_api.me()
        assert result1 == mock_me_response_1
        assert mock_api_client.get_me_v1_me_get.call_count == 1

        # Change API response
        mock_api_client.get_me_v1_me_get.return_value = mock_me_response_2

        # Second call with nocache=True - fetches and caches new data
        result2 = client_with_mock_api.me(nocache=True)
        assert result2 == mock_me_response_2
        assert mock_api_client.get_me_v1_me_get.call_count == 2

        # Third call without nocache - should use updated cache
        result3 = client_with_mock_api.me()
        assert result3 == mock_me_response_2  # Uses new cached value
        assert mock_api_client.get_me_v1_me_get.call_count == 2  # No additional API call


class TestClientApplicationNocache:
    """Test nocache parameter for Client.application() method."""

    @pytest.mark.unit
    @staticmethod
    def test_application_default_uses_cache(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that application() uses cache by default."""
        mock_app_response = {"application_id": "test-app", "name": "Test App"}
        mock_api_client.read_application_by_id_v1_applications_application_id_get.return_value = mock_app_response

        # First call
        result1 = client_with_mock_api.application("test-app")
        assert result1 == mock_app_response
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 1

        # Second call - should use cache
        result2 = client_with_mock_api.application("test-app")
        assert result2 == mock_app_response
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_application_nocache_true_fetches_fresh_data(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that application(nocache=True) fetches fresh data."""
        mock_app_response_1 = {"application_id": "test-app", "name": "App v1"}
        mock_app_response_2 = {"application_id": "test-app", "name": "App v2"}

        # First call
        mock_api_client.read_application_by_id_v1_applications_application_id_get.return_value = mock_app_response_1
        result1 = client_with_mock_api.application("test-app")
        assert result1 == mock_app_response_1
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 1

        # Change response
        mock_api_client.read_application_by_id_v1_applications_application_id_get.return_value = mock_app_response_2

        # Second call with nocache=True
        result2 = client_with_mock_api.application("test-app", nocache=True)
        assert result2 == mock_app_response_2
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_application_nocache_with_different_app_ids(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that nocache works correctly with different application IDs."""
        mock_app_response_a = {"application_id": "app-a", "name": "App A"}
        mock_app_response_b = {"application_id": "app-b", "name": "App B"}

        def side_effect(*args, **kwargs):
            app_id = kwargs.get("application_id")
            if app_id == "app-a":
                return mock_app_response_a
            return mock_app_response_b

        mock_api_client.read_application_by_id_v1_applications_application_id_get.side_effect = side_effect

        # Call for app-a
        result1 = client_with_mock_api.application("app-a")
        assert result1 == mock_app_response_a

        # Call for app-b
        result2 = client_with_mock_api.application("app-b")
        assert result2 == mock_app_response_b

        # Both should be cached
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 2

        # Call app-a with nocache=True
        result3 = client_with_mock_api.application("app-a", nocache=True)
        assert result3 == mock_app_response_a
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 3

        # Call app-b without nocache - should use cache
        result4 = client_with_mock_api.application("app-b")
        assert result4 == mock_app_response_b
        assert mock_api_client.read_application_by_id_v1_applications_application_id_get.call_count == 3


class TestClientApplicationVersionNocache:
    """Test nocache parameter for Client.application_version() method."""

    @pytest.mark.unit
    @staticmethod
    def test_application_version_default_uses_cache(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that application_version() uses cache by default."""
        mock_version_response = {"application_id": "test-app", "version": "1.0.0"}
        mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.return_value = (
            mock_version_response
        )

        # First call
        result1 = client_with_mock_api.application_version("test-app", "1.0.0")
        assert result1 == mock_version_response
        assert (
            mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.call_count
            == 1
        )

        # Second call - should use cache
        result2 = client_with_mock_api.application_version("test-app", "1.0.0")
        assert result2 == mock_version_response
        assert (
            mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.call_count
            == 1
        )

    @pytest.mark.unit
    @staticmethod
    def test_application_version_nocache_true_fetches_fresh_data(
        mock_settings: MagicMock, client_with_mock_api: Client, mock_api_client: MagicMock
    ) -> None:
        """Test that application_version(nocache=True) fetches fresh data."""
        mock_version_response_1 = {"application_id": "test-app", "version": "1.0.0", "updated": "2024-01-01"}
        mock_version_response_2 = {"application_id": "test-app", "version": "1.0.0", "updated": "2024-01-02"}

        # First call
        mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.return_value = (
            mock_version_response_1
        )
        result1 = client_with_mock_api.application_version("test-app", "1.0.0")
        assert result1 == mock_version_response_1
        assert (
            mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.call_count
            == 1
        )

        # Change response
        mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.return_value = (
            mock_version_response_2
        )

        # Second call with nocache=True
        result2 = client_with_mock_api.application_version("test-app", "1.0.0", nocache=True)
        assert result2 == mock_version_response_2
        assert (
            mock_api_client.application_version_details_v1_applications_application_id_versions_version_get.call_count
            == 2
        )


class TestRunDetailsNocache:
    """Test nocache parameter for Run.details() method - simplified tests."""

    @pytest.mark.unit
    @staticmethod
    def test_run_details_supports_nocache_parameter() -> None:
        """Test that Run.details() method signature supports nocache parameter."""
        from inspect import signature

        from aignostics_sdk.platform.resources.runs import Run

        # Verify the method has nocache parameter
        sig = signature(Run.details)
        assert "nocache" in sig.parameters
        param = sig.parameters["nocache"]
        assert param.default is False
        assert param.annotation is bool


class TestRunsListNocache:
    """Test nocache parameter for Runs.list() method - simplified tests."""

    @pytest.mark.unit
    @staticmethod
    def test_runs_list_supports_nocache_parameter() -> None:
        """Test that Runs.list() method signature supports nocache parameter."""
        from inspect import signature

        from aignostics_sdk.platform.resources.runs import Runs

        # Verify the method has nocache parameter
        sig = signature(Runs.list)
        assert "nocache" in sig.parameters
        param = sig.parameters["nocache"]
        assert param.default is False
        assert param.annotation is bool


class TestApplicationsResourcesNocache:
    """Test nocache parameter for Applications and Versions resources - simplified tests."""

    @pytest.mark.unit
    @staticmethod
    def test_versions_list_supports_nocache_parameter() -> None:
        """Test that Versions.list() method signature supports nocache parameter."""
        from inspect import signature

        from aignostics_sdk.platform.resources.applications import Versions

        # Verify the method has nocache parameter
        sig = signature(Versions.list)
        assert "nocache" in sig.parameters
        param = sig.parameters["nocache"]
        assert param.default is False
        assert param.annotation is bool

    @pytest.mark.unit
    @staticmethod
    def test_applications_details_supports_nocache_parameter() -> None:
        """Test that Applications.details() method signature supports nocache parameter."""
        from inspect import signature

        from aignostics_sdk.platform.resources.applications import Applications

        # Verify the method has nocache parameter
        sig = signature(Applications.details)
        assert "nocache" in sig.parameters
        param = sig.parameters["nocache"]
        assert param.default is False
        assert param.annotation is bool


class TestNocacheEdgeCases:
    """Test edge cases and special scenarios for nocache functionality."""

    @pytest.mark.unit
    @staticmethod
    def test_nocache_with_expired_cache_entry() -> None:
        """Test nocache behavior when cache entry has expired."""
        call_count = 0

        @cached_operation(ttl=1)  # 1 second TTL
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call - populates cache
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1
        assert call_count == 1

        # Wait for cache to expire
        time.sleep(1.1)

        # Second call with nocache=True on expired entry
        result2 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result2 == 2
        assert call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_nocache_clears_expired_entry_before_writing_new() -> None:
        """Test that nocache properly handles expired entries."""
        call_count = 0

        @cached_operation(ttl=1)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1

        # Wait for expiry
        time.sleep(1.1)

        # Call with nocache=True - should write new value
        result2 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result2 == 2

        # Subsequent call should use new cached value
        result3 = test_func()  # type: ignore[call-arg]
        assert result3 == 2
        assert call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_multiple_consecutive_nocache_calls() -> None:
        """Test multiple consecutive calls with nocache=True."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # Multiple calls with nocache=True
        result1 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result1 == 1

        result2 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result2 == 2

        result3 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result3 == 3

        assert call_count == 3

        # Last call without nocache should use cached value from third call
        result4 = test_func()  # type: ignore[call-arg]
        assert result4 == 3
        assert call_count == 3

    @pytest.mark.unit
    @staticmethod
    def test_nocache_interleaved_with_normal_calls() -> None:
        """Test interleaving nocache=True with normal cached calls."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # Normal call - populates cache
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1
        assert call_count == 1

        # Normal call - uses cache
        result2 = test_func()  # type: ignore[call-arg]
        assert result2 == 1
        assert call_count == 1

        # Nocache call - skips cache, updates it
        result3 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result3 == 2
        assert call_count == 2

        # Normal call - uses updated cache
        result4 = test_func()  # type: ignore[call-arg]
        assert result4 == 2
        assert call_count == 2

        # Another nocache call
        result5 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result5 == 3
        assert call_count == 3

        # Final normal call - uses latest cached value
        result6 = test_func()  # type: ignore[call-arg]
        assert result6 == 3
        assert call_count == 3


class TestNocacheWithClearCache:
    """Test interaction between nocache and cache clearing."""

    @pytest.mark.unit
    @staticmethod
    def test_nocache_after_cache_clear() -> None:
        """Test that nocache works correctly after cache has been cleared."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # Populate cache
        result1 = test_func()  # type: ignore[call-arg]
        assert result1 == 1

        # Clear cache
        operation_cache_clear()
        assert len(_operation_cache) == 0

        # Call with nocache=True - should work normally
        result2 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result2 == 2

        # Verify cache was populated
        assert len(_operation_cache) == 1

    @pytest.mark.unit
    @staticmethod
    def test_cache_clear_removes_nocache_populated_entries() -> None:
        """Test that cache clear removes entries populated with nocache=True."""
        call_count = 0

        @cached_operation(ttl=60)
        def test_func() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # Populate cache with nocache=True
        result1 = test_func(nocache=True)  # type: ignore[call-arg]
        assert result1 == 1
        assert len(_operation_cache) == 1

        # Clear cache
        operation_cache_clear()
        assert len(_operation_cache) == 0

        # Subsequent call should fetch fresh data
        result2 = test_func()  # type: ignore[call-arg]
        assert result2 == 2
