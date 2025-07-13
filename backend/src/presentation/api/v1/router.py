"""
Main router for API v1 endpoints.
"""

from typing import Any

from fastapi import APIRouter

from src.infrastructure.config import get_settings

# Get settings
settings = get_settings()

# Create main API v1 router
api_v1_router = APIRouter(
    prefix=settings.api_v1_prefix,
    tags=["v1"],
)

# Import and include routers here as they are created
# Example:
# from src.presentation.api.v1.endpoints import auth, appointments, patients
# api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_v1_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
# api_v1_router.include_router(patients.router, prefix="/patients", tags=["Patients"])


@api_v1_router.get("/")
async def api_v1_root() -> dict[str, Any]:
    """API v1 root endpoint."""
    return {
        "message": "Clinic Appointment System API v1",
        "version": "1.0.0",
        "endpoints": {
            "docs": f"{settings.api_v1_prefix}/docs",
            "health": f"{settings.api_v1_prefix}/health",
        },
    }
