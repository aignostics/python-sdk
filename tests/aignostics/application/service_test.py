"""Tests to verify the service functionality of the application module."""

import pytest
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.platform import NotFoundException
from tests.contants_test import HETA_APPLICATION_ID


@pytest.mark.unit
def test_application_version_valid_semver_formats(runner: CliRunner) -> None:
    """Test that valid semver formats are accepted."""
    from aignostics.application import Service as ApplicationService

    service = ApplicationService()

    # These should work if the application exists
    valid_formats = [
        "test-app:v1.0.0",
        "test-app:v1.2.3",
        "test-app:v10.20.30",
        "test-app:v1.1.2-prerelease+meta",
        "test-app:v1.1.2+meta",
        "test-app:v1.1.2+meta-valid",
        "test-app:v1.0.0-alpha",
        "test-app:v1.0.0-beta",
        "test-app:v1.0.0-alpha.beta",
        "test-app:v1.0.0-alpha.1",
        "test-app:v1.0.0-alpha0.beta",
        "test-app:v1.0.0-alpha.alpha",
        "test-app:v1.0.0-alpha+metadata",
        "test-app:v1.0.0-rc.1+meta",
    ]

    for version_id in valid_formats:
        try:
            service.application_version(version_id)
        except ValueError as e:
            pytest.fail(f"Valid semver format '{version_id}' was rejected: {e}")
        except NotFoundException:
            pytest.skip(f"Application '{version_id.split(':')[0]}' not found, skipping test for this version format.")


@pytest.mark.unit
def test_application_version_invalid_semver_formats(runner: CliRunner, record_property) -> None:
    """Test that invalid semver formats are rejected with ValueError."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    from aignostics.application import Service as ApplicationService

    service = ApplicationService()

    invalid_formats = [
        "test-app:1.0.0",  # Missing 'v' prefix
        "test-app:v1",  # Incomplete version
        "test-app:v1.0",  # Incomplete version
        "test-app:v1.0.0-",  # Trailing dash
        "test-app:v1.0.0+",  # Trailing plus
        "test-app:v1.0.0-+",  # Invalid prerelease
        "test-app:v1.0.0-+123",  # Invalid prerelease
        "test-app:v+invalid",  # Invalid format
        "test-app:v-invalid",  # Invalid format
        "test-app:v1.0.0.DEV.SNAPSHOT",  # Too many version parts
        "test-app:v1.0-SNAPSHOT-123",  # Invalid format
        "test-app:v",  # Just 'v'
        "test-app:vx.y.z",  # Non-numeric
        "test-app:v1.0.0-αα",  # Non-ASCII in prerelease # noqa: RUF001
        ":v1.0.0",  # Missing application ID
        "test-app:",  # Missing version
        "no-colon-v1.0.0",  # Missing colon separator
    ]

    for version_id in invalid_formats:
        with pytest.raises(ValueError, match=r"Invalid application version id format"):
            service.application_version(version_id)


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_application_version_use_latest_fallback(runner: CliRunner, record_property) -> None:
    """Test that use_latest_if_no_version_given works correctly."""
    record_property("tested-item-id", "SPEC-APPLICATION-SERVICE")
    service = ApplicationService()

    try:
        result = service.application_version(HETA_APPLICATION_ID, use_latest_if_no_version_given=True)
        assert result is not None
        assert result.application_version_id.startswith(f"{HETA_APPLICATION_ID}:v")
    except ValueError as e:
        if "no latest version available" in str(e):
            pass  # This is expected behavior
        else:
            pytest.fail(f"Unexpected error: {e}")

    with pytest.raises(ValueError, match=r"Invalid application version id format"):
        service.application_version("invalid-format", use_latest_if_no_version_given=False)


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60)
def test_application_versions_with_str_arg(runner: CliRunner, silent_logging: None) -> None:
    """Test that application_versions works correctly when passed a string application ID."""
    service = ApplicationService()

    # Test with valid application ID as string
    versions = service.application_versions(HETA_APPLICATION_ID)
    assert isinstance(versions, list)
    # If there are versions, verify they are ApplicationVersion objects
    if versions:
        from aignostics.platform import ApplicationVersion

        assert all(isinstance(v, ApplicationVersion) for v in versions)


@pytest.mark.e2e
@pytest.mark.flaky(retries=1, delay=5)
@pytest.mark.timeout(timeout=60)
def test_application_version_latest_with_str_arg(runner: CliRunner, silent_logging: None) -> None:
    """Test that application_version_latest works correctly when passed a string application ID."""
    service = ApplicationService()

    # Test with valid application ID as string
    latest = service.application_version_latest(HETA_APPLICATION_ID)
    # May be None if no versions exist, but should not raise an error
    if latest is not None:
        from aignostics.platform import ApplicationVersion

        assert isinstance(latest, ApplicationVersion)
        assert latest.application_version_id.startswith(f"{HETA_APPLICATION_ID}:v")


@pytest.mark.unit
def test_application_versions_exception_handling_with_str_arg() -> None:
    """Test that exception handling correctly uses string application ID in error message."""
    from unittest.mock import MagicMock, patch

    service = ApplicationService()

    # Mock the platform client to raise an exception
    with patch.object(service, "_get_platform_client") as mock_client:
        mock_versions = MagicMock()
        mock_versions.list_sorted.side_effect = Exception("Test error")
        mock_client.return_value.applications.versions = mock_versions

        # Test with string application ID
        test_app_id = "test-application-id"
        expected_error = rf"Failed to retrieve application versions for application '{test_app_id}'"
        with pytest.raises(RuntimeError, match=expected_error):
            service.application_versions(test_app_id)


@pytest.mark.unit
def test_application_version_latest_exception_handling_with_str_arg() -> None:
    """Test exception handling in application_version_latest with string application ID."""
    from unittest.mock import MagicMock, patch

    service = ApplicationService()

    # Mock the platform client to raise an exception
    with patch.object(service, "_get_platform_client") as mock_client:
        mock_versions = MagicMock()
        mock_versions.list_sorted.side_effect = Exception("Test error")
        mock_client.return_value.applications.versions = mock_versions

        # Test with string application ID
        test_app_id = "test-application-id"
        expected_error = rf"Failed to retrieve application versions for application '{test_app_id}'"
        with pytest.raises(RuntimeError, match=expected_error):
            service.application_version_latest(test_app_id)
