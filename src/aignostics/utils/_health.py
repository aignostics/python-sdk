"""Health models and status definitions for service health checks."""

from enum import StrEnum
from typing import ClassVar, Self

from pydantic import BaseModel, Field, model_validator


class _HealthStatus(StrEnum):
    UP = "UP"
    DOWN = "DOWN"


class Health(BaseModel):
    """Represents the health status of a service with optional components and failure reasons.

    - A health object can have child components, i.e. health forms a tree.
    - Any node in the tree can set itself to DOWN. In this case the node is required
        to set the reason attribute. If reason is not set when DOWN,
        automatic model validation of the tree will fail.
    - DOWN'ness is propagated to parent health objects. I.e. the health of a parent
        node is automatically set to DOWN if any of its child components are DOWN. The
        child components leading to this will be listed in the reason.
    - The root of the health tree is computed in the system module. The health of other
        modules is automatically picked up by the system module.
    """

    Code: ClassVar[type[_HealthStatus]] = _HealthStatus
    status: _HealthStatus
    reason: str | None = None
    components: dict[str, "Health"] = Field(default_factory=dict)

    def compute_health_from_components(self) -> Self:
        """Recursively compute health status from components.

        - If health is already DOWN, it remains DOWN with its original reason.
        - If health is UP but any component is DOWN, health becomes DOWN with
            a reason listing all failed components.

        Returns:
            Self: The updated health instance with computed status.
        """
        # Skip recomputation if already known to be DOWN
        if self.status == _HealthStatus.DOWN:
            return self

        # No components means we keep the existing status
        if not self.components:
            return self

        # Find all DOWN components
        down_components = []
        for component_name, component in self.components.items():
            # Recursively compute health for each component
            component.compute_health_from_components()
            if component.status == _HealthStatus.DOWN:
                down_components.append(component_name)

        # If any components are DOWN, mark the parent as DOWN
        if down_components:
            self.status = _HealthStatus.DOWN
            if len(down_components) == 1:
                self.reason = f"Component '{down_components[0]}' is DOWN"
            else:
                component_list = "', '".join(down_components)
                self.reason = f"Components '{component_list}' are DOWN"

        return self

    @model_validator(mode="after")
    def validate_health_state(self) -> Self:
        """Validate the health state and ensure consistency.

        - Compute overall health based on component health
        - Ensure UP status has no associated reason
        - Ensure DOWN status always has a reason

        Returns:
            Self: The validated model instance with correct health status.

        Raises:
            ValueError: If validation fails due to inconsistency.
        """
        # First compute health from components
        self.compute_health_from_components()

        # Validate that UP status has no reason
        if (self.status == _HealthStatus.UP) and self.reason:
            msg = f"Health {self.status} must not have reason"
            raise ValueError(msg)

        # Validate that DOWN status always has a reason
        if (self.status == _HealthStatus.DOWN) and not self.reason:
            msg = "Health DOWN must have a reason"
            raise ValueError(msg)

        return self

    def __str__(self) -> str:
        """Return string representation of health status with optional reason for DOWN state.

        Returns:
            str: The health status value, with reason appended if status is DOWN.
        """
        if self.status == _HealthStatus.DOWN and self.reason:
            return f"{self.status.value}: {self.reason}"
        return self.status.value
