"""
Tests for the main FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient

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
    assert data["docs"] == "/docs"


def test_health_check_endpoint(client: TestClient) -> None:
    """Test the health check endpoint returns correct response."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "clinic-appointment-api"
    assert data["version"] == "1.0.0"
    assert "environment" in data


def test_api_status_endpoint(client: TestClient) -> None:
    """Test the API status endpoint returns correct response."""
    response = client.get("/api/v1/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "operational"
    assert data["message"] == "API is running properly"


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
    assert data["info"]["description"] == "Sistema de agendamento de consultas para clínicas médicas"


def test_cors_headers_present(client: TestClient) -> None:
    """Test that CORS headers are properly configured."""
    # Test with a regular GET request to see CORS headers
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    
    # Should respond normally and include CORS headers
    assert response.status_code == 200


def test_invalid_endpoint_returns_404(client: TestClient) -> None:
    """Test that invalid endpoints return 404."""
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404