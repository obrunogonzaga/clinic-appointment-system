"""
User entity for authentication and authorization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    """
    User entity representing a system user.

    This entity handles user authentication and basic authorization.
    For Phase 1, we use a simple is_admin flag.
    """

    id: Optional[str] = Field(
        None, alias="_id", description="MongoDB ObjectId"
    )
    email: str = Field(..., description="User email address (unique)")
    name: str = Field(
        ..., min_length=2, max_length=100, description="User full name"
    )
    password_hash: str = Field(..., description="Bcrypt hashed password")
    is_admin: bool = Field(
        False, description="Whether user has admin privileges"
    )
    is_active: bool = Field(True, description="Whether user account is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="User creation timestamp"
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

    def is_authenticated(self) -> bool:
        """Check if user is authenticated (active)."""
        return self.is_active

    def has_admin_privileges(self) -> bool:
        """Check if user has admin privileges."""
        return self.is_admin and self.is_active

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        str_strip_whitespace = True
        validate_assignment = True
