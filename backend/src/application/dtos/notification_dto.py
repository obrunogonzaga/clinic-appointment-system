"""
DTOs for notification system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.domain.entities.notification import NotificationType, NotificationPriority


class NotificationResponse(BaseModel):
    """DTO for notification response."""
    
    id: str = Field(..., description="Notification ID")
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional data")
    
    source_user_id: Optional[str] = Field(None, description="Source user ID")
    read: bool = Field(..., description="Read status")
    read_at: Optional[datetime] = Field(None, description="When it was read")
    
    priority: NotificationPriority = Field(..., description="Priority level")
    created_at: datetime = Field(..., description="Creation timestamp")
    action_url: Optional[str] = Field(None, description="Action URL")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationListResponse(BaseModel):
    """DTO for paginated notification list."""
    
    notifications: List[NotificationResponse] = Field(
        ..., description="List of notifications"
    )
    total: int = Field(..., description="Total count")
    offset: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    has_more: bool = Field(..., description="Whether there are more notifications")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationBadgeResponse(BaseModel):
    """DTO for notification badge data (AE-055)."""
    
    total_unread: int = Field(..., description="Total unread notifications")
    pending_approvals: int = Field(..., description="Pending user approvals")
    high_priority: int = Field(..., description="High priority notifications")
    
    # Additional counts for different types
    user_pending: int = Field(0, description="Users pending approval")
    emails_unverified: int = Field(0, description="Unverified email addresses")
    system_alerts: int = Field(0, description="System alerts")
    
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="When badge data was last updated"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarkAsReadRequest(BaseModel):
    """DTO for marking notifications as read."""
    
    notification_ids: Optional[List[str]] = Field(
        None, 
        description="List of notification IDs to mark as read"
    )
    mark_all: bool = Field(
        False, 
        description="Mark all notifications as read"
    )


class MarkAsReadResponse(BaseModel):
    """DTO for mark as read response."""
    
    success: bool = Field(..., description="Operation success")
    count: int = Field(..., description="Number of notifications marked")
    message: str = Field(..., description="Response message")


class CreateNotificationRequest(BaseModel):
    """DTO for creating a notification."""
    
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional data")
    
    user_id: Optional[str] = Field(
        None, 
        description="Target user ID (None for global)"
    )
    source_user_id: Optional[str] = Field(
        None,
        description="Source user ID"
    )
    
    priority: NotificationPriority = Field(
        default=NotificationPriority.MEDIUM,
        description="Priority level"
    )
    action_url: Optional[str] = Field(None, description="Action URL")
    expires_in_hours: Optional[int] = Field(
        None,
        description="Expiration time in hours"
    )


class NotificationFilterRequest(BaseModel):
    """DTO for filtering notifications."""
    
    type: Optional[NotificationType] = Field(None, description="Filter by type")
    priority: Optional[NotificationPriority] = Field(None, description="Filter by priority")
    read: Optional[bool] = Field(None, description="Filter by read status")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    limit: int = Field(50, ge=1, le=100, description="Pagination limit")
    offset: int = Field(0, ge=0, description="Pagination offset")