"""
Service dependencies for dependency injection.
"""

from src.application.services.notification_manager_service import (
    NotificationManagerService
)
from src.infrastructure.container import container


async def get_notification_manager_service() -> NotificationManagerService:
    """
    Get notification manager service instance.
    
    Returns:
        NotificationManagerService instance
    """
    return NotificationManagerService(
        notification_repository=container.notification_repository
    )