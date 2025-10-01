"""
Main router for API v1 endpoints.
"""

from typing import Any

from fastapi import APIRouter

from src.infrastructure.config import get_settings

# Import and include routers
from src.presentation.api.v1.endpoints import (
    admin,
    appointments,
    auth,
    cars,
    clients,
    collectors,
    drivers,
    jobs,
    logistics_packages,
    notifications,
    reports,
    tags,
)

# Get settings
settings = get_settings()

# Create main API v1 router
api_v1_router = APIRouter(
    prefix=settings.api_v1_prefix,
    tags=["v1"],
)

# Include routers
api_v1_router.include_router(
    auth.router, prefix="/auth", tags=["Authentication"]
)

api_v1_router.include_router(
    admin.router, tags=["Admin"]  # No prefix, already has /admin
)

api_v1_router.include_router(
    appointments.router, prefix="/appointments", tags=["Appointments"]
)

api_v1_router.include_router(
    drivers.router, prefix="/drivers", tags=["Drivers"]
)

api_v1_router.include_router(
    collectors.router, prefix="/collectors", tags=["Collectors"]
)

api_v1_router.include_router(
    clients.router, prefix="/clients", tags=["Clients"]
)

api_v1_router.include_router(cars.router, prefix="/cars", tags=["Cars"])

api_v1_router.include_router(
    logistics_packages.router,
    prefix="/logistics-packages",
    tags=["Logistics Packages"],
)

api_v1_router.include_router(
    reports.router, prefix="/reports", tags=["Reports"]
)

api_v1_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)

api_v1_router.include_router(tags.router, prefix="/tags", tags=["Tags"])

api_v1_router.include_router(jobs.router, tags=["Background Jobs"])


@api_v1_router.get("/")
async def api_v1_root() -> dict[str, Any]:
    """API v1 root endpoint."""
    return {
        "message": "Clinic Appointment System API v1",
        "version": "1.0.0",
        "endpoints": {
            "docs": f"{settings.api_v1_prefix}/docs",
            "health": f"{settings.api_v1_prefix}/health",
            "auth": f"{settings.api_v1_prefix}/auth",
            "admin": f"{settings.api_v1_prefix}/admin",
            "appointments": f"{settings.api_v1_prefix}/appointments",
            "drivers": f"{settings.api_v1_prefix}/drivers",
            "collectors": f"{settings.api_v1_prefix}/collectors",
            "clients": f"{settings.api_v1_prefix}/clients",
            "cars": f"{settings.api_v1_prefix}/cars",
            "logistics_packages": f"{settings.api_v1_prefix}/logistics-packages",
            "reports": f"{settings.api_v1_prefix}/reports",
            "notifications": f"{settings.api_v1_prefix}/notifications",
        },
    }
