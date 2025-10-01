"""ARQ worker configuration."""

import logging
from typing import Any, Callable

from arq.connections import RedisSettings

from src.infrastructure.config import get_settings

settings = get_settings()


logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    """Build RedisSettings from application config."""
    # Parse redis_url to extract host and port
    # Format: redis://host:port or redis://host:port/db
    redis_url = settings.redis_url or "redis://localhost:6379"
    url_parts = redis_url.replace("redis://", "").split("/")
    host_port = url_parts[0]

    if ":" in host_port:
        host, port_str = host_port.split(":")
        port = int(port_str)
    else:
        host = host_port
        port = 6379

    # Extract database number if present
    database = int(url_parts[1]) if len(url_parts) > 1 else settings.redis_db

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
        password=settings.redis_password or None,
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
