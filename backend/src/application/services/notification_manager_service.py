"""
Notification manager service for handling system notifications.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.domain.entities.notification import (
    Notification, 
    NotificationType, 
    NotificationPriority
)
from src.domain.entities.user_enhanced import UserEnhanced
from src.domain.repositories.notification_repository_interface import (
    NotificationRepositoryInterface
)
from src.application.dtos.notification_dto import (
    NotificationResponse,
    NotificationListResponse,
    NotificationBadgeResponse,
    CreateNotificationRequest,
    MarkAsReadRequest,
    MarkAsReadResponse,
)
from src.domain.base import DomainException

logger = logging.getLogger(__name__)


class NotificationManagerService:
    """
    Service for managing system notifications (AE-055, AE-056, AE-057).
    
    Handles creation, retrieval, and management of notifications.
    """
    
    def __init__(self, notification_repository: NotificationRepositoryInterface):
        """
        Initialize notification manager.
        
        Args:
            notification_repository: Repository for notifications
        """
        self.notification_repository = notification_repository
    
    async def create_notification(
        self,
        request: CreateNotificationRequest
    ) -> NotificationResponse:
        """
        Create a new notification.
        
        Args:
            request: Notification creation request
            
        Returns:
            Created notification response
        """
        try:
            # Create notification entity
            notification = Notification(
                type=request.type,
                title=request.title,
                message=request.message,
                data=request.data,
                user_id=request.user_id,
                source_user_id=request.source_user_id,
                priority=request.priority,
                action_url=request.action_url,
            )
            
            # Set expiration if specified
            if request.expires_in_hours:
                notification.expires_at = datetime.utcnow() + timedelta(
                    hours=request.expires_in_hours
                )
            
            # Save to repository
            created = await self.notification_repository.create(notification)
            
            logger.info(f"Notification created: {created.id} - {created.type}")
            
            return self._notification_to_response(created)
            
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise DomainException(f"Falha ao criar notificação: {str(e)}")
    
    async def create_user_pending_notification(
        self,
        user: UserEnhanced,
        admin_ids: Optional[List[str]] = None
    ) -> None:
        """
        Create notification for pending user approval.
        
        Args:
            user: User pending approval
            admin_ids: List of admin IDs to notify
        """
        try:
            notification_data = {
                "user_id": user.id,
                "user_email": user.email,
                "user_name": user.name,
                "user_role": user.role.value if user.role else "COLABORADOR",
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            
            # Create global notification for all admins if no specific IDs
            if not admin_ids:
                notification = Notification(
                    type=NotificationType.USER_PENDING_APPROVAL,
                    title="Nova Solicitação de Cadastro",
                    message=f"Usuário {user.name} ({user.email}) aguarda aprovação",
                    data=notification_data,
                    source_user_id=user.id,
                    priority=NotificationPriority.HIGH,
                    action_url=f"/admin/users/{user.id}/review",
                )
                await self.notification_repository.create(notification)
            else:
                # Create individual notifications for each admin
                for admin_id in admin_ids:
                    notification = Notification(
                        type=NotificationType.USER_PENDING_APPROVAL,
                        title="Nova Solicitação de Cadastro",
                        message=f"Usuário {user.name} ({user.email}) aguarda aprovação",
                        data=notification_data,
                        user_id=admin_id,
                        source_user_id=user.id,
                        priority=NotificationPriority.HIGH,
                        action_url=f"/admin/users/{user.id}/review",
                    )
                    await self.notification_repository.create(notification)
            
            logger.info(f"Pending approval notification created for user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to create pending notification: {e}")
    
    async def get_notifications(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> NotificationListResponse:
        """
        Get notifications for a user (AE-056).
        
        Args:
            user_id: User ID to get notifications for
            limit: Pagination limit
            offset: Pagination offset
            unread_only: Only return unread notifications
            
        Returns:
            List of notifications
        """
        try:
            if unread_only and user_id:
                notifications = await self.notification_repository.get_unread_for_user(
                    user_id, limit, offset
                )
                total = await self.notification_repository.count_unread(user_id)
            elif user_id:
                notifications = await self.notification_repository.get_all_for_user(
                    user_id, limit, offset, include_read=not unread_only
                )
                total = len(notifications)  # Simplified count
            else:
                # Admin view - all notifications
                notifications = await self.notification_repository.get_by_type(
                    NotificationType.USER_PENDING_APPROVAL, limit, offset
                )
                total = await self.notification_repository.count_by_type(
                    NotificationType.USER_PENDING_APPROVAL
                )
            
            return NotificationListResponse(
                notifications=[
                    self._notification_to_response(n) for n in notifications
                ],
                total=total,
                offset=offset,
                limit=limit,
                has_more=(offset + limit) < total
            )
            
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            raise DomainException(f"Falha ao buscar notificações: {str(e)}")
    
    async def get_badge_data(
        self,
        user_id: Optional[str] = None
    ) -> NotificationBadgeResponse:
        """
        Get badge data for notification indicators (AE-055).
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Badge data with counts
        """
        try:
            # Get base badge data from repository
            badge_data = await self.notification_repository.get_badge_data(user_id)
            
            # Count specific notification types
            pending_count = await self.notification_repository.count_by_type(
                NotificationType.USER_PENDING_APPROVAL, user_id
            )
            
            return NotificationBadgeResponse(
                total_unread=badge_data.get("total_unread", 0),
                pending_approvals=badge_data.get("pending_approvals", 0),
                high_priority=badge_data.get("high_priority", 0),
                user_pending=pending_count,
                emails_unverified=0,  # TODO: Implement when needed
                system_alerts=0,  # TODO: Implement when needed
            )
            
        except Exception as e:
            logger.error(f"Failed to get badge data: {e}")
            return NotificationBadgeResponse(
                total_unread=0,
                pending_approvals=0,
                high_priority=0,
            )
    
    async def mark_as_read(
        self,
        user_id: str,
        request: MarkAsReadRequest
    ) -> MarkAsReadResponse:
        """
        Mark notifications as read (AE-057).
        
        Args:
            user_id: User marking notifications
            request: Mark as read request
            
        Returns:
            Operation result
        """
        try:
            if request.mark_all:
                # Mark all as read
                count = await self.notification_repository.mark_all_as_read(user_id)
                return MarkAsReadResponse(
                    success=True,
                    count=count,
                    message=f"{count} notificações marcadas como lidas"
                )
            elif request.notification_ids:
                # Mark specific notifications
                count = 0
                for notification_id in request.notification_ids:
                    if await self.notification_repository.mark_as_read(
                        notification_id, user_id
                    ):
                        count += 1
                
                return MarkAsReadResponse(
                    success=count > 0,
                    count=count,
                    message=f"{count} notificações marcadas como lidas"
                )
            else:
                return MarkAsReadResponse(
                    success=False,
                    count=0,
                    message="Nenhuma notificação especificada"
                )
                
        except Exception as e:
            logger.error(f"Failed to mark as read: {e}")
            raise DomainException(f"Falha ao marcar como lida: {str(e)}")
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification to delete
            user_id: User requesting deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            # Verify ownership or admin status before deletion
            notification = await self.notification_repository.get_by_id(notification_id)
            if not notification:
                return False
            
            # Check if user can delete (owner or admin)
            if notification.user_id != user_id:
                # TODO: Check if user is admin
                pass
            
            return await self.notification_repository.delete(notification_id)
            
        except Exception as e:
            logger.error(f"Failed to delete notification: {e}")
            return False
    
    async def cleanup_expired(self) -> int:
        """
        Clean up expired notifications.
        
        Returns:
            Number of notifications deleted
        """
        try:
            count = await self.notification_repository.delete_expired()
            if count > 0:
                logger.info(f"Cleaned up {count} expired notifications")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup notifications: {e}")
            return 0
    
    def _notification_to_response(
        self,
        notification: Notification
    ) -> NotificationResponse:
        """
        Convert notification entity to response DTO.
        
        Args:
            notification: Notification entity
            
        Returns:
            Notification response DTO
        """
        return NotificationResponse(
            id=notification.id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            source_user_id=notification.source_user_id,
            read=notification.read,
            read_at=notification.read_at,
            priority=notification.priority,
            created_at=notification.created_at,
            action_url=notification.action_url,
        )