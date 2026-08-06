"""Tests for bucket settings module."""

import json

import pytest
from aignostics.bucket._settings import Settings
from aignostics.cli import cli
from pydantic import ValidationError
from typer.testing import CliRunner


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.integration
@pytest.mark.timeout(timeout=30)
def test_cli_bucket_info_settings(runner: CliRunner) -> None:
    """Check settings in system info with proper defaults."""
    result = runner.invoke(cli, ["system", "info"])
    assert result.exit_code == 0

    # Parse the JSON output from stdout only (stderr contains logs)
    output_data = json.loads(result.stdout)

    # Verify the bucket settings defaults
    assert output_data["settings"]["AIGNOSTICS_BUCKET_PROTOCOL"] == "gs"
    assert output_data["settings"]["AIGNOSTICS_BUCKET_REGION_NAME"] == "EUROPE-WEST3"
    assert output_data["settings"]["AIGNOSTICS_BUCKET_UPLOAD_SIGNED_URL_EXPIRATION_SECONDS"] == 7200
    assert output_data["settings"]["AIGNOSTICS_BUCKET_DOWNLOAD_SIGNED_URL_EXPIRATION_SECONDS"] == 604800
