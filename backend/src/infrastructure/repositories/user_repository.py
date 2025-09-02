"""
MongoDB implementation of User repository.
"""

from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import IndexModel
from pymongo.errors import DuplicateKeyError

from src.domain.base import DomainException
from src.domain.entities.user import User
from src.domain.repositories.user_repository_interface import UserRepositoryInterface


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
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("is_admin", 1)]),
            IndexModel([("is_active", 1)]),
            IndexModel([("created_at", -1)]),
        ]
        await self.collection.create_indexes(indexes)

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
            raise DomainException(f"Usuário com email '{user.email}' já existe")
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
                by_alias=True, 
                exclude={"id", "created_at"}
            )
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True
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
                
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
            
        except Exception:
            return False

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        try:
            count = await self.collection.count_documents(
                {"email": email.lower()}, 
                limit=1
            )
            return count > 0
            
        except Exception:
            return False

    async def has_admin_users(self) -> bool:
        """Check if there are any admin users in the system."""
        try:
            count = await self.collection.count_documents(
                {"is_admin": True, "is_active": True}, 
                limit=1
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

    def _doc_to_user(self, doc: dict) -> User:
        """Convert MongoDB document to User entity."""
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return User.model_validate(doc)