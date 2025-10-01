"""ARQ worker configuration."""

import logging
from typing import Any, Callable
from urllib.parse import urlparse

from arq.connections import RedisSettings

from src.infrastructure.config import get_settings

settings = get_settings()


logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    """Build RedisSettings from application config."""
    redis_url = settings.redis_url or "redis://localhost:6379"
    parsed = urlparse(redis_url)

    host = parsed.hostname or "localhost"
    port = parsed.port or 6379

    path = parsed.path.lstrip("/")
    database = int(path) if path else settings.redis_db

    password = (
        parsed.password
        if parsed.password is not None
        else settings.redis_password or None
    )

    logger.info(
        "Configuring ARQ worker with Redis at %s:%s (db=%s)",
        host,
        port,
        database,
    )

    return RedisSettings(
        host=host,
        port=port,
        database=database,
        password=password,
    )


class WorkerSettings:
    """ARQ worker settings configuration."""

    # Import task functions here to avoid circular imports
    # These will be set after importing the tasks module
    functions: list[Callable[..., Any]] = []

    redis_settings = get_redis_settings()

    # Worker behavior
    max_jobs = 10  # Maximum concurrent jobs
    job_timeout = 300  # 5 minutes timeout per job
    keep_result = 3600  # Keep job results for 1 hour

    # Logging
    log_results = True

    # Health check
    health_check_interval = 60  # Check worker health every 60 seconds

    # Retry policy
    max_tries = 3  # Retry failed jobs up to 3 times
