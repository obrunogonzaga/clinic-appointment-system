"""
Enhanced user entity with approval workflow and role-based permissions.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, EmailStr
from src.domain.enums import UserRole, UserStatus, get_role_permissions


class UserApproval(BaseModel):
    """User approval information."""
    approved_by: Optional[str] = Field(None, description="Admin user ID who approved")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    rejected_by: Optional[str] = Field(None, description="Admin user ID who rejected")
    rejected_at: Optional[datetime] = Field(None, description="Rejection timestamp")


class UserSecurity(BaseModel):
    """User security settings."""
    email_verified: bool = Field(False, description="Email verification status")
    email_verification_token: Optional[str] = Field(None, description="Email verification token (hashed)")
    email_verification_expires: Optional[datetime] = Field(None, description="Token expiration")
    email_verified_at: Optional[datetime] = Field(None, description="Email verification timestamp")
    
    failed_login_attempts: int = Field(0, description="Failed login attempts counter")
    last_failed_attempt: Optional[datetime] = Field(None, description="Last failed login timestamp")
    account_locked_until: Optional[datetime] = Field(None, description="Account lock expiry")
    last_successful_login: Optional[datetime] = Field(None, description="Last successful login")
    last_login_ip: Optional[str] = Field(None, description="Last login IP address")
    
    password_reset_token: Optional[str] = Field(None, description="Password reset token (hashed)")
    password_reset_expires: Optional[datetime] = Field(None, description="Password reset token expiry")
    last_password_change: Optional[datetime] = Field(None, description="Last password change timestamp")
    
    refresh_token: Optional[str] = Field(None, description="Current refresh token (hashed)")
    refresh_token_expires: Optional[datetime] = Field(None, description="Refresh token expiry")
    refresh_token_family: Optional[str] = Field(None, description="Token family for rotation tracking")


class UserMetadata(BaseModel):
    """Additional user metadata."""
    phone: Optional[str] = Field(None, description="Phone number")
    cpf: Optional[str] = Field(None, description="CPF (Brazilian ID)")
    department: Optional[str] = Field(None, description="Department/Unit")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    address: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    
    # For drivers specifically
    drivers_license: Optional[str] = Field(None, description="Driver's license number")
    license_expiry: Optional[datetime] = Field(None, description="License expiry date")
    vehicle_assigned: Optional[str] = Field(None, description="Assigned vehicle ID")


class UserEnhanced(BaseModel):
    """
    Enhanced User entity with approval workflow and role-based permissions.
    """
    
    # Basic fields
    id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId")
    email: EmailStr = Field(..., description="User email address (unique)")
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    
    # Role and status
    role: UserRole = Field(UserRole.COLABORADOR, description="User role")
    status: UserStatus = Field(UserStatus.PENDENTE, description="Account status")
    
    # Approval information
    approval: UserApproval = Field(default_factory=UserApproval, description="Approval information")
    
    # Security settings
    security: UserSecurity = Field(default_factory=UserSecurity, description="Security settings")
    
    # Additional metadata
    metadata: UserMetadata = Field(default_factory=UserMetadata, description="Additional user information")
    
    # Custom permissions (beyond role defaults)
    custom_permissions: List[str] = Field([], description="Additional custom permissions")
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="User creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User ID who created this account (null = self-registered)")
    updated_by: Optional[str] = Field(None, description="User ID who last updated this account")
    
    # Backward compatibility
    is_admin: bool = Field(False, description="Legacy admin flag (use role instead)")
    is_active: bool = Field(True, description="Legacy active flag (use status instead)")
    
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
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to set legacy fields based on new fields."""
        # Set legacy is_admin based on role
        self.is_admin = self.role == UserRole.ADMIN
        
        # Set legacy is_active based on status
        self.is_active = self.status in [UserStatus.APROVADO, UserStatus.PENDENTE]
    
    def is_authenticated(self) -> bool:
        """Check if user can authenticate."""
        return (
            self.status == UserStatus.APROVADO 
            and not self.is_locked()
            and self.security.email_verified
        )
    
    def is_pending(self) -> bool:
        """Check if user is pending approval."""
        return self.status == UserStatus.PENDENTE
    
    def is_approved(self) -> bool:
        """Check if user is approved."""
        return self.status == UserStatus.APROVADO
    
    def is_rejected(self) -> bool:
        """Check if user was rejected."""
        return self.status == UserStatus.REJEITADO
    
    def is_suspended(self) -> bool:
        """Check if user is suspended."""
        return self.status == UserStatus.SUSPENSO
    
    def is_locked(self) -> bool:
        """Check if account is temporarily locked due to failed attempts."""
        locked_until = self.security.account_locked_until
        if locked_until:
            return datetime.utcnow() < locked_until
        return False
    
    def can_login(self) -> bool:
        """Check if user can login (approved, verified, not locked)."""
        return (
            self.status == UserStatus.APROVADO
            and self.security.email_verified
            and not self.is_locked()
        )
    
    def needs_email_verification(self) -> bool:
        """Check if user needs to verify email."""
        return not self.security.email_verified
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            permission: Permission string to check
            
        Returns:
            True if user has permission
        """
        if self.status != UserStatus.APROVADO:
            return False
        
        # Check role-based permissions
        role_perms = get_role_permissions(self.role)
        if permission in role_perms:
            return True
        
        # Check custom permissions
        return permission in self.custom_permissions
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Check if user has all specified permissions."""
        return all(self.has_permission(p) for p in permissions)
    
    def get_all_permissions(self) -> List[str]:
        """Get all user permissions (role + custom)."""
        if self.status != UserStatus.APROVADO:
            return []
        
        role_perms = get_role_permissions(self.role)
        return list(set(role_perms + self.custom_permissions))
    
    def increment_failed_login(self, max_attempts: int = 5) -> None:
        """
        Increment failed login attempts and lock if necessary.
        
        Args:
            max_attempts: Maximum attempts before locking
        """
        self.security.failed_login_attempts += 1
        if self.security.failed_login_attempts >= max_attempts:
            # Lock account for 30 minutes
            self.security.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_login(self) -> None:
        """Reset failed login attempts on successful login."""
        self.security.failed_login_attempts = 0
        self.security.locked_until = None
        self.security.last_login = datetime.utcnow()
    
    def approve(self, admin_id: str) -> None:
        """
        Approve user account.
        
        Args:
            admin_id: ID of admin approving the user
        """
        self.status = UserStatus.APROVADO
        self.approval.approved_by = admin_id
        self.approval.approved_at = datetime.utcnow()
        self.approval.rejection_reason = None
        self.approval.rejected_by = None
        self.approval.rejected_at = None
        self.updated_at = datetime.utcnow()
    
    def reject(self, admin_id: str, reason: str) -> None:
        """
        Reject user account.
        
        Args:
            admin_id: ID of admin rejecting the user
            reason: Reason for rejection
        """
        self.status = UserStatus.REJEITADO
        self.approval.rejected_by = admin_id
        self.approval.rejected_at = datetime.utcnow()
        self.approval.rejection_reason = reason
        self.updated_at = datetime.utcnow()
    
    def suspend(self, admin_id: str) -> None:
        """
        Suspend user account.
        
        Args:
            admin_id: ID of admin suspending the user
        """
        self.status = UserStatus.SUSPENSO
        self.updated_by = admin_id
        self.updated_at = datetime.utcnow()
    
    def reactivate(self, admin_id: str) -> None:
        """
        Reactivate suspended user account.
        
        Args:
            admin_id: ID of admin reactivating the user
        """
        if self.status == UserStatus.SUSPENSO:
            self.status = UserStatus.APROVADO
            self.updated_by = admin_id
            self.updated_at = datetime.utcnow()
    
    def generate_email_verification_token(self) -> str:
        """Generate email verification token."""
        import secrets
        token = secrets.token_urlsafe(32)
        self.security.email_verification_token = token
        self.security.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def verify_email(self, token: str) -> bool:
        """
        Verify email with token.
        
        Args:
            token: Verification token
            
        Returns:
            True if verification successful
        """
        if (
            self.security.email_verification_token == token
            and self.security.email_verification_expires
            and datetime.utcnow() < self.security.email_verification_expires
        ):
            self.security.email_verified = True
            self.security.email_verified_at = datetime.utcnow()
            self.security.email_verification_token = None
            self.security.email_verification_expires = None
            return True
        return False
    
    def generate_password_reset_token(self) -> str:
        """Generate password reset token."""
        import secrets
        token = secrets.token_urlsafe(32)
        self.security.password_reset_token = token
        self.security.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        return token
    
    def can_reset_password(self, token: str) -> bool:
        """
        Check if password can be reset with token.
        
        Args:
            token: Reset token
            
        Returns:
            True if token is valid
        """
        return (
            self.security.password_reset_token == token
            and self.security.password_reset_expires
            and datetime.utcnow() < self.security.password_reset_expires
        )
    
    def reset_password(self, new_password_hash: str) -> None:
        """
        Reset password.
        
        Args:
            new_password_hash: New hashed password
        """
        self.password_hash = new_password_hash
        self.security.password_reset_token = None
        self.security.password_reset_expires = None
        self.security.last_password_change = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        str_strip_whitespace = True
        validate_assignment = True
        use_enum_values = True
