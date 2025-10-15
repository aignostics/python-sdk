"""Tests for health models and status definitions."""

import pytest

from aignostics.utils import get_logger
from aignostics.utils._health import Health

DB_FAILURE = "DB failure"

log = get_logger(__name__)


@pytest.mark.unit
def test_health_default_status(record_property) -> None:
    """Test that health can be initialized with default UP status."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.UP)
    assert health.status == Health.Code.UP
    assert health.reason is None
    assert health.components == {}


@pytest.mark.unit
def test_health_down_requires_reason(record_property) -> None:
    """Test that a DOWN status requires a reason."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    # Valid case - DOWN with reason
    health = Health(status=Health.Code.DOWN, reason="Database connection failed")
    assert health.status == Health.Code.DOWN
    assert health.reason == "Database connection failed"

    # Invalid case - DOWN without reason should raise ValidationError
    with pytest.raises(ValueError, match="Health DOWN must have a reason"):
        Health(status=Health.Code.DOWN)


@pytest.mark.unit
def test_health_up_with_reason_invalid(record_property) -> None:
    """Test that an UP status cannot have a reason."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with pytest.raises(ValueError, match="Health UP must not have reason"):
        Health(status=Health.Code.UP, reason="This should not be allowed")


@pytest.mark.unit
def test_compute_health_from_components_no_components(record_property) -> None:
    """Test that health status is unchanged when there are no components."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.UP)
    result = health.compute_health_from_components()

    assert result.status == Health.Code.UP
    assert result.reason is None
    assert result is health  # Should return self


@pytest.mark.unit
def test_compute_health_from_components_already_down(record_property) -> None:
    """Test that health status remains DOWN with original reason when already DOWN."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.DOWN, reason="Original failure")
    health.components = {
        "database": Health(status=Health.Code.DOWN, reason=DB_FAILURE),
        "cache": Health(status=Health.Code.UP),
    }

    result = health.compute_health_from_components()

    assert result.status == Health.Code.DOWN
    assert result.reason == "Original failure"  # Original reason should be preserved
    assert result is health  # Should return self


@pytest.mark.unit
def test_compute_health_from_components_single_down(record_property) -> None:
    """Test that health status is DOWN when a single component is DOWN."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.UP)
    health.components = {
        "database": Health(status=Health.Code.DOWN, reason=DB_FAILURE),
        "cache": Health(status=Health.Code.UP),
    }

    result = health.compute_health_from_components()

    assert result.status == Health.Code.DOWN
    assert result.reason == "Component 'database' is DOWN"
    assert result is health  # Should return self


@pytest.mark.unit
def test_compute_health_from_components_multiple_down(record_property) -> None:
    """Test that health status is DOWN with correct reason when multiple components are DOWN."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
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


@pytest.mark.unit
def test_compute_health_recursive(record_property) -> None:
    """Test that health status is recursively computed through the component tree."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
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


@pytest.mark.unit
def test_str_representation_up(record_property) -> None:
    """Test string representation of UP health status."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.UP)
    assert str(health) == "UP"


@pytest.mark.unit
def test_str_representation_down(record_property) -> None:
    """Test string representation of DOWN health status."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.DOWN, reason="Service unavailable")
    assert str(health) == "DOWN: Service unavailable"


@pytest.mark.unit
def test_validate_health_state_integration(record_property) -> None:
    """Test the complete validation process with complex health tree."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
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


@pytest.mark.unit
def test_health_manually_set_components_validated(record_property) -> None:
    """Test that manually setting components triggers validation."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    health = Health(status=Health.Code.UP)

    # Now manually set components that would cause validation to fail
    with pytest.raises(ValueError, match="Health DOWN must have a reason"):
        health.components = {
            "bad_component": Health(status=Health.Code.DOWN),  # Missing reason
        }
        # Accessing any attribute triggers validation
        log.info(str(health))
