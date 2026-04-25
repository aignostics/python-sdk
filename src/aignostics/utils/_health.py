"""Health models and status definitions for service health checks."""

from enum import StrEnum
from typing import Any, ClassVar, Self

from pydantic import BaseModel, Field, model_validator


class HealthStatus(StrEnum):
    """Health status enumeration for service health checks.

    Values:
        UP: Service is operating normally
        DEGRADED: Service is operational but with reduced functionality
        DOWN: Service is not operational
    """

    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


class Health(BaseModel):
    """Represents the health status of a service with optional components and failure reasons.

    - A health object can have child components, i.e. health forms a tree.
        - Any node in the tree can set itself to DOWN or DEGRADED. If DOWN or DEGRADED, the node
            is required to set the reason attribute. If reason is not set when DOWN or DEGRADED,
            automatic model validation fails.
        - DOWN trumps DEGRADED, DEGRADED trumps UP. If any child is DOWN, parent is DOWN.
            If none are DOWN but any are DEGRADED, parent is DEGRADED.
        - The root of the health tree is computed in the system module.
            The health of other modules is automatically picked up by the system module.
    """

    Code: ClassVar[type[HealthStatus]] = HealthStatus
    status: HealthStatus
    reason: str | None = None
    components: dict[str, "Health"] = Field(default_factory=dict)
    uptime_statistics: dict[str, dict[str, Any]] | None = None  # Optional uptime stats

    def compute_health_from_components(self) -> Self:
        """Recursively compute health status from components.

        - If health is already DOWN, it remains DOWN with its original reason.
        - If health is UP but any component is DOWN, health becomes DOWN with
            a reason listing all failed components.
        - If no components are DOWN but any are DEGRADED, health becomes DEGRADED with a reason.

        Returns:
            Self: The updated health instance with computed status.
        """
        # Skip recomputation if already known to be DOWN
        if self.status == HealthStatus.DOWN:
            return self

        # No components means we keep the existing status
        if not self.components:
            return self

        # Find all DOWN and DEGRADED components
        down_components = []
        degraded_components = []
        for component_name, component in self.components.items():
            # Recursively compute health for each component
            component.compute_health_from_components()
            if component.status == HealthStatus.DOWN:
                down_components.append((component_name, component.reason))
            elif component.status == HealthStatus.DEGRADED:
                degraded_components.append((component_name, component.reason))

        # If any components are DOWN, mark the parent as DOWN
        if down_components:
            self.status = HealthStatus.DOWN
            if len(down_components) == 1:
                component_name, component_reason = down_components[0]
                self.reason = f"Component '{component_name}' is DOWN ({component_reason})"
            else:
                component_list = ", ".join(f"'{name}' ({reason})" for name, reason in down_components)
                self.reason = f"Components {component_list} are DOWN"
        # If no components are DOWN but any are DEGRADED, mark parent as DEGRADED
        elif degraded_components:
            self.status = HealthStatus.DEGRADED
            if len(degraded_components) == 1:
                component_name, component_reason = degraded_components[0]
                self.reason = f"Component '{component_name}' is DEGRADED ({component_reason})"
            else:
                component_list = ", ".join(f"'{name}' ({reason})" for name, reason in degraded_components)
                self.reason = f"Components {component_list} are DEGRADED"

        return self

    @model_validator(mode="after")
    def validate_health_state(self) -> Self:
        """Validate the health state and ensure consistency.

        - Compute overall health based on component health
        - Ensure UP status has no associated reason
        - Ensure DOWN and DEGRADED status always have a reason

        Returns:
            Self: The validated model instance with correct health status.

        Raises:
            ValueError: If validation fails due to inconsistency.
        """
        # First compute health from components
        self.compute_health_from_components()

        # Validate that UP status has no reason
        if (self.status == HealthStatus.UP) and self.reason:
            msg = f"Health {self.status} must not have reason"
            raise ValueError(msg)

        # Validate that DOWN and DEGRADED status always have a reason
        if (self.status in {HealthStatus.DOWN, HealthStatus.DEGRADED}) and not self.reason:
            msg = f"Health {self.status} must have a reason"
            raise ValueError(msg)

        return self

    def __str__(self) -> str:
        """Return string representation of health status with optional reason for DOWN/DEGRADED state.

        Returns:
            str: The health status value, with reason appended if status is DOWN or DEGRADED.
        """
        if self.status in {HealthStatus.DOWN, HealthStatus.DEGRADED} and self.reason:
            return f"{self.status.value}: {self.reason}"
        return self.status.value

    def __bool__(self) -> bool:
        """Convert health status to a boolean value.

        Returns:
            bool: True if the status is UP or DEGRADED, False otherwise.
        """
        return self.status in {HealthStatus.UP, HealthStatus.DEGRADED}
