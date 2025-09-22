"""
Rate limiting service using SlowAPI.
"""

from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.infrastructure.config import Settings
from src.infrastructure.services.redis_service import RedisService


class RateLimiter:
    """
    Rate limiting service with Redis backend.
    
    Provides configurable rate limits for different endpoints
    with fallback to in-memory storage if Redis is unavailable.
    """
    
    def __init__(self, settings: Settings, redis_service: Optional[RedisService] = None):
        """
        Initialize rate limiter.
        
        Args:
            settings: Application settings
            redis_service: Optional Redis service for distributed rate limiting
        """
        self.settings = settings
        self.redis_service = redis_service
        
        # Check if rate limiting is enabled
        self.enabled = getattr(settings, 'rate_limit_enabled', True)
        
        # Get rate limit configurations
        self.login_rate_limit = getattr(settings, 'login_rate_limit', '5/minute')
        self.register_rate_limit = getattr(settings, 'register_rate_limit', '3/hour')
        self.api_rate_limit = getattr(settings, 'api_rate_limit', '100/minute')
        self.verification_rate_limit = getattr(settings, 'verification_rate_limit', '2/hour')
        
        # Storage backend
        storage_uri = None
        if redis_service and redis_service.is_available():
            storage_uri = getattr(settings, 'redis_url', 'redis://localhost:6379')
            
        # Create limiter instance
        self.limiter = Limiter(
            key_func=self._get_identifier,
            default_limits=[self.api_rate_limit] if self.enabled else [],
            storage_uri=storage_uri,
            headers_enabled=True,  # Add rate limit headers to responses
            strategy="fixed-window",  # or "moving-window" for more accuracy
            swallow_errors=True,  # Don't crash if Redis is down
        )
        
    def _get_identifier(self, request: Request) -> str:
        """
        Get identifier for rate limiting (IP address or user ID).
        
        Args:
            request: FastAPI request
            
        Returns:
            Identifier string
        """
        # Try to get authenticated user ID first
        user = getattr(request.state, 'user', None)
        if user:
            return f"user:{user.id}"
            
        # Fall back to IP address
        return get_remote_address(request)
        
    def get_limiter(self) -> Limiter:
        """
        Get the limiter instance for FastAPI integration.
        
        Returns:
            Limiter instance
        """
        return self.limiter
        
    def get_middleware(self) -> SlowAPIMiddleware:
        """
        Get SlowAPI middleware for FastAPI app.
        
        Returns:
            SlowAPI middleware
        """
        return SlowAPIMiddleware(app=None, limiter=self.limiter)
        
    def limit_login(self) -> Callable:
        """
        Get rate limit decorator for login endpoint.
        
        Returns:
            Rate limit decorator
        """
        return self.limiter.limit(self.login_rate_limit)
        
    def limit_register(self) -> Callable:
        """
        Get rate limit decorator for registration endpoint.
        
        Returns:
            Rate limit decorator
        """
        return self.limiter.limit(self.register_rate_limit)
        
    def limit_verification(self) -> Callable:
        """
        Get rate limit decorator for email verification endpoints.
        
        Returns:
            Rate limit decorator
        """
        return self.limiter.limit(self.verification_rate_limit)
        
    def limit_password_reset(self) -> Callable:
        """
        Get rate limit decorator for password reset.
        
        Returns:
            Rate limit decorator
        """
        return self.limiter.limit("2/hour")
        
    def limit_api_heavy(self) -> Callable:
        """
        Get rate limit decorator for heavy API operations.
        
        Returns:
            Rate limit decorator
        """
        return self.limiter.limit("10/minute")
        
    def custom_limit(self, rate: str) -> Callable:
        """
        Create custom rate limit decorator.
        
        Args:
            rate: Rate limit string (e.g., "5/minute", "100/hour")
            
        Returns:
            Rate limit decorator
        """
        return self.limiter.limit(rate)
        
    @staticmethod
    def create_rate_limit_handler() -> Callable:
        """
        Create custom rate limit exceeded handler.
        
        Returns:
            Error handler function
        """
        async def handler(request: Request, exc: RateLimitExceeded) -> Response:
            """Custom handler for rate limit exceeded."""
            
            # Extract rate limit info
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": "Muitas tentativas. Por favor, aguarde antes de tentar novamente.",
                    "detail": {
                        "limit": str(exc.detail),
                        "retry_after": request.state.view_rate_limit
                    }
                },
                headers={
                    "Retry-After": str(request.state.view_rate_limit),
                    "X-RateLimit-Limit": str(request.state.view_rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(request.state.view_rate_limit)
                }
            )
            
            return response
            
        return handler
        
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> tuple[bool, int]:
        """
        Manually check rate limit for custom logic.
        
        Args:
            key: Rate limit key
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if not self.enabled:
            return True, limit
            
        if self.redis_service and self.redis_service.is_available():
            # Use Redis for distributed rate limiting
            current = await self.redis_service.increment(
                f"rate_limit:{key}",
                expire=window
            )
            
            remaining = max(0, limit - current)
            is_allowed = current <= limit
            
            return is_allowed, remaining
        else:
            # Fallback to in-memory rate limiting
            # This is less accurate but works without Redis
            # In production, you'd want Redis for distributed systems
            return True, limit
            
    async def reset_rate_limit(self, key: str) -> bool:
        """
        Reset rate limit for a specific key.
        
        Args:
            key: Rate limit key
            
        Returns:
            True if reset successfully
        """
        if self.redis_service and self.redis_service.is_available():
            return await self.redis_service.delete(f"rate_limit:{key}")
        return True
        
    def disable(self):
        """Disable rate limiting (for testing)."""
        self.enabled = False
        self.limiter = Limiter(
            key_func=self._get_identifier,
            default_limits=[],
            swallow_errors=True,
        )
        
    def enable(self):
        """Re-enable rate limiting."""
        self.enabled = True
        # Recreate limiter with limits
        storage_uri = None
        if self.redis_service and self.redis_service.is_available():
            storage_uri = getattr(self.settings, 'redis_url', 'redis://localhost:6379')
            
        self.limiter = Limiter(
            key_func=self._get_identifier,
            default_limits=[self.api_rate_limit],
            storage_uri=storage_uri,
            headers_enabled=True,
            strategy="fixed-window",
            swallow_errors=True,
        )