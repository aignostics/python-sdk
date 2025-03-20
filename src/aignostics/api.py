"""Webservice API of Aignostics Python SDK.

This module provides a webservice API with several endpoints:
- A health/healthz endpoint that returns the health status of the service
- A hello-world endpoint that returns a greeting message
- An echo endpoint that echoes back the provided text

The endpoints use Pydantic models for request and response validation.
"""

import os
from collections.abc import Generator
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, FastAPI, Response, status
from pydantic import BaseModel, Field

from aignostics import Service

TITLE = "Aignostics Python SDK"
HELLO_WORLD_EXAMPLE = "Hello, world!"
UVICORN_HOST = os.environ.get("UVICORN_HOST", "127.0.0.1")
UVICORN_PORT = os.environ.get("UVICORN_PORT", "8000")
CONTACT_NAME = "Aignostics GmbH"
CONTACT_EMAIL = "support@aignostics.com"
CONTACT_URL = "https://github.com/aignostics"
TERMS_OF_SERVICE_URL = "https://aignostics.readthedocs.io/en/latest/"


def get_service() -> Generator[Service, None, None]:
    """Get the service instance.

    Yields:
        Service: The service instance.
    """
    service = Service()
    try:
        yield service
    finally:
        # Cleanup code if needed
        pass


api = FastAPI(
    root_path="/api",
    title=TITLE,
    contact={
        "name": CONTACT_NAME,
        "email": CONTACT_EMAIL,
        "url": CONTACT_URL,
    },
    terms_of_service=TERMS_OF_SERVICE_URL,
    openapi_tags=[
        {
            "name": "v1",
            "description": "API version 1, check link on the right",
            "externalDocs": {
                "description": "sub-docs",
                "url": f"http://{UVICORN_HOST}:{UVICORN_PORT}/api/v1/docs",
            },
        },
        {
            "name": "v2",
            "description": "API version 2, check link on the right",
            "externalDocs": {
                "description": "sub-docs",
                "url": f"http://{UVICORN_HOST}:{UVICORN_PORT}/api/v2/docs",
            },
        },
    ],
)

api_v1 = FastAPI(
    version="1.0.0",
    title=TITLE,
    contact={
        "name": CONTACT_NAME,
        "email": CONTACT_EMAIL,
        "url": CONTACT_URL,
    },
    terms_of_service=TERMS_OF_SERVICE_URL,
)

api_v2 = FastAPI(
    version="2.0.0",
    title=TITLE,
    contact={
        "name": CONTACT_NAME,
        "email": CONTACT_EMAIL,
        "url": CONTACT_URL,
    },
    terms_of_service=TERMS_OF_SERVICE_URL,
)


class _HealthStatus(StrEnum):
    """Health status enumeration."""

    UP = "UP"
    DOWN = "DOWN"


class Health(BaseModel):
    """Health status model."""

    status: _HealthStatus
    reason: str | None = None


class HealthResponse(BaseModel):
    """Response model for health endpoint."""

    health: str = Field(
        ...,
        description="The hello world message",
        examples=[HELLO_WORLD_EXAMPLE],
    )


@api_v1.get("/healthz", tags=["Observability"])
@api_v1.get("/health", tags=["Observability"])
@api_v2.get("/healthz", tags=["Observability"])
@api_v2.get("/health", tags=["Observability"])
async def health(service: Annotated[Service, Depends(get_service)], response: Response) -> Health:
    """Check the health of the service.

    This endpoint returns the health status of the service.
    The health status can be either UP or DOWN.
    If the service is healthy, the status will be UP.
    If the service is unhealthy, the status will be DOWN and a reason will be provided.
    The response will have a 200 OK status code if the service is healthy,
    and a 500 Internal Server Error status code if the service is unhealthy.

    Returns:
        Health: The health status of the service.
    """
    if service.healthy():
        health_result = Health(status=_HealthStatus.UP)
    else:
        health_result = Health(status=_HealthStatus.DOWN, reason="Service is unhealthy")

    if health_result.status == _HealthStatus.DOWN:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return health_result


class HelloWorldResponse(BaseModel):
    """Response model for hello-world endpoint."""

    message: str = Field(
        ...,
        description="The hello world message",
        examples=[HELLO_WORLD_EXAMPLE],
    )


@api_v1.get("/hello-world", tags=["Basics"])
@api_v2.get("/hello-world", tags=["Basics"])
async def hello_world() -> HelloWorldResponse:
    """
    Return a hello world message.

    Returns:
        HelloWorldResponse: A response containing the hello world message.
    """
    return HelloWorldResponse(message=Service.get_hello_world())


class EchoResponse(BaseModel):
    """Response model for echo endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        description="The message content",
        examples=[HELLO_WORLD_EXAMPLE],
    )


class EchoRequest(BaseModel):
    """Request model for echo endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        description="The text to echo back",
        examples=[HELLO_WORLD_EXAMPLE],
    )


@api_v1.post("/echo", tags=["Basics"])
async def echo(request: EchoRequest) -> EchoResponse:
    """
    Echo back the provided text.

    Args:
        request (EchoRequest): The request containing the text to echo back.

    Returns:
        EchoResponse: A response containing the echoed text.

    Raises:
        422 Unprocessable Entity: If text is not provided or empty.
    """
    return EchoResponse(message=request.text)


class Utterance(BaseModel):
    """Request model for echo endpoint."""

    utterance: str = Field(
        ...,
        min_length=1,
        description="The utterance to echo back",
        examples=[HELLO_WORLD_EXAMPLE],
    )


@api_v2.post("/echo", tags=["Basics"])
async def echo_v2(request: Utterance) -> EchoResponse:
    """
    Echo back the provided utterance.

    Args:
        request (Utterance): The request containing the utterance to echo back.

    Returns:
        EchoResponse: A response containing the echoed utterance.

    Raises:
        422 Unprocessable Entity: If utterance is not provided or empty.
    """
    return EchoResponse(message=request.utterance)


api.mount("/v1", api_v1)
api.mount("/v2", api_v2)
