"""
Main FastAPI application entry point with Clean Architecture structure.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp

from src.domain.base import DomainException
from src.infrastructure.config import get_settings
from src.infrastructure.container import container
from src.presentation.api.responses import HealthResponse
from src.presentation.api.v1.router import api_v1_router
from src.presentation.exceptions import (
    domain_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    try:
        await container.startup()
        print("✅ Application started successfully")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        raise

    yield

    # Shutdown
    await container.shutdown()
    print("✅ Application shutdown complete")


# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    description="Sistema de agendamento de consultas para clínicas médicas",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# Configure trusted hosts for HTTPS proxy
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.widia.io", "api-staging.widia.io", "clinica-staging.widia.io"]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Add exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]

# Include API routers
app.include_router(api_v1_router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Clinic Appointment System API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if not settings.is_production else None,
        "api": {
            "v1": settings.api_v1_prefix,
        },
    }


@app.get(
    "/health",
    tags=["Health"],
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica a saúde da aplicação e suas dependências",
)
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint with dependency status."""
    # Check MongoDB connection
    mongodb_status = "healthy"
    try:
        await container.mongodb_client.admin.command("ping")
    except Exception:
        mongodb_status = "unhealthy"

    return HealthResponse(
        success=True,
        message="Health check completed",
        status="healthy" if mongodb_status == "healthy" else "degraded",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        request_id=request.headers.get("X-Request-ID"),
        details={
            "mongodb": mongodb_status,
            "debug_mode": settings.debug,
        },
    )


# Middleware for request ID injection
@app.middleware("http")
async def add_request_id(
    request: Request, call_next: Callable[[Request], Any]
) -> Any:
    """Add unique request ID to each request."""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


if __name__ == "__main__":
    # For development only
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
