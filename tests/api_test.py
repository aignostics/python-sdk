"""Tests to verify the API functionality of Aignostics Python SDK."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from aignostics.api import api

HELLO_WORLD_PATH_V1 = "/api/v1/hello-world"
HELLO_WORLD_PATH_V2 = "/api/v2/hello-world"

ECHO_PATH_V1 = "/api/v1/echo"
ECHO_PATH_V2 = "/api/v2/echo"

HEALTH_PATH_V1 = "/api/v1/health"
HEALTH_PATH_V2 = "/api/v2/health"

HEALTHZ_PATH_V1 = "/api/v1/healthz"
HEALTHZ_PATH_V2 = "/api/v2/healthz"

HELLO_WORLD = "Hello, world!"

SERVICE_UP = "UP"
SERVICE_DOWN = "DOWN"
SERVICE_IS_UNHEALTHY = "Service is unhealthy"


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI test client fixture."""
    return TestClient(api)


def test_root_endpoint_returns_404(client: TestClient) -> None:
    """Test that the root endpoint returns a 404 status code."""
    response = client.get("/")
    assert response.status_code == 404
    assert "Not Found" in response.json()["detail"]


def test_hello_world_endpoint(client: TestClient) -> None:
    """Test that the hello-world endpoint returns the expected message."""
    response = client.get(HELLO_WORLD_PATH_V1)
    assert response.status_code == 200
    assert response.json()["message"].startswith(HELLO_WORLD)

    response = client.get(HELLO_WORLD_PATH_V2)
    assert response.status_code == 200
    assert response.json()["message"].startswith(HELLO_WORLD)


def test_echo_endpoint_valid_input(client: TestClient) -> None:
    """Test that the echo endpoint returns the input text."""
    test_text = "Test message"

    response = client.post(ECHO_PATH_V1, json={"text": test_text})
    assert response.status_code == 200
    assert response.json() == {"message": test_text}

    response = client.post(ECHO_PATH_V2, json={"utterance": test_text})
    assert response.status_code == 200
    assert response.json() == {"message": test_text}


def test_echo_endpoint_empty_text(client: TestClient) -> None:
    """Test that the echo endpoint validates empty text."""
    response = client.post(ECHO_PATH_V1, json={"text": ""})
    assert response.status_code == 422  # Validation error

    response = client.post(ECHO_PATH_V2, json={"utterance": ""})
    assert response.status_code == 422  # Validation error


def test_echo_endpoint_missing_text(client: TestClient) -> None:
    """Test that the echo endpoint validates missing text field."""
    response = client.post(ECHO_PATH_V1, json={})
    assert response.status_code == 422  # Validation error

    response = client.post(ECHO_PATH_V2, json={})
    assert response.status_code == 422  # Validation error


def test_health_endpoint(client: TestClient) -> None:
    """Test that the health endpoint returns UP status."""
    response = client.get(HEALTH_PATH_V1)
    assert response.status_code == 200
    assert response.json()["status"] == SERVICE_UP
    assert response.json()["reason"] is None

    response = client.get(HEALTH_PATH_V2)
    assert response.status_code == 200
    assert response.json()["status"] == SERVICE_UP
    assert response.json()["reason"] is None

    response = client.get(HEALTHZ_PATH_V1)
    assert response.status_code == 200
    assert response.json()["status"] == SERVICE_UP
    assert response.json()["reason"] is None

    response = client.get(HEALTHZ_PATH_V2)
    assert response.status_code == 200
    assert response.json()["status"] == SERVICE_UP
    assert response.json()["reason"] is None


@patch("aignostics.api.Service")
def test_health_endpoint_down(mock_service, client: TestClient) -> None:
    """Test that the health endpoint returns 500 status when service is unhealthy."""
    # Configure the mock to return unhealthy status
    mock_service_instance = mock_service.return_value
    mock_service_instance.healthy.return_value = False

    response = client.get(HEALTH_PATH_V1)
    assert response.status_code == 500
    assert response.json()["status"] == SERVICE_DOWN
    assert response.json()["reason"] == SERVICE_IS_UNHEALTHY

    response = client.get(HEALTH_PATH_V2)
    assert response.status_code == 500
    assert response.json()["status"] == SERVICE_DOWN
    assert response.json()["reason"] == SERVICE_IS_UNHEALTHY

    response = client.get(HEALTHZ_PATH_V1)
    assert response.status_code == 500
    assert response.json()["status"] == SERVICE_DOWN
    assert response.json()["reason"] == SERVICE_IS_UNHEALTHY

    response = client.get(HEALTHZ_PATH_V2)
    assert response.status_code == 500
    assert response.json()["status"] == SERVICE_DOWN
    assert response.json()["reason"] == SERVICE_IS_UNHEALTHY
