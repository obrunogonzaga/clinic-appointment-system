"""Service dependencies for dependency injection."""

from fastapi import Depends

from src.application.services.dashboard_analytics_service import (
    DashboardAnalyticsService,
)
from src.application.services.notification_manager_service import (
    NotificationManagerService,
)
from src.application.services.patient_document_service import (
    PatientDocumentService,
)
from src.infrastructure.container import (
    container,
    get_appointment_repository,
    get_car_repository,
    get_collector_repository,
    get_driver_repository,
    get_patient_document_repository,
    get_r2_storage_service,
    get_app_settings,
)
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.infrastructure.repositories.car_repository import CarRepository
from src.infrastructure.repositories.collector_repository import (
    CollectorRepository,
)
from src.infrastructure.repositories.driver_repository import DriverRepository
from src.infrastructure.repositories.patient_document_repository import (
    PatientDocumentRepository,
)
from src.infrastructure.services.r2_storage_service import R2StorageService
from src.infrastructure.config import Settings


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


async def get_patient_document_service(
    document_repository: PatientDocumentRepository = Depends(
        get_patient_document_repository
    ),
    appointment_repository: AppointmentRepository = Depends(
        get_appointment_repository
    ),
    storage_service: R2StorageService = Depends(get_r2_storage_service),
    settings: Settings = Depends(get_app_settings),
) -> PatientDocumentService:
    """Provide patient document service wired with repositories and storage."""

    return PatientDocumentService(
        document_repository=document_repository,
        appointment_repository=appointment_repository,
        storage_service=storage_service,
        settings=settings,
    )