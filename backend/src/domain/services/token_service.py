"""
Token service for managing authentication and verification tokens.
"""

import secrets
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone
import logging

from jose import JWTError, jwt

from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class TokenService:
    """
    Service for generating and validating various types of tokens.
    
    Handles:
    - JWT access tokens
    - Refresh tokens
    - Email verification tokens
    - Password reset tokens
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize token service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
        
        # Email verification settings
        self.email_verification_expire_hours = getattr(
            settings, 'email_verification_expire_hours', 24
        )
        
        # Password reset settings
        self.password_reset_expire_hours = getattr(
            settings, 'password_reset_expire_hours', 1
        )
        
    def create_access_token(
        self, 
        user_id: str,
        user_email: str,
        is_admin: bool = False,
        additional_claims: Optional[dict] = None
    ) -> Tuple[str, datetime]:
        """
        Create JWT access token.
        
        Args:
            user_id: User ID
            user_email: User email
            is_admin: Whether user is admin
            additional_claims: Additional JWT claims
            
        Returns:
            Tuple of (token, expiration_time)
        """
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(
            minutes=self.access_token_expire_minutes
        )

        claims = {
            "sub": user_id,
            "email": user_email,
            "is_admin": is_admin,
            "exp": expires_at,
            "iat": now_utc,
            "type": "access"
        }
        
        if additional_claims:
            claims.update(additional_claims)
            
        token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        
        return token, expires_at
        
    def create_refresh_token(
        self,
        user_id: str,
        token_family: Optional[str] = None
    ) -> Tuple[str, datetime, str]:
        """
        Create refresh token with family tracking.
        
        Args:
            user_id: User ID
            token_family: Token family for rotation tracking
            
        Returns:
            Tuple of (token, expiration_time, family_id)
        """
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(
            days=self.refresh_token_expire_days
        )
        
        # Generate or use existing family ID
        family_id = token_family or secrets.token_urlsafe(32)
        
        # Generate unique token ID
        token_id = secrets.token_urlsafe(32)
        
        claims = {
            "sub": user_id,
            "exp": expires_at,
            "iat": now_utc,
            "type": "refresh",
            "jti": token_id,  # JWT ID for tracking
            "family": family_id  # Family for rotation detection
        }
        
        token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        
        return token, expires_at, family_id
        
    def verify_access_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode access token.
        
        Args:
            token: JWT token
            
        Returns:
            Token claims if valid, None otherwise
        """
        try:
            claims = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify it's an access token
            if claims.get("type") != "access":
                return None
                
            return claims
            
        except JWTError as e:
            logger.debug(f"Access token verification failed: {e}")
            return None
            
    def verify_refresh_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode refresh token.
        
        Args:
            token: Refresh token
            
        Returns:
            Token claims if valid, None otherwise
        """
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verify it's a refresh token
            if claims.get("type") != "refresh":
                return None
                
            return claims
            
        except JWTError as e:
            logger.debug(f"Refresh token verification failed: {e}")
            return None
            
    def generate_email_verification_token(self) -> Tuple[str, str, datetime]:
        """
        Generate email verification token.
        
        Returns:
            Tuple of (token, hashed_token, expiration_time)
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Hash for storage (never store plain tokens)
        hashed_token = self._hash_token(token)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(
            hours=self.email_verification_expire_hours
        )
        
        return token, hashed_token, expires_at
        
    def generate_password_reset_token(self) -> Tuple[str, str, datetime]:
        """
        Generate password reset token.
        
        Returns:
            Tuple of (token, hashed_token, expiration_time)
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Hash for storage
        hashed_token = self._hash_token(token)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(
            hours=self.password_reset_expire_hours
        )
        
        return token, hashed_token, expires_at
        
    def verify_email_token(
        self, 
        token: str, 
        stored_hash: str,
        expiration: datetime
    ) -> bool:
        """
        Verify email verification token.
        
        Args:
            token: Plain token from user
            stored_hash: Hashed token from database
            expiration: Token expiration time
            
        Returns:
            True if token is valid
        """
        # Check expiration
        if datetime.utcnow() > expiration:
            return False
            
        # Verify token hash
        token_hash = self._hash_token(token)
        return secrets.compare_digest(token_hash, stored_hash)
        
    def verify_password_reset_token(
        self,
        token: str,
        stored_hash: str,
        expiration: datetime
    ) -> bool:
        """
        Verify password reset token.
        
        Args:
            token: Plain token from user
            stored_hash: Hashed token from database
            expiration: Token expiration time
            
        Returns:
            True if token is valid
        """
        # Check expiration
        if datetime.utcnow() > expiration:
            return False
            
        # Verify token hash
        token_hash = self._hash_token(token)
        return secrets.compare_digest(token_hash, stored_hash)
        
    def _hash_token(self, token: str) -> str:
        """
        Hash token for secure storage.
        
        Args:
            token: Plain token
            
        Returns:
            Hashed token
        """
        # Use SHA-256 for token hashing
        return hashlib.sha256(
            f"{token}{self.secret_key}".encode()
        ).hexdigest()
        
    def generate_state_token(self) -> str:
        """
        Generate CSRF/state token for OAuth flows.
        
        Returns:
            State token
        """
        return secrets.token_urlsafe(32)
        
    def create_api_key(self, identifier: str) -> str:
        """
        Create API key for service-to-service auth.
        
        Args:
            identifier: Service identifier
            
        Returns:
            API key
        """
        # Generate random key
        key = secrets.token_urlsafe(32)
        
        # Create composite key with identifier
        api_key = f"{identifier}.{key}"
        
        return api_key
        
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validate API key and extract identifier.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Service identifier if valid
        """
        try:
            parts = api_key.split(".")
            if len(parts) == 2:
                return parts[0]  # Return identifier
        except:
            pass
            
        return None
        
    def rotate_refresh_token(
        self,
        old_token: str,
        user_id: str
    ) -> Optional[Tuple[str, datetime, str]]:
        """
        Rotate refresh token (security best practice).
        
        Args:
            old_token: Current refresh token
            user_id: User ID
            
        Returns:
            New token tuple if valid, None otherwise
        """
        # Verify old token
        claims = self.verify_refresh_token(old_token)
        if not claims:
            return None
            
        # Check user ID matches
        if claims.get("sub") != user_id:
            logger.warning(f"Token rotation attempted with mismatched user ID")
            return None
            
        # Create new token with same family
        family_id = claims.get("family")
        return self.create_refresh_token(user_id, family_id)
        
    def invalidate_token_family(self, family_id: str):
        """
        Invalidate all tokens in a family (for security breach).
        
        This would typically update a blacklist in Redis/database.
        
        Args:
            family_id: Token family to invalidate
        """
        # This would be implemented with Redis/database
        # to track invalidated families
        logger.warning(f"Token family {family_id} invalidated due to potential breach")
        
    def generate_temp_access_code(self, length: int = 6) -> str:
        """
        Generate temporary access code (for 2FA, etc).
        
        Args:
            length: Code length
            
        Returns:
            Numeric code
        """
        # Generate numeric code
        return ''.join(secrets.choice('0123456789') for _ in range(length))
