"""Tests for health models and status definitions."""

import pytest

from aignostics.utils import get_logger
from aignostics.utils._health import Health

DB_FAILURE = "DB failure"

log = get_logger(__name__)


def test_health_default_status() -> None:
    """Test that health can be initialized with default UP status."""
    health = Health(status=Health.Code.UP)
    assert health.status == Health.Code.UP
    assert health.reason is None
    assert health.components == {}


def test_health_down_requires_reason() -> None:
    """Test that a DOWN status requires a reason."""
    # Valid case - DOWN with reason
    health = Health(status=Health.Code.DOWN, reason="Database connection failed")
    assert health.status == Health.Code.DOWN
    assert health.reason == "Database connection failed"

    # Invalid case - DOWN without reason should raise ValidationError
    with pytest.raises(ValueError, match="Health DOWN must have a reason"):
        Health(status=Health.Code.DOWN)


def test_health_up_with_reason_invalid() -> None:
    """Test that an UP status cannot have a reason."""
    with pytest.raises(ValueError, match="Health UP must not have reason"):
        Health(status=Health.Code.UP, reason="This should not be allowed")


def test_compute_health_from_components_no_components() -> None:
    """Test that health status is unchanged when there are no components."""
    health = Health(status=Health.Code.UP)
    result = health.compute_health_from_components()

    assert result.status == Health.Code.UP
    assert result.reason is None
    assert result is health  # Should return self


def test_compute_health_from_components_already_down() -> None:
    """Test that health status remains DOWN with original reason when already DOWN."""
    health = Health(status=Health.Code.DOWN, reason="Original failure")
    health.components = {
        "database": Health(status=Health.Code.DOWN, reason=DB_FAILURE),
        "cache": Health(status=Health.Code.UP),
    }

    result = health.compute_health_from_components()

    assert result.status == Health.Code.DOWN
    assert result.reason == "Original failure"  # Original reason should be preserved
    assert result is health  # Should return self


def test_compute_health_from_components_single_down() -> None:
    """Test that health status is DOWN when a single component is DOWN."""
    health = Health(status=Health.Code.UP)
    health.components = {
        "database": Health(status=Health.Code.DOWN, reason=DB_FAILURE),
        "cache": Health(status=Health.Code.UP),
    }

    result = health.compute_health_from_components()

    assert result.status == Health.Code.DOWN
    assert result.reason == "Component 'database' is DOWN"
    assert result is health  # Should return self


def test_compute_health_from_components_multiple_down() -> None:
    """Test that health status is DOWN with correct reason when multiple components are DOWN."""
    health = Health(status=Health.Code.UP)
    health.components = {
        "database": Health(status=Health.Code.DOWN, reason=DB_FAILURE),
        "cache": Health(status=Health.Code.DOWN, reason="Cache failure"),
        "api": Health(status=Health.Code.UP),
    }

    result = health.compute_health_from_components()

    assert result.status == Health.Code.DOWN
    # Order might vary, so check for presence of both components in reason
    assert result.reason is not None  # First ensure reason is not None
    assert "Components '" in result.reason
    assert "database" in result.reason
    assert "cache" in result.reason
    assert "are DOWN" in result.reason
    assert result is health  # Should return self


def test_compute_health_recursive() -> None:
    """Test that health status is recursively computed through the component tree."""
    # Create a nested health structure
    deep_component = Health(status=Health.Code.DOWN, reason="Deep failure")
    mid_component = Health(
        status=Health.Code.UP,
        components={"deep": deep_component},
    )
    health = Health(
        status=Health.Code.UP,
        components={"mid": mid_component, "other": Health(status=Health.Code.UP)},
    )

    result = health.compute_health_from_components()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None
    assert "Component 'mid' is DOWN" in result.reason
    assert health.components["mid"].status == Health.Code.DOWN
    assert health.components["mid"].reason is not None  # First ensure reason is not None
    assert "Component 'deep' is DOWN" in health.components["mid"].reason
    assert health.components["other"].status == Health.Code.UP


def test_str_representation_up() -> None:
    """Test string representation of UP health status."""
    health = Health(status=Health.Code.UP)
    assert str(health) == "UP"


def test_str_representation_down() -> None:
    """Test string representation of DOWN health status."""
    health = Health(status=Health.Code.DOWN, reason="Service unavailable")
    assert str(health) == "DOWN: Service unavailable"


def test_validate_health_state_integration() -> None:
    """Test the complete validation process with complex health tree."""
    # Create a complex health tree
    health = Health(
        status=Health.Code.UP,
        components={
            "database": Health(status=Health.Code.UP),
            "services": Health(
                status=Health.Code.UP,
                components={
                    "auth": Health(status=Health.Code.DOWN, reason="Auth error"),
                    "storage": Health(status=Health.Code.UP),
                },
            ),
            "monitoring": Health(status=Health.Code.UP),
        },
    )

    # Validation happens automatically during model creation via model_validator

    # Check propagation through levels
    assert health.status == Health.Code.DOWN
    assert health.reason is not None  # First ensure reason is not None
    assert "Component 'services' is DOWN" in health.reason

    assert health.components["services"].status == Health.Code.DOWN
    assert health.components["services"].reason is not None
    assert "Component 'auth' is DOWN" in health.components["services"].reason

    assert health.components["database"].status == Health.Code.UP
    assert health.components["monitoring"].status == Health.Code.UP


def test_health_manually_set_components_validated() -> None:
    """Test that manually setting components triggers validation."""
    health = Health(status=Health.Code.UP)

    # Now manually set components that would cause validation to fail
    with pytest.raises(ValueError, match="Health DOWN must have a reason"):
        health.components = {
            "bad_component": Health(status=Health.Code.DOWN),  # Missing reason
        }
        # Accessing any attribute triggers validation
        log.info(str(health))
