"""Models used throughout Aignostics Python SDK's codebase ."""

from enum import StrEnum

from pydantic import BaseModel, Field

UTTERANCE_EXAMPLE = "Hello, world!"
ECHO_EXAMPLE = "HELLO, WORLD!"


class Utterance(BaseModel):
    """Model representing a text utterance."""

    text: str = Field(
        ...,
        min_length=1,
        description="The utterance to echo back",
        examples=[UTTERANCE_EXAMPLE],
    )


class Echo(BaseModel):
    """Response model for echo endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        description="The echo",
        examples=[ECHO_EXAMPLE],
    )


class HealthStatus(StrEnum):
    """Health status enumeration."""

    UP = "UP"
    DOWN = "DOWN"


class Health(BaseModel):
    """Health status model."""

    status: HealthStatus
    reason: str | None = None
