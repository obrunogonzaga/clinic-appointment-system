"""
User Data Transfer Objects for API communication.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, Field, field_validator, EmailStr
from src.domain.enums import UserRole, UserStatus


class UserCreateRequest(BaseModel):
    """DTO for user creation request."""

    email: str = Field(..., description="User email address")
    name: str = Field(
        ..., min_length=2, max_length=100, description="User full name"
    )
    password: str = Field(..., min_length=8, description="User password")
    is_admin: bool = Field(
        False, description="Whether user has admin privileges"
    )

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Normalize name by stripping whitespace."""
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class LoginRequest(BaseModel):
    """DTO for user login request."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class UserResponse(BaseModel):
    """DTO for user response (public user data)."""

    id: str = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    is_admin: bool = Field(
        ..., description="Whether user has admin privileges"
    )
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="User creation timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TokenResponse(BaseModel):
    """DTO for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    user: UserResponse = Field(..., description="Authenticated user data")
    refresh_token: Optional[str] = Field(None, description="Refresh token for token renewal")


class AuthStatusResponse(BaseModel):
    """DTO for authentication status response."""

    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Response message")
    user: Optional[Union[UserResponse, UserEnhancedResponse]] = Field(
        None, description="User data if authenticated"
    )


class FirstAdminCheckResponse(BaseModel):
    """DTO for checking if first admin setup is needed."""

    needs_setup: bool = Field(
        ..., description="Whether system needs initial admin setup"
    )
    message: str = Field(..., description="Explanation message")


class UserUpdateRequest(BaseModel):
    """DTO for user update request."""

    name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="User full name"
    )
    is_admin: Optional[bool] = Field(
        None, description="Whether user has admin privileges"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether user account is active"
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Normalize name by stripping whitespace."""
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class UserListRequest(BaseModel):
    """DTO for user list request with pagination."""

    limit: int = Field(
        10, ge=1, le=100, description="Number of users per page"
    )
    offset: int = Field(0, ge=0, description="Number of users to skip")
    
    class Config:
        """Pydantic configuration."""
        
        str_strip_whitespace = True


class UserListResponse(BaseModel):
    """DTO for paginated user list response."""

    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    limit: int = Field(..., description="Number of users per page")
    offset: int = Field(..., description="Number of users skipped")
    has_next: bool = Field(..., description="Whether there are more users")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class PasswordChangeRequest(BaseModel):
    """DTO for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class PublicUserRegisterRequest(BaseModel):
    """DTO for public user registration (self-registration)."""
    
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(
        ..., min_length=2, max_length=100, description="User full name"
    )
    password: str = Field(..., min_length=8, description="User password")
    role: UserRole = Field(
        UserRole.COLABORADOR, 
        description="Requested role (cannot be ADMIN)"
    )
    phone: Optional[str] = Field(None, description="Phone number")
    cpf: Optional[str] = Field(None, description="CPF (Brazilian ID)")
    department: Optional[str] = Field(None, description="Department/Unit")
    
    # For drivers specifically
    drivers_license: Optional[str] = Field(
        None, description="Driver's license number (required for MOTORISTA)"
    )
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: UserRole) -> UserRole:
        """Ensure users cannot self-register as admin."""
        if v == UserRole.ADMIN:
            raise ValueError("Não é possível se cadastrar como administrador")
        return v
    
    @field_validator("drivers_license")
    @classmethod
    def validate_drivers_license(cls, v: Optional[str], values) -> Optional[str]:
        """Ensure drivers have a license."""
        if values.data.get("role") == UserRole.MOTORISTA and not v:
            raise ValueError("CNH é obrigatória para motoristas")
        return v
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True
        use_enum_values = True


class UserEnhancedResponse(BaseModel):
    """DTO for enhanced user response with role and status."""
    
    id: str = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="Account status")
    phone: Optional[str] = Field(None, description="Phone number")
    department: Optional[str] = Field(None, description="Department")
    email_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="User creation timestamp")
    created_by: Optional[str] = Field(None, description="Creator user ID (null = self-registered)")
    
    # Approval information (if relevant)
    approved_by: Optional[str] = Field(None, description="Approver user ID")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    rejected_by: Optional[str] = Field(None, description="Rejecter user ID")
    rejected_at: Optional[datetime] = Field(None, description="Rejection timestamp")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        use_enum_values = True


class PendingUsersResponse(BaseModel):
    """DTO for pending users list response."""
    
    users: List[UserEnhancedResponse] = Field(..., description="List of pending users")
    total: int = Field(..., description="Total number of pending users")
    limit: int = Field(..., description="Number of users per page")
    offset: int = Field(..., description="Number of users skipped")
    has_next: bool = Field(..., description="Whether there are more users")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserApprovalRequest(BaseModel):
    """DTO for approving a user."""
    
    message: Optional[str] = Field(
        None, description="Optional approval message for the user"
    )
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class UserRejectionRequest(BaseModel):
    """DTO for rejecting a user."""
    
    reason: str = Field(
        ..., min_length=10, max_length=500,
        description="Reason for rejection (required)"
    )
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class DashboardStatsResponse(BaseModel):
    """DTO for admin dashboard statistics."""
    
    total_users: int = Field(..., description="Total number of users")
    pending_users: int = Field(..., description="Number of pending users")
    approved_users: int = Field(..., description="Number of approved users")
    rejected_users: int = Field(..., description="Number of rejected users")
    suspended_users: int = Field(..., description="Number of suspended users")
    
    users_by_role: dict[str, int] = Field(..., description="User count by role")
    recent_registrations: List[UserEnhancedResponse] = Field(
        ..., description="Recent user registrations"
    )
    pending_approvals: List[UserEnhancedResponse] = Field(
        ..., description="Users awaiting approval"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class EmailVerificationRequest(BaseModel):
    """DTO for email verification."""
    
    token: str = Field(..., description="Email verification token")
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class ResendVerificationRequest(BaseModel):
    """DTO for resending email verification."""
    
    email: EmailStr = Field(..., description="User email address")
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class RefreshTokenRequest(BaseModel):
    """DTO for refresh token request."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True


class RefreshTokenResponse(BaseModel):
    """DTO for refresh token response."""
    
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_at: datetime = Field(..., description="Access token expiration")
    refresh_token: str = Field(..., description="New refresh token (rotated)")
    refresh_expires_at: datetime = Field(..., description="Refresh token expiration")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
