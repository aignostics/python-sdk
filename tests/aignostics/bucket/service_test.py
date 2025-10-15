"""Tests of the bucket service."""

from unittest import mock

import pytest

from aignostics.bucket._service import Service


@pytest.mark.integration
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_create_signed_upload_url_expires_in_3600_seconds(mock_get_s3_client: mock.MagicMock) -> None:
    """Test that create_signed_upload_url calls generate_presigned_url with ExpiresIn of 3600 seconds."""
    # Arrange
    mock_s3_client = mock.MagicMock()
    mock_s3_client.generate_presigned_url.return_value = "https://example.com/signed-upload-url"
    mock_get_s3_client.return_value = mock_s3_client

    service = Service()
    service._settings = mock.MagicMock()
    service._settings.upload_signed_url_expiration_seconds = 2 * 60 * 60
    service.get_bucket_name = mock.MagicMock(return_value="test-bucket")

    # Act
    result = service.create_signed_upload_url("test-object-key")

    # Assert
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="put_object",
        Params={"Bucket": service.get_bucket_name(), "Key": "test-object-key"},
        ExpiresIn=2 * 60 * 60,
    )
    assert result == "https://example.com/signed-upload-url"


@pytest.mark.integration
@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_create_signed_download_url_expires_in_7_days(mock_get_s3_client: mock.MagicMock) -> None:
    """Test that create_signed_download_url calls generate_presigned_url with ExpiresIn of 7 days (604800 seconds)."""
    # Arrange
    mock_s3_client = mock.MagicMock()
    mock_s3_client.generate_presigned_url.return_value = "https://example.com/signed-download-url"
    mock_get_s3_client.return_value = mock_s3_client

    service = Service()
    service._settings = mock.MagicMock()
    service._settings.download_signed_url_expiration_seconds = 7 * 24 * 60 * 60  # 7 days in seconds
    service.get_bucket_name = mock.MagicMock(return_value="test-bucket")

    # Act
    result = service.create_signed_download_url("test-object-key")

    # Assert
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": service.get_bucket_name(), "Key": "test-object-key"},
        ExpiresIn=604800,  # 7 days in seconds
    )
    assert result == "https://example.com/signed-download-url"
