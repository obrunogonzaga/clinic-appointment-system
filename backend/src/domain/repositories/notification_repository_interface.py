"""
Notification repository interface for system notifications.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.domain.entities.notification import Notification, NotificationType


class NotificationRepositoryInterface(ABC):
    """
    Interface for notification repository operations.
    
    Defines contract for notification data access.
    """
    
    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        """
        Create a new notification.
        
        Args:
            notification: Notification to create
            
        Returns:
            Created notification with ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """
        Get notification by ID.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Notification if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_unread_for_user(
        self, 
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get unread notifications for a user.
        
        Args:
            user_id: User ID to get notifications for
            limit: Maximum number of notifications
            offset: Pagination offset
            
        Returns:
            List of unread notifications
        """
        pass
    
    @abstractmethod
    async def get_all_for_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_read: bool = True
    ) -> List[Notification]:
        """
        Get all notifications for a user.
        
        Args:
            user_id: User ID to get notifications for
            limit: Maximum number of notifications
            offset: Pagination offset
            include_read: Whether to include read notifications
            
        Returns:
            List of notifications
        """
        pass
    
    @abstractmethod
    async def get_by_type(
        self,
        notification_type: NotificationType,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get notifications by type.
        
        Args:
            notification_type: Type of notification
            limit: Maximum number of notifications
            offset: Pagination offset
            
        Returns:
            List of notifications of given type
        """
        pass
    
    @abstractmethod
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User marking as read
            
        Returns:
            True if marked successfully
        """
        pass
    
    @abstractmethod
    async def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        pass
    
    @abstractmethod
    async def delete(self, notification_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def delete_expired(self) -> int:
        """
        Delete all expired notifications.
        
        Returns:
            Number of notifications deleted
        """
        pass
    
    @abstractmethod
    async def count_unread(self, user_id: Optional[str] = None) -> int:
        """
        Count unread notifications.
        
        Args:
            user_id: Optional user ID to count for
            
        Returns:
            Count of unread notifications
        """
        pass
    
    @abstractmethod
    async def count_by_type(
        self,
        notification_type: NotificationType,
        user_id: Optional[str] = None
    ) -> int:
        """
        Count notifications by type.
        
        Args:
            notification_type: Type to count
            user_id: Optional user ID to filter
            
        Returns:
            Count of notifications
        """
        pass
    
    @abstractmethod
    async def get_badge_data(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get badge data for notification indicators.
        
        Args:
            user_id: Optional user ID to filter
            
        Returns:
            Dictionary with counts by category
        """
        pass
    
    @abstractmethod
    async def create_indexes(self) -> None:
        """
        Create database indexes for optimal performance.
        """
        pass