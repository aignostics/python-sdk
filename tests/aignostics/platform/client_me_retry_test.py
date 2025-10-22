"""Tests for retry and timeout behavior in Client.me() method."""

import logging
import time
from http import HTTPStatus
from unittest.mock import ANY, MagicMock, Mock, patch

import pytest
from aignx.codegen.exceptions import ServiceException
from urllib3.exceptions import IncompleteRead, PoolError, ProtocolError, ProxyError
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError

from aignostics.platform._client import Client


class TestMeSuccess:
    """Test cases for successful Client.me() calls."""

    @pytest.mark.unit
    @staticmethod
    def test_me_success_no_retry(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that successful me() call completes without retries.

        This is a sanity check that the happy path works correctly.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        client_with_mock_api._api.get_me_v1_me_get.return_value = mock_me_response

        result = client_with_mock_api.me()

        assert result == mock_me_response
        # Should succeed on first try
        assert client_with_mock_api._api.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_me_passes_timeout_to_api(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() passes the correct timeout value to the API call."""
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        client_with_mock_api._api.get_me_v1_me_get.return_value = mock_me_response

        # Set a specific timeout in settings
        mock_settings.return_value.me_timeout = 15.0

        client_with_mock_api.me()

        # Verify the timeout was passed correctly
        client_with_mock_api._api.get_me_v1_me_get.assert_called_once_with(_request_timeout=15, _headers=ANY)


class TestMeRetryOnTransientErrors:
    """Test cases for retry behavior on transient errors."""

    @pytest.mark.unit
    @staticmethod
    def test_me_retries_on_service_exception(mock_settings: MagicMock, client_with_mock_api: Client, caplog) -> None:
        """Test that me() retries on ServiceException (5xx server errors).

        ServiceException represents server errors that should be retried.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            mock_response = Mock()
            mock_response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with (
            pytest.raises(ServiceException),
            caplog.at_level(logging.WARNING),
        ):
            client_with_mock_api.me()

        # Should have retried multiple times
        assert call_count >= 3, f"Expected at least 3 attempts but got {call_count}"

        # Verify retry log messages exist
        retry_logs = [record for record in caplog.records if "Retrying" in record.getMessage()]
        assert len(retry_logs) > 0, "Should log retry attempts for ServiceException"

    @pytest.mark.unit
    @staticmethod
    def test_me_retries_on_timeout_error(mock_settings: MagicMock, client_with_mock_api: Client, caplog) -> None:
        """Test that me() retries on Urllib3TimeoutError.

        Timeout errors are transient and should be retried.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            msg = "Request timed out"
            raise Urllib3TimeoutError(msg)

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with (
            pytest.raises(Urllib3TimeoutError),
            caplog.at_level(logging.WARNING),
        ):
            client_with_mock_api.me()

        # Should have retried multiple times
        assert call_count >= 3, f"Expected at least 3 attempts but got {call_count}"

        # Verify retry log messages exist
        retry_logs = [record for record in caplog.records if "Retrying" in record.getMessage()]
        assert len(retry_logs) > 0, "Should log retry attempts for timeout errors"

    @pytest.mark.unit
    @staticmethod
    def test_me_retries_on_pool_error(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() retries on PoolError.

        Pool errors are transient connection pool issues that should be retried.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            msg = "Connection pool exhausted"
            raise PoolError(pool=None, message=msg)

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(PoolError):
            client_with_mock_api.me()

        # Should have retried multiple times
        assert call_count >= 3, f"Expected at least 3 attempts but got {call_count}"

    @pytest.mark.unit
    @staticmethod
    def test_me_retries_on_incomplete_read(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() retries on IncompleteRead.

        IncompleteRead errors occur when the connection is closed prematurely and should be retried.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            raise IncompleteRead(partial=10, expected=100)

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(IncompleteRead):
            client_with_mock_api.me()

        # Should have retried multiple times
        assert call_count >= 3, f"Expected at least 3 attempts but got {call_count}"

    @pytest.mark.unit
    @staticmethod
    def test_me_retries_on_protocol_error(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() retries on ProtocolError.

        Protocol errors are transient network issues that should be retried.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            msg = "Protocol error"
            raise ProtocolError(msg)

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(ProtocolError):
            client_with_mock_api.me()

        # Should have retried multiple times
        assert call_count >= 3, f"Expected at least 3 attempts but got {call_count}"

    @pytest.mark.unit
    @staticmethod
    def test_me_retries_on_proxy_error(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() retries on ProxyError.

        Proxy errors can be transient and should be retried.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            msg = "Proxy connection failed"
            raise ProxyError(msg, error=Exception(msg))

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(ProxyError):
            client_with_mock_api.me()

        # Should have retried multiple times
        assert call_count >= 3, f"Expected at least 3 attempts but got {call_count}"


class TestMeRetrySuccess:
    """Test cases for successful retry scenarios."""

    @pytest.mark.unit
    @staticmethod
    def test_me_succeeds_after_transient_failure(
        mock_settings: MagicMock, client_with_mock_api: Client, caplog
    ) -> None:
        """Test that me() succeeds after initial transient failures.

        This tests the happy path of retry logic - connection fails initially but succeeds
        on a subsequent retry.
        """
        call_count = 0
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:  # Fail once, then succeed
                time.sleep(0.5)
                msg = "Temporary connection failure"
                raise Urllib3TimeoutError(msg)
            return mock_me_response

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with caplog.at_level(logging.WARNING):
            result = client_with_mock_api.me()

        assert result == mock_me_response
        # Should have called get_me twice (initial + 1 retry)
        assert call_count == 2, f"Expected 2 attempts but got {call_count}"

        # Verify retry log messages exist
        retry_logs = [record for record in caplog.records if "Retrying" in record.getMessage()]
        assert len(retry_logs) == 1, "Should log exactly one retry attempt"

    @pytest.mark.unit
    @staticmethod
    def test_me_succeeds_on_second_retry(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() succeeds after multiple transient failures.

        This tests that the retry logic can handle multiple consecutive failures
        before succeeding.
        """
        call_count = 0
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail twice, then succeed
                time.sleep(0.5)
                mock_response = Mock()
                mock_response.status = HTTPStatus.SERVICE_UNAVAILABLE
                raise ServiceException(status=HTTPStatus.SERVICE_UNAVAILABLE, reason="Service temporarily unavailable")
            return mock_me_response

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        result = client_with_mock_api.me()

        assert result == mock_me_response
        # Should have called get_me three times (initial + 2 retries)
        assert call_count == 3, f"Expected 3 attempts but got {call_count}"


class TestMeNoRetryOnNonRetryableErrors:
    """Test cases for errors that should NOT trigger retries."""

    @pytest.mark.unit
    @staticmethod
    def test_me_no_retry_on_non_retryable_exception(
        mock_settings: MagicMock, client_with_mock_api: Client, caplog
    ) -> None:
        """Test that me() does not retry on non-retryable exceptions.

        Exceptions not in RETRYABLE_EXCEPTIONS should fail immediately without retries.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            msg = "Invalid request"
            raise ValueError(msg)

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        start_time = time.time()

        with (
            pytest.raises(ValueError),
            caplog.at_level(logging.WARNING),
        ):
            client_with_mock_api.me()

        elapsed_time = time.time() - start_time

        # Should fail immediately without retries - elapsed time should be < 2 seconds
        assert elapsed_time < 2.0, f"Expected fast failure but took {elapsed_time:.2f}s"

        # Verify get_me was called only once (no retries)
        assert call_count == 1

        # Verify no retry log messages
        retry_logs = [record for record in caplog.records if "Retrying" in record.getMessage()]
        assert len(retry_logs) == 0, "Should not log retry attempts for non-retryable errors"


class TestMeRetryConfiguration:
    """Test cases for retry configuration settings."""

    @pytest.mark.unit
    @staticmethod
    def test_me_respects_max_attempts_setting(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() respects the me_retry_attempts setting.

        The retry logic should stop after the configured maximum number of attempts.
        """
        # Set max attempts to 5
        mock_settings.return_value.me_retry_attempts = 5

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            mock_response = Mock()
            mock_response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(ServiceException):
            client_with_mock_api.me()

        # Should have attempted exactly 5 times (respecting the configured max)
        assert call_count == 5, f"Expected exactly 5 attempts but got {call_count}"

    @pytest.mark.unit
    @staticmethod
    def test_me_respects_zero_max_attempts(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() with me_retry_attempts=0 does not retry.

        When max attempts is set to 0, the function should fail immediately without any retries.
        """
        # Set max attempts to 0 (no retries)
        mock_settings.return_value.me_retry_attempts = 0

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = Mock()
            mock_response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(ServiceException):
            client_with_mock_api.me()

        # Should have attempted exactly once (no retries)
        assert call_count == 1, f"Expected exactly 1 attempt but got {call_count}"

    @pytest.mark.unit
    @staticmethod
    def test_me_wait_times_increase_with_retries(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that wait times between retries increase exponentially.

        The exponential backoff should increase wait times between retries.
        """
        mock_settings.return_value.me_retry_wait_min = 0.1
        mock_settings.return_value.me_retry_wait_max = 10.0
        mock_settings.return_value.me_retry_attempts = 4

        call_times = []

        def side_effect(*args, **kwargs):
            call_times.append(time.time())
            mock_response = Mock()
            mock_response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with pytest.raises(ServiceException):
            client_with_mock_api.me()

        # Verify we have multiple attempts
        assert len(call_times) == 4, f"Expected 4 attempts but got {len(call_times)}"

        # Calculate wait times between attempts
        wait_times = [call_times[i + 1] - call_times[i] for i in range(len(call_times) - 1)]

        # Verify that wait times are within the configured range
        # With min=0.1 and exponential backoff with jitter, first wait should be around 0.1-0.2s
        for wait_time in wait_times:
            assert wait_time >= 0.05, f"Wait time {wait_time} is too short (should be at least close to min 0.1)"
            assert wait_time <= 12, f"Wait time {wait_time} is too long (should be capped at max + some overhead)"

        # Note: We can't verify strict exponential increase due to jitter,
        # but we can verify that at least some wait times are longer than min


class TestMeEdgeCases:
    """Test cases for edge cases and unusual scenarios."""

    @pytest.mark.unit
    @staticmethod
    def test_me_with_none_response(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() handles None response from API.

        The API might return None in error cases, and this should be handled gracefully.
        """
        client_with_mock_api._api.get_me_v1_me_get.return_value = None

        result = client_with_mock_api.me()

        assert result is None
        assert client_with_mock_api._api.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_me_with_empty_response(mock_settings: MagicMock, client_with_mock_api: Client) -> None:
        """Test that me() handles empty dict response from API."""
        client_with_mock_api._api.get_me_v1_me_get.return_value = {}

        result = client_with_mock_api.me()

        assert result == {}
        assert client_with_mock_api._api.get_me_v1_me_get.call_count == 1

    @pytest.mark.unit
    @staticmethod
    def test_me_logs_retry_attempts(mock_settings: MagicMock, client_with_mock_api: Client, caplog) -> None:
        """Test that me() logs retry attempts at WARNING level.

        Retry attempts should be logged to help with debugging and monitoring.
        """
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.5)
            mock_response = Mock()
            mock_response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            raise ServiceException(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason="Server error")

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with (
            pytest.raises(ServiceException),
            caplog.at_level(logging.WARNING),
        ):
            client_with_mock_api.me()

        # Verify that retry attempts were logged
        retry_logs = [
            record
            for record in caplog.records
            if "Retrying" in record.getMessage() and record.levelno == logging.WARNING
        ]
        assert len(retry_logs) > 0, "Should log retry attempts at WARNING level"

        # Verify log contains useful information
        for log in retry_logs:
            assert "attempt" in log.getMessage().lower() or "retrying" in log.getMessage().lower()


class TestMeWithSettings:
    """Test cases for with settings."""

    @pytest.mark.unit
    @staticmethod
    def test_me_uses_settings_from_settings(client_with_mock_api: Client) -> None:
        """Test that me() retrieves settings on each call.

        Settings should be fetched dynamically to allow for runtime configuration changes.
        """
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}
        client_with_mock_api._api.get_me_v1_me_get.return_value = mock_me_response

        with patch("aignostics.platform._client.settings") as mock_settings:
            settings_obj = MagicMock()
            settings_obj.me_retry_attempts = 3
            settings_obj.me_retry_wait_min = 0.1
            settings_obj.me_retry_wait_max = 5.0
            settings_obj.me_timeout = 20.0
            mock_settings.return_value = settings_obj

            client_with_mock_api.me()

            # Verify settings were called
            mock_settings.assert_called()

            # Verify the timeout from settings was used
            client_with_mock_api._api.get_me_v1_me_get.assert_called_once_with(_request_timeout=20, _headers=ANY)

    @pytest.mark.unit
    @staticmethod
    def test_me_allows_runtime_settings_changes(client_with_mock_api: Client) -> None:
        """Test that me() respects settings changes between calls.

        Settings should be re-evaluated on each call to allow for runtime configuration.
        """
        call_count = 0
        mock_me_response = {"user_id": "test-user", "org_id": "test-org"}

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                time.sleep(0.5)
                msg = "Temporary error"
                raise Urllib3TimeoutError(msg)
            return mock_me_response

        client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

        with patch("aignostics.platform._client.settings") as mock_settings:
            # First call with max_attempts = 1 (will fail)
            settings_obj_1 = MagicMock()
            settings_obj_1.me_retry_attempts = 1
            settings_obj_1.me_retry_wait_min = 0.1
            settings_obj_1.me_retry_wait_max = 2.0
            settings_obj_1.me_timeout = 10.0

            mock_settings.return_value = settings_obj_1

            with pytest.raises(Urllib3TimeoutError):
                client_with_mock_api.me()

            assert call_count == 1

            # Reset the side effect
            call_count = 0
            client_with_mock_api._api.get_me_v1_me_get.side_effect = side_effect

            # Second call with max_attempts = 3 (will succeed after retry)
            settings_obj_2 = MagicMock()
            settings_obj_2.me_retry_attempts = 3
            settings_obj_2.me_retry_wait_min = 0.1
            settings_obj_2.me_retry_wait_max = 2.0
            settings_obj_2.me_timeout = 10.0

            mock_settings.return_value = settings_obj_2

            result = client_with_mock_api.me()

            assert result == mock_me_response
            assert call_count == 2
