"""
Pytest configuration and shared fixtures.
"""

import os
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing any application code
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["DATABASE_NAME"] = "test_clinic_db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(autouse=True)
def mock_container():
    """Automatically mock the container for all tests."""
    with patch("src.infrastructure.container.container") as mock:
        # Setup container mock
        mock.startup = AsyncMock()
        mock.shutdown = AsyncMock()
        mock.mongodb_client = MagicMock()
        mock.database = MagicMock()

        # Mock MongoDB client methods
        mock_admin = MagicMock()
        mock_admin.command = AsyncMock(return_value={"ok": 1})
        mock.mongodb_client.admin = mock_admin

        yield mock
