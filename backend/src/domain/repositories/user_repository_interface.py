"""
User repository interface for data access abstraction.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User


class UserRepositoryInterface(ABC):
    """
    Abstract interface for user data access operations.
    
    This interface defines the contract for user persistence,
    following the Repository pattern for clean separation of concerns.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user with populated ID
            
        Raises:
            DomainException: If user already exists or validation fails
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User unique identifier
            
        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def update(self, user_id: str, user: User) -> Optional[User]:
        """
        Update existing user.
        
        Args:
            user_id: User unique identifier
            user: Updated user data
            
        Returns:
            Updated user entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User unique identifier
            
        Returns:
            True if user was deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: User email address
            
        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    async def has_admin_users(self) -> bool:
        """
        Check if there are any admin users in the system.
        
        This is used for the initial admin registration flow.
        
        Returns:
            True if at least one admin user exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_active_users(self) -> int:
        """
        Count total active users.
        
        Returns:
            Number of active users
        """
        pass