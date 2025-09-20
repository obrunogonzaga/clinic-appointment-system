"""
MongoDB implementation of notification repository.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import IndexModel, DESCENDING

from src.domain.entities.notification import Notification, NotificationType
from src.domain.repositories.notification_repository_interface import (
    NotificationRepositoryInterface
)
from src.domain.base import DomainException


class NotificationRepository(NotificationRepositoryInterface):
    """
    MongoDB implementation of notification repository.
    
    Handles notification persistence and retrieval.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize repository with database connection.
        
        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection: AsyncIOMotorCollection = database.notifications
    
    async def create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        indexes = [
            # Single field indexes
            IndexModel([("user_id", 1)], name="user_id_idx"),
            IndexModel([("source_user_id", 1)], name="source_user_id_idx"),
            IndexModel([("type", 1)], name="type_idx"),
            IndexModel([("read", 1)], name="read_idx"),
            IndexModel([("priority", 1)], name="priority_idx"),
            IndexModel([("created_at", DESCENDING)], name="created_at_desc_idx"),
            IndexModel([("expires_at", 1)], sparse=True, name="expires_at_idx"),
            
            # Compound indexes for common queries
            IndexModel(
                [("user_id", 1), ("read", 1), ("created_at", DESCENDING)],
                name="user_unread_compound_idx"
            ),
            IndexModel(
                [("type", 1), ("read", 1), ("created_at", DESCENDING)],
                name="type_unread_compound_idx"
            ),
            IndexModel(
                [("user_id", 1), ("type", 1), ("read", 1)],
                name="user_type_read_compound_idx"
            ),
        ]
        await self.collection.create_indexes(indexes)
    
    async def create(self, notification: Notification) -> Notification:
        """Create a new notification."""
        try:
            # Prepare notification data
            notification_dict = notification.model_dump(by_alias=True, exclude={"id"})
            notification_dict["_id"] = ObjectId()
            
            # Insert notification
            result = await self.collection.insert_one(notification_dict)
            
            # Return with populated ID
            notification.id = str(result.inserted_id)
            return notification
            
        except Exception as e:
            raise DomainException(f"Failed to create notification: {str(e)}")
    
    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        try:
            if not ObjectId.is_valid(notification_id):
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(notification_id)})
            return self._doc_to_notification(doc) if doc else None
            
        except Exception:
            return None
    
    async def get_unread_for_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """Get unread notifications for a user."""
        try:
            # Query for unread notifications
            query = {
                "$or": [
                    {"user_id": user_id},
                    {"user_id": None}  # Global notifications
                ],
                "read": False
            }
            
            cursor = self.collection.find(query).sort(
                [("priority", -1), ("created_at", -1)]
            ).skip(offset).limit(limit)
            
            notifications = []
            async for doc in cursor:
                notification = self._doc_to_notification(doc)
                if notification:
                    notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            raise DomainException(f"Failed to get unread notifications: {str(e)}")
    
    async def get_all_for_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_read: bool = True
    ) -> List[Notification]:
        """Get all notifications for a user."""
        try:
            # Build query
            query = {
                "$or": [
                    {"user_id": user_id},
                    {"user_id": None}  # Global notifications
                ]
            }
            
            if not include_read:
                query["read"] = False
            
            cursor = self.collection.find(query).sort(
                "created_at", -1
            ).skip(offset).limit(limit)
            
            notifications = []
            async for doc in cursor:
                notification = self._doc_to_notification(doc)
                if notification:
                    notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            raise DomainException(f"Failed to get notifications: {str(e)}")
    
    async def get_by_type(
        self,
        notification_type: NotificationType,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications by type."""
        try:
            cursor = self.collection.find(
                {"type": notification_type.value}
            ).sort("created_at", -1).skip(offset).limit(limit)
            
            notifications = []
            async for doc in cursor:
                notification = self._doc_to_notification(doc)
                if notification:
                    notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            raise DomainException(f"Failed to get notifications by type: {str(e)}")
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Mark notification as read."""
        try:
            if not ObjectId.is_valid(notification_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(notification_id)},
                {
                    "$set": {
                        "read": True,
                        "read_at": datetime.utcnow(),
                        "read_by": user_id
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        try:
            result = await self.collection.update_many(
                {
                    "$or": [
                        {"user_id": user_id},
                        {"user_id": None}
                    ],
                    "read": False
                },
                {
                    "$set": {
                        "read": True,
                        "read_at": datetime.utcnow(),
                        "read_by": user_id
                    }
                }
            )
            
            return result.modified_count
            
        except Exception:
            return 0
    
    async def delete(self, notification_id: str) -> bool:
        """Delete a notification."""
        try:
            if not ObjectId.is_valid(notification_id):
                return False
            
            result = await self.collection.delete_one(
                {"_id": ObjectId(notification_id)}
            )
            
            return result.deleted_count > 0
            
        except Exception:
            return False
    
    async def delete_expired(self) -> int:
        """Delete all expired notifications."""
        try:
            result = await self.collection.delete_many(
                {
                    "expires_at": {"$lt": datetime.utcnow()}
                }
            )
            
            return result.deleted_count
            
        except Exception:
            return 0
    
    async def count_unread(self, user_id: Optional[str] = None) -> int:
        """Count unread notifications."""
        try:
            query = {"read": False}
            
            if user_id:
                query["$or"] = [
                    {"user_id": user_id},
                    {"user_id": None}
                ]
            
            count = await self.collection.count_documents(query)
            return count
            
        except Exception:
            return 0
    
    async def count_by_type(
        self,
        notification_type: NotificationType,
        user_id: Optional[str] = None
    ) -> int:
        """Count notifications by type."""
        try:
            query = {"type": notification_type.value}
            
            if user_id:
                query["$or"] = [
                    {"user_id": user_id},
                    {"user_id": None}
                ]
            
            count = await self.collection.count_documents(query)
            return count
            
        except Exception:
            return 0
    
    async def get_badge_data(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """Get badge data for notification indicators."""
        try:
            # Base query
            base_query = {}
            if user_id:
                base_query["$or"] = [
                    {"user_id": user_id},
                    {"user_id": None}
                ]
            
            # Count unread
            unread_query = {**base_query, "read": False}
            unread_count = await self.collection.count_documents(unread_query)
            
            # Count pending approvals
            pending_query = {
                **base_query,
                "type": NotificationType.USER_PENDING_APPROVAL.value,
                "read": False
            }
            pending_count = await self.collection.count_documents(pending_query)
            
            # Count high priority
            high_priority_query = {
                **base_query,
                "priority": "high",
                "read": False
            }
            high_priority_count = await self.collection.count_documents(high_priority_query)
            
            return {
                "total_unread": unread_count,
                "pending_approvals": pending_count,
                "high_priority": high_priority_count,
            }
            
        except Exception:
            return {
                "total_unread": 0,
                "pending_approvals": 0,
                "high_priority": 0,
            }
    
    def _doc_to_notification(self, doc: Dict[str, Any]) -> Optional[Notification]:
        """
        Convert MongoDB document to Notification entity.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Notification entity or None
        """
        if not doc:
            return None
        
        try:
            doc["id"] = str(doc.pop("_id"))
            return Notification(**doc)
        except Exception:
            return None