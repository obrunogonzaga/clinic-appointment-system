"""
MongoDB implementation of User repository.
"""

from typing import Optional, List
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import IndexModel
from pymongo.errors import DuplicateKeyError

from src.domain.base import DomainException
from src.domain.entities.user import User
from src.domain.entities.user_enhanced import UserEnhanced
from src.domain.enums import UserStatus, UserRole
from src.domain.repositories.user_repository_interface import (
    UserRepositoryInterface,
)


class UserRepository(UserRepositoryInterface):
    """
    MongoDB implementation of UserRepositoryInterface.

    Handles user persistence with proper error handling and indexing.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize user repository.

        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection: AsyncIOMotorCollection = database.users

    async def ensure_indexes(self) -> None:
        """Create necessary indexes for optimal performance."""
        # Try to handle existing indexes gracefully
        try:
            # Drop old conflicting index if exists
            existing = await self.collection.list_indexes().to_list(None)
            for idx in existing:
                if idx.get("name") == "email_1":
                    try:
                        await self.collection.drop_index("email_1")
                    except Exception:
                        pass
        except Exception:
            pass
        
        indexes = [
            # Basic indexes
            IndexModel([("email", 1)], unique=True, name="email_unique_idx"),
            IndexModel([("is_admin", 1)], name="is_admin_idx"),
            IndexModel([("is_active", 1)], name="is_active_idx"),
            IndexModel([("created_at", -1)], name="created_at_desc_idx"),
            
            # Enhanced authentication indexes (AE-009)
            IndexModel([("status", 1)], name="status_idx"),  # For filtering by status
            IndexModel([("role", 1)], name="role_idx"),  # For filtering by role
            IndexModel([("status", 1), ("created_at", -1)], name="status_created_compound_idx"),  # For pending users sorted by date
            IndexModel([("role", 1), ("status", 1)], name="role_status_compound_idx"),  # For role-based status filtering
            IndexModel([("email_verified", 1)], name="email_verified_idx"),  # For unverified users
            IndexModel([("status", 1), ("role", 1), ("created_at", -1)], name="status_role_created_compound_idx"),  # Complex filtering
            
            # Security token indexes
            IndexModel([("security.email_verification_token", 1)], sparse=True, name="email_verification_token_idx"),  # For email verification
            IndexModel([("security.password_reset_token", 1)], sparse=True, name="password_reset_token_idx"),  # For password reset
            IndexModel([("security.refresh_token", 1)], sparse=True, name="refresh_token_idx"),  # For refresh token lookup
            
            # Login security indexes
            IndexModel([("security.login_attempts", 1)], name="login_attempts_idx"),  # For blocked accounts
            IndexModel([("security.last_failed_login", 1)], sparse=True, name="last_failed_login_idx"),  # For time-based unlocking
            IndexModel([("security.account_locked_until", 1)], sparse=True, name="account_locked_until_idx"),  # For locked accounts
        ]
        
        # Create indexes, ignoring conflicts
        try:
            await self.collection.create_indexes(indexes)
        except Exception as e:
            # If there's a conflict, try to create indexes one by one
            if "IndexOptionsConflict" in str(e) or "already exists" in str(e):
                pass  # Indexes already exist, which is fine
            else:
                # For other errors, log but don't fail startup
                print(f"Warning: Could not create all indexes: {e}")

    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            # Prepare user data for MongoDB
            user_dict = user.model_dump(by_alias=True, exclude={"id"})
            user_dict["_id"] = ObjectId()

            # Insert user
            result = await self.collection.insert_one(user_dict)

            # Return user with populated ID
            user.id = str(result.inserted_id)
            return user

        except DuplicateKeyError:
            raise DomainException(
                f"Usuário com email '{user.email}' já existe"
            )
        except Exception as e:
            raise DomainException(f"Erro ao criar usuário: {str(e)}")

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            if not ObjectId.is_valid(user_id):
                return None

            doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            return self._doc_to_user(doc) if doc else None

        except Exception:
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            doc = await self.collection.find_one({"email": email.lower()})
            return self._doc_to_user(doc) if doc else None

        except Exception:
            return None

    async def update(self, user_id: str, user: User) -> Optional[User]:
        """Update existing user."""
        try:
            if not ObjectId.is_valid(user_id):
                return None

            update_data = user.model_dump(
                by_alias=True, exclude={"id", "created_at"}
            )

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True,
            )

            return self._doc_to_user(result) if result else None

        except DuplicateKeyError:
            raise DomainException(f"Email '{user.email}' já está em uso")
        except Exception as e:
            raise DomainException(f"Erro ao atualizar usuário: {str(e)}")

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        try:
            if not ObjectId.is_valid(user_id):
                return False

            result = await self.collection.delete_one(
                {"_id": ObjectId(user_id)}
            )
            return result.deleted_count > 0

        except Exception:
            return False

    async def exists_by_email(self, email: str) -> bool:
        """Check if active user exists by email."""
        try:
            count = await self.collection.count_documents(
                {"email": email.lower(), "is_active": {"$ne": False}}, limit=1
            )
            return count > 0

        except Exception:
            return False

    async def has_admin_users(self) -> bool:
        """Check if there are any admin users in the system."""
        try:
            count = await self.collection.count_documents(
                {"is_admin": True, "is_active": True}, limit=1
            )
            return count > 0

        except Exception:
            return False

    async def count_active_users(self) -> int:
        """Count total active users."""
        try:
            return await self.collection.count_documents({"is_active": True})
        except Exception:
            return 0

    async def list_users(self, limit: int = 10, offset: int = 0) -> list[User]:
        """List active users with pagination."""
        try:
            cursor = (
                self.collection.find({"is_active": {"$ne": False}})  # Only active users
                .sort("created_at", -1)  # Order by created_at desc
                .skip(offset)
                .limit(limit)
            )
            
            docs = await cursor.to_list(length=limit)
            return [self._doc_to_user(doc) for doc in docs]
        except Exception:
            return []

    async def count_total_users(self) -> int:
        """Count total number of active users."""
        try:
            return await self.collection.count_documents({"is_active": {"$ne": False}})
        except Exception:
            return 0

    async def soft_delete(self, user_id: str) -> bool:
        """Soft delete user by setting is_active to False."""
        try:
            if not ObjectId.is_valid(user_id):
                return False

            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_inactive_by_email(self, email: str) -> Optional[User]:
        """Get inactive user by email address."""
        try:
            doc = await self.collection.find_one(
                {"email": email.lower(), "is_active": False}
            )
            return self._doc_to_user(doc) if doc else None
        except Exception:
            return None
    
    async def reactivate_user(
        self, user_id: str, 
        update_data: dict
    ) -> Optional[User]:
        """Reactivate a soft-deleted user with new data."""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            from src.domain.enums import UserStatus
            
            # Prepare update with reactivation
            update_data["is_active"] = True
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            # Reset status fields for fresh start
            if "status" not in update_data:
                # Default to approved for reactivated users by admin
                update_data["status"] = UserStatus.APROVADO
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True
            )
            
            return self._doc_to_user(result) if result else None
        except Exception as e:
            raise DomainException(f"Erro ao reativar usuário: {str(e)}")

    def _doc_to_user(self, doc: dict) -> User:
        """Convert MongoDB document to User entity (supports both User and UserEnhanced)."""
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        
        # Check if this is an enhanced user (has status/role fields)
        if "status" in doc or "role" in doc:
            # Convert to UserEnhanced
            return self._doc_to_user_enhanced(doc)
        
        # Legacy User entity
        return User.model_validate(doc)
    
    def _doc_to_user_enhanced(self, doc: dict) -> UserEnhanced:
        """Convert MongoDB document to UserEnhanced entity."""
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        
        # Ensure nested objects exist
        if "approval" not in doc:
            doc["approval"] = {}
        if "security" not in doc:
            doc["security"] = {}
        if "metadata" not in doc:
            doc["metadata"] = {}
        
        return UserEnhanced.model_validate(doc)
    
    async def get_pending_users(
        self, limit: int = 10, offset: int = 0
    ) -> List[User]:
        """Get all active users with PENDENTE status."""
        try:
            cursor = self.collection.find(
                {"status": UserStatus.PENDENTE, "is_active": {"$ne": False}}
            ).sort("created_at", -1).skip(offset).limit(limit)
            
            users = []
            async for doc in cursor:
                user = self._doc_to_user(doc)
                users.append(user)
            
            return users
        except Exception:
            return []
    
    async def get_users_by_status(
        self, status: UserStatus, limit: int = 10, offset: int = 0
    ) -> List[User]:
        """Get active users by status."""
        try:
            cursor = self.collection.find(
                {"status": status, "is_active": {"$ne": False}}
            ).sort("created_at", -1).skip(offset).limit(limit)
            
            users = []
            async for doc in cursor:
                user = self._doc_to_user(doc)
                users.append(user)
            
            return users
        except Exception:
            return []
    
    async def get_users_by_role(
        self, role: UserRole, limit: int = 10, offset: int = 0
    ) -> List[User]:
        """Get active users by role."""
        try:
            cursor = self.collection.find(
                {"role": role, "is_active": {"$ne": False}}
            ).sort("created_at", -1).skip(offset).limit(limit)
            
            users = []
            async for doc in cursor:
                user = self._doc_to_user(doc)
                users.append(user)
            
            return users
        except Exception:
            return []
    
    async def count_pending_users(self) -> int:
        """Count active users with PENDENTE status."""
        try:
            return await self.collection.count_documents({"status": UserStatus.PENDENTE, "is_active": {"$ne": False}})
        except Exception:
            return 0
    
    async def count_users_by_status(self, status: UserStatus) -> int:
        """Count active users by status."""
        try:
            return await self.collection.count_documents({"status": status, "is_active": {"$ne": False}})
        except Exception:
            return 0
    
    async def approve_user(
        self, user_id: str, admin_id: str
    ) -> Optional[User]:
        """Approve a pending user."""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            current_time = datetime.now(timezone.utc)

            update_data = {
                "status": UserStatus.APROVADO,
                "approval.approved_by": admin_id,
                "approval.approved_at": current_time,
                "approval.rejected_by": None,
                "approval.rejected_at": None,
                "approval.rejection_reason": None,
                "updated_at": current_time,
                "updated_by": admin_id,
                "security.email_verified": True,
                "security.email_verified_at": current_time,
                "security.email_verification_token": None,
                "security.email_verification_expires": None,
            }
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id), "status": UserStatus.PENDENTE},
                {"$set": update_data},
                return_document=True
            )
            
            return self._doc_to_user(result) if result else None
            
        except Exception:
            return None
    
    async def reject_user(
        self, user_id: str, admin_id: str, reason: str
    ) -> Optional[User]:
        """Reject a pending user."""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            update_data = {
                "status": UserStatus.REJEITADO,
                "approval.rejected_by": admin_id,
                "approval.rejected_at": datetime.now(timezone.utc),
                "approval.rejection_reason": reason,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": admin_id,
            }
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id), "status": UserStatus.PENDENTE},
                {"$set": update_data},
                return_document=True
            )
            
            return self._doc_to_user(result) if result else None
            
        except Exception:
            return None
    
    async def get_by_email_verification_token(
        self, token: str
    ) -> Optional[User]:
        """Get user by email verification token."""
        try:
            doc = await self.collection.find_one(
                {
                    "security.email_verification_token": token,
                    "security.email_verification_expires": {"$gt": datetime.now(timezone.utc)}
                }
            )
            return self._doc_to_user(doc) if doc else None
        except Exception:
            return None
    
    async def get_by_password_reset_token(
        self, token: str
    ) -> Optional[User]:
        """Get user by password reset token."""
        try:
            doc = await self.collection.find_one(
                {
                    "security.password_reset_token": token,
                    "security.password_reset_expires": {"$gt": datetime.now(timezone.utc)}
                }
            )
            return self._doc_to_user(doc) if doc else None
        except Exception:
            return None
    
    async def update_refresh_token(
        self, user_id: str, refresh_token: str, expires_at: datetime
    ) -> bool:
        """Update user's refresh token."""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "security.refresh_token": refresh_token,
                        "security.refresh_token_expires": expires_at,
                        "updated_at": datetime.now(timezone.utc),
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_by_refresh_token(
        self, refresh_token: str
    ) -> Optional[User]:
        """Get user by refresh token."""
        try:
            doc = await self.collection.find_one(
                {
                    "security.refresh_token": refresh_token,
                    "security.refresh_token_expires": {"$gt": datetime.now(timezone.utc)}
                }
            )
            return self._doc_to_user(doc) if doc else None
        except Exception:
            return None
    
    async def clear_refresh_token(self, user_id: str) -> bool:
        """Clear user's refresh token (for logout)."""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "security.refresh_token": None,
                        "security.refresh_token_expires": None,
                        "updated_at": datetime.now(timezone.utc),
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
