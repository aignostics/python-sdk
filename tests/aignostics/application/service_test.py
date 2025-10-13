"""Tests to verify the service functionality of the application module."""

import pytest
from typer.testing import CliRunner

from aignostics.application import Service as ApplicationService
from aignostics.platform import NotFoundException
from tests.contants_test import HETA_APPLICATION_ID, HETA_APPLICATION_VERSION


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
