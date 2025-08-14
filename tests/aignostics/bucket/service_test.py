"""Tests of the bucket service."""

from unittest import mock

from aignostics.bucket._service import Service


@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_create_signed_upload_url_expires_in_3600_seconds(mock_get_s3_client: mock.MagicMock) -> None:
    """Test that create_signed_upload_url calls generate_presigned_url with ExpiresIn of 3600 seconds."""
    # Arrange
    mock_s3_client = mock.MagicMock()
    mock_s3_client.generate_presigned_url.return_value = "https://example.com/signed-upload-url"
    mock_get_s3_client.return_value = mock_s3_client

    service = Service()
    service._settings = mock.MagicMock()
    service._settings.name = "test-bucket"
    service._settings.upload_signed_url_expiration_seconds = 2 * 60 * 60

    # Act
    result = service.create_signed_upload_url("test-object-key")

    # Assert
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="put_object",
        Params={"Bucket": "test-bucket", "Key": "test-object-key"},
        ExpiresIn=2 * 60 * 60,
    )
    assert result == "https://example.com/signed-upload-url"


@mock.patch("aignostics.bucket._service.Service._get_s3_client")
def test_create_signed_download_url_expires_in_7_days(mock_get_s3_client: mock.MagicMock) -> None:
    """Test that create_signed_download_url calls generate_presigned_url with ExpiresIn of 7 days (604800 seconds)."""
    # Arrange
    mock_s3_client = mock.MagicMock()
    mock_s3_client.generate_presigned_url.return_value = "https://example.com/signed-download-url"
    mock_get_s3_client.return_value = mock_s3_client

    service = Service()
    service._settings = mock.MagicMock()
    service._settings.name = "test-bucket"
    service._settings.download_signed_url_expiration_seconds = 7 * 24 * 60 * 60  # 7 days in seconds

    # Act
    result = service.create_signed_download_url("test-object-key")

    # Assert
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": "test-bucket", "Key": "test-object-key"},
        ExpiresIn=604800,  # 7 days in seconds
    )
    assert result == "https://example.com/signed-download-url"
