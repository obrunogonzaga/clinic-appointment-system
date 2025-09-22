"""
Rate limiting dependencies for endpoints.
"""

from typing import Callable

from fastapi import Request
from slowapi import Limiter

from src.infrastructure.container import container
from src.infrastructure.services.rate_limiter import RateLimiter


def get_rate_limiter() -> RateLimiter:
    """Get the rate limiter instance from container."""
    return container.rate_limiter


def get_limiter() -> Limiter:
    """Get the SlowAPI limiter instance."""
    return container.rate_limiter.get_limiter()