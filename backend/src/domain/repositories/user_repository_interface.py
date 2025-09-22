"""
User repository interface for data access abstraction.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from src.domain.entities.user import User
from src.domain.enums import UserStatus, UserRole


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

    @abstractmethod
    async def list_users(self, limit: int = 10, offset: int = 0) -> list[User]:
        """
        List users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of user entities
        """
        pass

    @abstractmethod
    async def count_total_users(self) -> int:
        """
        Count total number of users (active and inactive).

        Returns:
            Total number of users
        """
        pass

    @abstractmethod
    async def soft_delete(self, user_id: str) -> bool:
        """
        Soft delete user by setting is_active to False.

        Args:
            user_id: User unique identifier

        Returns:
            True if user was deactivated, False if not found
        """
        pass

    @abstractmethod
    async def get_pending_users(
        self, limit: int = 10, offset: int = 0
    ) -> List[User]:
        """
        Get all users with PENDENTE status.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of pending user entities
        """
        pass

    @abstractmethod
    async def get_users_by_status(
        self, status: UserStatus, limit: int = 10, offset: int = 0
    ) -> List[User]:
        """
        Get users by status.

        Args:
            status: User status to filter by
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of user entities with the specified status
        """
        pass

    @abstractmethod
    async def get_users_by_role(
        self, role: UserRole, limit: int = 10, offset: int = 0
    ) -> List[User]:
        """
        Get users by role.

        Args:
            role: User role to filter by
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of user entities with the specified role
        """
        pass

    @abstractmethod
    async def count_pending_users(self) -> int:
        """
        Count users with PENDENTE status.

        Returns:
            Number of pending users
        """
        pass

    @abstractmethod
    async def count_users_by_status(self, status: UserStatus) -> int:
        """
        Count users by status.

        Args:
            status: User status to count

        Returns:
            Number of users with the specified status
        """
        pass

    @abstractmethod
    async def approve_user(
        self, user_id: str, admin_id: str
    ) -> Optional[User]:
        """
        Approve a pending user.

        Args:
            user_id: ID of user to approve
            admin_id: ID of admin approving the user

        Returns:
            Approved user entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def reject_user(
        self, user_id: str, admin_id: str, reason: str
    ) -> Optional[User]:
        """
        Reject a pending user.

        Args:
            user_id: ID of user to reject
            admin_id: ID of admin rejecting the user
            reason: Reason for rejection

        Returns:
            Rejected user entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email_verification_token(
        self, token: str
    ) -> Optional[User]:
        """
        Get user by email verification token.

        Args:
            token: Email verification token

        Returns:
            User entity if found with valid token, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_password_reset_token(
        self, token: str
    ) -> Optional[User]:
        """
        Get user by password reset token.

        Args:
            token: Password reset token

        Returns:
            User entity if found with valid token, None otherwise
        """
        pass

    @abstractmethod
    async def update_refresh_token(
        self, user_id: str, refresh_token: str, expires_at: datetime
    ) -> bool:
        """
        Update user's refresh token.

        Args:
            user_id: User unique identifier
            refresh_token: New refresh token
            expires_at: Token expiration datetime

        Returns:
            True if updated successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_by_refresh_token(
        self, refresh_token: str
    ) -> Optional[User]:
        """
        Get user by refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            User entity if found with valid token, None otherwise
        """
        pass

    @abstractmethod
    async def clear_refresh_token(self, user_id: str) -> bool:
        """
        Clear user's refresh token (for logout).

        Args:
            user_id: User unique identifier

        Returns:
            True if cleared successfully, False otherwise
        """
        pass
