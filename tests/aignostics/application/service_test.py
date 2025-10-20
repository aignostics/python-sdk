"""Tests to verify the service functionality of the application module."""

from datetime import UTC, datetime, timedelta

import pytest
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.platform import NotFoundException
from tests.contants_test import HETA_APPLICATION_ID, HETA_APPLICATION_VERSION


@pytest.mark.unit
def test_validate_due_date_none() -> None:
    """Test that None is accepted (optional parameter)."""
    # Should not raise any exception
    ApplicationService._validate_due_date(None)


@pytest.mark.unit
def test_validate_due_date_valid_formats() -> None:
    """Test that valid ISO 8601 formats in the future are accepted."""
    # Create a datetime 2 hours in the future
    future_time = datetime.now(tz=UTC) + timedelta(hours=2)

    valid_formats = [
        future_time.isoformat(),  # With timezone offset like +00:00
        future_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",  # With Z suffix
        future_time.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",  # With microseconds and Z
        future_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),  # With microseconds and timezone
    ]

    for time_str in valid_formats:
        # Should not raise any exception
        try:
            ApplicationService._validate_due_date(time_str)
        except ValueError as e:
            pytest.fail(f"Valid ISO 8601 format '{time_str}' was rejected: {e}")


@pytest.mark.unit
def test_validate_due_date_invalid_format() -> None:
    """Test that invalid ISO 8601 formats are rejected."""
    invalid_formats = [
        "2025-10-19",  # Date only
        "19:53:00",  # Time only
        "2025/10/19 19:53:00",  # Wrong separators
        "2025-10-19 19:53:00",  # Space instead of T
        "not-a-date",  # Completely invalid
        "2025-13-45T25:70:99Z",  # Invalid values
    ]

    for time_str in invalid_formats:
        with pytest.raises(ValueError, match=r"Invalid ISO 8601 format"):
            ApplicationService._validate_due_date(time_str)


@pytest.mark.unit
def test_validate_due_date_past_datetime() -> None:
    """Test that datetimes in the past are rejected."""
    # Create a datetime 2 hours in the past
    past_time = datetime.now(tz=UTC) - timedelta(hours=2)

    past_formats = [
        past_time.isoformat(),
        past_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
    ]

    for time_str in past_formats:
        with pytest.raises(ValueError, match=r"due_date must be in the future"):
            ApplicationService._validate_due_date(time_str)


@pytest.mark.unit
def test_validate_due_date_current_time() -> None:
    """Test that current time (not future) is rejected."""
    # Get current time - should be rejected as it's not in the future
    current_time = datetime.now(tz=UTC)
    current_time_str = current_time.isoformat()

    with pytest.raises(ValueError, match=r"due_date must be in the future"):
        ApplicationService._validate_due_date(current_time_str)


@pytest.mark.unit
def test_validate_due_date_edge_case_one_second_future() -> None:
    """Test that a datetime 1 second in the future is accepted."""
    # Create a datetime 1 second in the future
    future_time = datetime.now(tz=UTC) + timedelta(seconds=1)
    future_time_str = future_time.isoformat()

    # Should not raise any exception
    try:
        ApplicationService._validate_due_date(future_time_str)
    except ValueError as e:
        pytest.fail(f"Future datetime '{future_time_str}' was rejected: {e}")


@pytest.mark.e2e
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
def test_application_version_invalid_semver_formats(runner: CliRunner) -> None:
    """Test that invalid semver formats are rejected with ValueError."""
    from aignostics.application import Service as ApplicationService

    service = ApplicationService()

    invalid_application_versions = [
        "test-app:v1.0.0",  # legacy format
        "bla",  # not semver
    ]

    for application_version in invalid_application_versions:
        with pytest.raises(ValueError, match=r"not compliant with semantic versioning"):
            service.application_version("test-app", application_version)


@pytest.mark.e2e
def test_application_version_use_latest_fallback(runner: CliRunner) -> None:
    """Test that latest version works and tested."""
    service = ApplicationService()

    try:
        app_version = service.application_version(HETA_APPLICATION_ID)
        assert app_version is not None
        assert app_version.version_number == HETA_APPLICATION_VERSION
    except NotFoundException as e:
        if "No versions found for application" in str(e):
            pass  # This is expected behavior
    except ValueError as e:
        pytest.fail(f"Unexpected error: {e}")

    with pytest.raises(ValueError, match=r"not compliant with semantic versioning"):
        service.application_version(HETA_APPLICATION_ID, "invalid-format")


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60 * 2)
def test_application_versions_are_unique(runner: CliRunner) -> None:
    """Check that application versions are unique (currently fails due to backend bug)."""
    # Get all applications
    service = ApplicationService()
    applications = service.applications()

    # Check each application for duplicate versions
    for app in applications:
        versions = service.application_versions(app.application_id)

        # Extract version numbers
        version_numbers = [v.version_number for v in versions]

        # Check for duplicates
        unique_versions = set(version_numbers)
        assert len(version_numbers) == len(unique_versions), (
            f"Application '{app.application_id}' has duplicate versions. "
            f"Found {len(version_numbers)} versions but only {len(unique_versions)} unique: {version_numbers}"
        )
