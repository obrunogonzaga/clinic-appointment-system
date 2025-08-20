"""
Tests for the main FastAPI application.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Import app after conftest sets up the mocks
from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint returns correct response."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Welcome to Clinic Appointment System API"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "testing"
    assert data["docs"] == "/docs"
    assert data["api"]["v1"] == "/api/v1"


def test_health_check_endpoint(client: TestClient, mock_container) -> None:
    """Test the health check endpoint returns correct response."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "Clinic Appointment System API"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "testing"
    assert data["success"] is True
    assert data["details"]["mongodb"] == "healthy"
    assert data["details"]["debug_mode"] is True


def test_api_v1_root_endpoint(client: TestClient) -> None:
    """Test the API v1 root endpoint returns correct response."""
    response = client.get("/api/v1/")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Clinic Appointment System API v1"
    assert data["version"] == "1.0.0"
    assert data["endpoints"]["docs"] == "/api/v1/docs"
    assert data["endpoints"]["health"] == "/api/v1/health"


def test_docs_endpoint_accessible(client: TestClient) -> None:
    """Test that the API documentation endpoint is accessible."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_json_endpoint(client: TestClient) -> None:
    """Test that the OpenAPI JSON schema is accessible."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert data["info"]["title"] == "Clinic Appointment System API"
    assert data["info"]["version"] == "1.0.0"
    assert (
        data["info"]["description"]
        == "Sistema de agendamento de consultas para clínicas médicas"
    )


def test_cors_headers_present(client: TestClient) -> None:
    """Test that CORS headers are properly configured."""
    # Test with a regular GET request to see CORS headers
    response = client.get("/", headers={"Origin": "http://localhost:3000"})

    # Should respond normally and include CORS headers
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "x-request-id" in response.headers


def test_invalid_endpoint_returns_404(client: TestClient) -> None:
    """Test that invalid endpoints return 404."""
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    # The error message might be in English or Portuguese depending on the exception handler
    assert (
        "not found" in data["message"].lower()
        or "não encontrado" in data["message"].lower()
    )


def test_health_check_mongodb_unhealthy(
    client: TestClient, mock_container
) -> None:
    """Test health check when MongoDB is unavailable."""
    # Mock MongoDB client to simulate connection failure
    mock_admin = MagicMock()
    mock_admin.command = AsyncMock(side_effect=Exception("Connection failed"))
    mock_container.mongodb_client.admin = mock_admin

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"
    assert data["details"]["mongodb"] == "unhealthy"


def test_request_id_header_added(client: TestClient) -> None:
    """Test that request ID header is added to responses."""
    # First request without X-Request-ID
    response = client.get("/")
    assert "x-request-id" in response.headers
    request_id_1 = response.headers["x-request-id"]

    # Second request with custom X-Request-ID
    custom_id = "test-request-123"
    response = client.get("/", headers={"X-Request-ID": custom_id})
    assert response.headers["x-request-id"] == custom_id

    # Verify different requests get different IDs
    response = client.get("/")
    request_id_2 = response.headers["x-request-id"]
    assert request_id_1 != request_id_2


def test_validation_error_handling(client: TestClient) -> None:
    """Test that validation errors are properly handled."""
    # This will be more useful when we have endpoints with validation
    # For now, we test with a POST to a non-existent endpoint
    response = client.post("/api/v1/invalid", json={"invalid": "data"})

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
