"""
Global exception handlers and error response models for the API.
"""

from typing import Any, Dict, List, Optional, Union, cast

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.base import (
    DomainException,
    DomainValidationException,
    EntityNotFoundException,
)


class ErrorDetail(BaseModel):
    """Error detail information."""

    field: Optional[str] = Field(None, description="Campo com erro")
    message: str = Field(..., description="Mensagem de erro")
    code: Optional[str] = Field(None, description="Código do erro")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = Field(False, description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de erro principal")
    errors: Optional[List[ErrorDetail]] = Field(
        None,
        description="Lista detalhada de erros",
    )
    request_id: Optional[str] = Field(
        None,
        description="ID único da requisição para rastreamento",
    )


def create_error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        message: Main error message
        status_code: HTTP status code
        errors: List of detailed errors
        request_id: Request ID for tracking

    Returns:
        JSONResponse: Formatted error response
    """
    error_response = ErrorResponse(
        success=False,
        message=message,
        errors=errors,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(exclude_none=True),
    )


async def domain_exception_handler(
    request: Request,
    exc: Exception,  # Will be DomainException at runtime
) -> JSONResponse:
    """
    Handle domain exceptions.

    Args:
        request: FastAPI request
        exc: Domain exception

    Returns:
        JSONResponse: Error response
    """
    # Cast to DomainException since we know it will be at runtime
    domain_exc = cast(DomainException, exc)
    status_code = status.HTTP_400_BAD_REQUEST

    if isinstance(exc, EntityNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DomainValidationException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    errors = None
    if isinstance(exc, DomainValidationException) and exc.field:
        errors = [
            ErrorDetail(
                field=exc.field,
                message=str(exc),
                code=exc.code,
            )
        ]

    return create_error_response(
        message=str(domain_exc),
        status_code=status_code,
        errors=errors,
        request_id=request.headers.get("X-Request-ID"),
    )


async def http_exception_handler(
    request: Request,
    exc: Union[HTTPException, StarletteHTTPException],
) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSONResponse: Error response
    """
    return create_error_response(
        message=exc.detail if hasattr(exc, "detail") else str(exc),
        status_code=exc.status_code,
        request_id=request.headers.get("X-Request-ID"),
    )


async def validation_exception_handler(
    request: Request,
    exc: Exception,  # Will be RequestValidationError at runtime
) -> JSONResponse:
    """
    Handle validation exceptions from Pydantic.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        JSONResponse: Error response with detailed validation errors
    """
    # Cast to RequestValidationError since we know it will be at runtime
    validation_exc = cast(RequestValidationError, exc)
    errors = []
    for error in validation_exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        errors.append(
            ErrorDetail(
                field=field_path or None,
                message=error["msg"],
                code=error["type"],
            )
        )

    return create_error_response(
        message="Erro de validação nos dados enviados",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors,
        request_id=request.headers.get("X-Request-ID"),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle general uncaught exceptions.

    Args:
        request: FastAPI request
        exc: Any exception

    Returns:
        JSONResponse: Error response
    """
    # Log the exception details here
    # In production, you might want to hide internal error details

    return create_error_response(
        message="Erro interno do servidor",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request.headers.get("X-Request-ID"),
    )


class APIException(HTTPException):
    """
    Custom API exception with standardized error format.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        errors: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize API exception.

        Args:
            status_code: HTTP status code
            message: Error message
            errors: List of detailed errors
            headers: Optional HTTP headers
        """
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.errors = errors


class BadRequestException(APIException):
    """Bad request exception (400)."""

    def __init__(
        self,
        message: str = "Requisição inválida",
        errors: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            errors=errors,
        )


class UnauthorizedException(APIException):
    """Unauthorized exception (401)."""

    def __init__(
        self,
        message: str = "Não autorizado",
        errors: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            errors=errors,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(APIException):
    """Forbidden exception (403)."""

    def __init__(
        self,
        message: str = "Acesso negado",
        errors: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            errors=errors,
        )


class NotFoundException(APIException):
    """Not found exception (404)."""

    def __init__(
        self,
        message: str = "Recurso não encontrado",
        errors: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            errors=errors,
        )


class ConflictException(APIException):
    """Conflict exception (409)."""

    def __init__(
        self,
        message: str = "Conflito com o estado atual",
        errors: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            errors=errors,
        )
