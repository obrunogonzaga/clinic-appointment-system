"""
Notification entity for system notifications (AE-055, AE-056, AE-057).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Types of notifications in the system."""
    
    USER_PENDING_APPROVAL = "user_pending_approval"
    USER_APPROVED = "user_approved"
    USER_REJECTED = "user_rejected"
    EMAIL_VERIFIED = "email_verified"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKED = "account_locked"
    SYSTEM_ALERT = "system_alert"
    INFO = "info"


class NotificationPriority(str, Enum):
    """Priority levels for notifications."""
    
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Notification(BaseModel):
    """
    Notification entity for system-wide notifications.
    
    Used to track important events and display them in the admin dashboard.
    """
    
    id: Optional[str] = Field(None, description="Unique notification ID")
    type: NotificationType = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional data payload"
    )
    
    # Target and source
    user_id: Optional[str] = Field(
        None, 
        description="Target user ID (admin who should see this)"
    )
    source_user_id: Optional[str] = Field(
        None,
        description="Source user ID (user who triggered the notification)"
    )
    
    # Read status
    read: bool = Field(False, description="Whether notification has been read")
    read_at: Optional[datetime] = Field(None, description="When notification was read")
    read_by: Optional[str] = Field(None, description="Who marked it as read")
    
    # Metadata
    priority: NotificationPriority = Field(
        default=NotificationPriority.MEDIUM,
        description="Notification priority"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When notification was created"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="When notification expires and should be auto-deleted"
    )
    
    # Action URL
    action_url: Optional[str] = Field(
        None,
        description="URL to navigate when notification is clicked"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def mark_as_read(self, user_id: str) -> None:
        """
        Mark notification as read.
        
        Args:
            user_id: ID of user marking as read
        """
        self.read = True
        self.read_at = datetime.utcnow()
        self.read_by = user_id
    
    def is_expired(self) -> bool:
        """
        Check if notification has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert notification to dictionary.
        
        Returns:
            Dictionary representation
        """
        return self.model_dump(exclude_none=True)