"""Service dependencies for dependency injection."""

from fastapi import Depends

from src.application.services.dashboard_analytics_service import (
    DashboardAnalyticsService,
)
from src.application.services.notification_manager_service import (
    NotificationManagerService,
)
from src.infrastructure.container import (
    container,
    get_appointment_repository,
    get_car_repository,
    get_collector_repository,
    get_driver_repository,
)
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.infrastructure.repositories.car_repository import CarRepository
from src.infrastructure.repositories.collector_repository import (
    CollectorRepository,
)
from src.infrastructure.repositories.driver_repository import DriverRepository


async def get_notification_manager_service() -> NotificationManagerService:
    """Get notification manager service instance."""

    return NotificationManagerService(
        notification_repository=container.notification_repository
    )


async def get_dashboard_analytics_service(
    appointment_repository: AppointmentRepository = Depends(
        get_appointment_repository
    ),
    driver_repository: DriverRepository = Depends(get_driver_repository),
    collector_repository: CollectorRepository = Depends(get_collector_repository),
    car_repository: CarRepository = Depends(get_car_repository),
) -> DashboardAnalyticsService:
    """Provide the dashboard analytics service with Mongo repositories."""

    return DashboardAnalyticsService(
        appointment_repository=appointment_repository,
        driver_repository=driver_repository,
        collector_repository=collector_repository,
        car_repository=car_repository,
    )