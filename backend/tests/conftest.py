"""
Pytest configuration and shared fixtures.
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Set up test environment variables."""
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "true"

    yield

    # Cleanup after tests
    # Remove test environment variables if needed
    pass


@pytest.fixture(scope="session")
def test_app() -> TestClient:
    """Create a test client for the entire test session."""
    from src.main import app

    return TestClient(app)
