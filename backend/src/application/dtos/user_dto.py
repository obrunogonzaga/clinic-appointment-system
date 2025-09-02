"""
User Data Transfer Objects for API communication.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserCreateRequest(BaseModel):
    """DTO for user creation request."""

    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password: str = Field(..., min_length=8, description="User password")
    is_admin: bool = Field(False, description="Whether user has admin privileges")

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
    is_admin: bool = Field(..., description="Whether user has admin privileges")
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


class AuthStatusResponse(BaseModel):
    """DTO for authentication status response."""

    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Response message")
    user: Optional[UserResponse] = Field(None, description="User data if authenticated")


class FirstAdminCheckResponse(BaseModel):
    """DTO for checking if first admin setup is needed."""

    needs_setup: bool = Field(..., description="Whether system needs initial admin setup")
    message: str = Field(..., description="Explanation message")


class PasswordChangeRequest(BaseModel):
    """DTO for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True