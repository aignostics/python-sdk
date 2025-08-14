"""Tests for bucket settings module."""

import pytest
from pydantic import ValidationError

from aignostics.bucket._settings import Settings


def test_signed_url_upload_settings() -> None:
    """Test upload settings, happy and not so happy path."""
    # Test default works
    settings = Settings()
    assert settings.upload_signed_url_expiration_seconds == 2 * 60 * 60  # 2 hours

    # Test min works
    settings = Settings(
        upload_signed_url_expiration_seconds=60,  # 1 minute
    )
    assert settings.upload_signed_url_expiration_seconds == 60

    # Test max works
    settings = Settings(
        upload_signed_url_expiration_seconds=7 * 24 * 60 * 60,  # 7 days
    )
    assert settings.upload_signed_url_expiration_seconds == 7 * 24 * 60 * 60

    # Test below min fails
    with pytest.raises(ValidationError):
        Settings(
            upload_signed_url_expiration_seconds=59,  # Below min
        )
    # Test above max fails
    with pytest.raises(ValidationError):
        Settings(
            upload_signed_url_expiration_seconds=7 * 24 * 60 * 60 + 1,  # Above max
        )


def test_signed_url_download_settings() -> None:
    """Test download settings, happy and not so happy path."""
    # Test default works (default is max: 7 days)
    settings = Settings()
    assert settings.download_signed_url_expiration_seconds == 7 * 24 * 60 * 60  # 7 days

    # Test min works
    settings = Settings(
        download_signed_url_expiration_seconds=60,  # 1 minute
    )
    assert settings.download_signed_url_expiration_seconds == 60

    # Test max works
    settings = Settings(
        download_signed_url_expiration_seconds=7 * 24 * 60 * 60,  # 7 days
    )
    assert settings.download_signed_url_expiration_seconds == 7 * 24 * 60 * 60

    # Test below min fails
    with pytest.raises(ValidationError):
        Settings(
            download_signed_url_expiration_seconds=59,  # Below min
        )

    # Test above max fails
    with pytest.raises(ValidationError):
        Settings(
            download_signed_url_expiration_seconds=7 * 24 * 60 * 60 + 1,  # Above max
        )
