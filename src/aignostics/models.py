"""Models used throughout Aignostics Python SDK's codebase ."""

from enum import StrEnum

from pydantic import BaseModel


class HealthStatus(StrEnum):
    """Health status enumeration."""

    UP = "UP"
    DOWN = "DOWN"


class Health(BaseModel):
    """Health status model."""

    status: HealthStatus
    reason: str | None = None
