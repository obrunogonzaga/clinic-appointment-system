"""
Tests for exception handlers.
"""

import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.base import (
    DomainException,
    DomainValidationException,
    EntityNotFoundException,
)
from src.presentation.exceptions import (
    ErrorResponse,
    domain_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


@pytest.mark.asyncio
async def test_domain_exception_handler():
    """Test domain exception handler."""
    exception = DomainException("Erro de domínio", code="DOMAIN_ERROR")
    request = Request({"type": "http", "headers": {}}, receive=None, send=None)

    response = await domain_exception_handler(request, exception)

    assert response.status_code == 400
    content = response.body.decode()
    assert "Erro de domínio" in content
    # Error code is not included in the response by default


@pytest.mark.asyncio
async def test_http_exception_handler():
    """Test HTTP exception handler."""
    exception = StarletteHTTPException(status_code=404, detail="Resource not found")
    request = Request({"type": "http", "headers": {}}, receive=None, send=None)

    response = await http_exception_handler(request, exception)

    assert response.status_code == 404
    content = response.body.decode()
    assert "not found" in content.lower()


@pytest.mark.asyncio
async def test_validation_exception_handler():
    """Test validation exception handler."""
    # Create a mock validation error with proper structure
    mock_errors = [
        {
            "loc": ("body", "name"),
            "msg": "String should have at least 3 characters",
            "type": "string_too_short",
        },
        {
            "loc": ("body", "age"),
            "msg": "Input should be greater than 0",
            "type": "greater_than",
        },
    ]

    class MockValidationError:
        def errors(self):
            return mock_errors

    exception = RequestValidationError(errors=mock_errors)
    exception._errors = mock_errors  # Set the internal errors
    request = Request({"type": "http", "headers": {}}, receive=None, send=None)

    response = await validation_exception_handler(request, exception)

    assert response.status_code == 422
    content = response.body.decode()
    assert "validação" in content.lower()


def test_entity_not_found_exception():
    """Test EntityNotFoundException exception."""
    error = EntityNotFoundException("User", "123")
    assert "User" in str(error)
    assert "123" in str(error)
    assert error.code == "ENTITY_NOT_FOUND"


def test_domain_validation_exception():
    """Test DomainValidationException exception."""
    error = DomainValidationException("Invalid data", field="email")
    assert str(error) == "Invalid data"
    assert error.code == "VALIDATION_ERROR"
    assert error.field == "email"
