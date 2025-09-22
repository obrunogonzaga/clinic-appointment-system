"""
Notification endpoints for dashboard notifications (AE-055, AE-056, AE-057).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.notification_dto import (
    NotificationResponse,
    NotificationListResponse,
    NotificationBadgeResponse,
    CreateNotificationRequest,
    MarkAsReadRequest,
    MarkAsReadResponse,
)
from src.application.services.notification_manager_service import (
    NotificationManagerService
)
from src.domain.base import DomainException
from src.domain.entities.user import User
from src.presentation.api.responses import SuccessResponse
from src.presentation.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user,
)
from src.presentation.dependencies.services import (
    get_notification_manager_service
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/badge",
    response_model=NotificationBadgeResponse,
    summary="Get Badge Data (AE-055)",
    description="Get notification badge data for header display",
)
async def get_badge_data(
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> NotificationBadgeResponse:
    """Get notification badge data for current user."""
    try:
        # Admin users see all notifications, regular users see their own
        user_id = None if current_user.is_admin else current_user.id
        return await notification_service.get_badge_data(user_id)
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List Notifications (AE-056)",
    description="Get paginated list of notifications",
)
async def list_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> NotificationListResponse:
    """Get notifications for current user."""
    try:
        # Admin users see all notifications, regular users see their own
        user_id = None if current_user.is_admin else current_user.id
        
        return await notification_service.get_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get Notification",
    description="Get a specific notification by ID",
)
async def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> NotificationResponse:
    """Get a specific notification."""
    try:
        # TODO: Implement get single notification
        # For now, get list and filter
        notifications = await notification_service.get_notifications(
            user_id=current_user.id,
            limit=100,
            offset=0
        )
        
        for notif in notifications.notifications:
            if notif.id == notification_id:
                return notif
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/{notification_id}/read",
    response_model=MarkAsReadResponse,
    summary="Mark as Read (AE-057)",
    description="Mark a specific notification as read",
)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> MarkAsReadResponse:
    """Mark a notification as read."""
    try:
        request = MarkAsReadRequest(notification_ids=[notification_id])
        return await notification_service.mark_as_read(
            user_id=current_user.id,
            request=request
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/read-all",
    response_model=MarkAsReadResponse,
    summary="Mark All as Read (AE-057)",
    description="Mark all notifications as read for current user",
)
async def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> MarkAsReadResponse:
    """Mark all notifications as read."""
    try:
        request = MarkAsReadRequest(mark_all=True)
        return await notification_service.mark_as_read(
            user_id=current_user.id,
            request=request
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/mark-read",
    response_model=MarkAsReadResponse,
    summary="Mark Multiple as Read",
    description="Mark multiple notifications as read",
)
async def mark_multiple_read(
    request: MarkAsReadRequest,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> MarkAsReadResponse:
    """Mark multiple notifications as read."""
    try:
        return await notification_service.mark_as_read(
            user_id=current_user.id,
            request=request
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/{notification_id}",
    response_model=SuccessResponse,
    summary="Delete Notification",
    description="Delete a specific notification",
)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> SuccessResponse:
    """Delete a notification."""
    try:
        success = await notification_service.delete_notification(
            notification_id=notification_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificação não encontrada"
            )
        
        return SuccessResponse(
            success=True,
            message="Notificação deletada com sucesso"
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "",
    response_model=NotificationResponse,
    summary="Create Notification (Admin)",
    description="Create a new notification (admin only)",
    dependencies=[Depends(get_current_admin_user)],
)
async def create_notification(
    request: CreateNotificationRequest,
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> NotificationResponse:
    """Create a new notification (admin only)."""
    try:
        return await notification_service.create_notification(request)
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/cleanup",
    response_model=SuccessResponse,
    summary="Cleanup Expired (Admin)",
    description="Delete expired notifications (admin only)",
    dependencies=[Depends(get_current_admin_user)],
)
async def cleanup_notifications(
    notification_service: NotificationManagerService = Depends(
        get_notification_manager_service
    ),
) -> SuccessResponse:
    """Cleanup expired notifications."""
    try:
        count = await notification_service.cleanup_expired()
        
        return SuccessResponse(
            success=True,
            message=f"{count} notificações expiradas removidas"
        )
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )