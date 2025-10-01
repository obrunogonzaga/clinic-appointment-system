"""Service for managing background tasks with ARQ."""

import logging
from typing import Any, Dict, Optional

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from src.infrastructure.config import get_settings

settings = get_settings()


logger = logging.getLogger(__name__)


class TaskService:
    """Service for enqueueing and managing background tasks."""

    def __init__(self) -> None:
        self._pool: Optional[ArqRedis] = None

    async def get_pool(self) -> ArqRedis:
        """Get or create the ARQ Redis connection pool."""
        if self._pool is None:
            redis_settings = self._get_redis_settings()
            self._pool = await create_pool(redis_settings)
        return self._pool

    async def close(self) -> None:
        """Close the ARQ Redis connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def enqueue_normalization(
        self, appointment_id: str
    ) -> Optional[str]:
        """
        Enqueue an appointment normalization job.

        Args:
            appointment_id: ID of the appointment to normalize

        Returns:
            Job ID if successfully enqueued, None otherwise
        """
        try:
            pool = await self.get_pool()
            job = await pool.enqueue_job(
                "normalize_appointment",
                appointment_id,
            )
            if job:
                logger.info(
                    "Enqueued normalization job %s for appointment %s",
                    job.job_id,
                    appointment_id,
                )
                return job.job_id
            return None
        except Exception as exc:
            logger.error(
                "Failed to enqueue normalization for appointment %s: %s",
                appointment_id,
                exc,
            )
            return None

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a background job.

        Args:
            job_id: ID of the job to check

        Returns:
            Job status dictionary or None if job not found
        """
        try:
            pool = await self.get_pool()
            job_result = await pool.job_info(job_id)
            if not job_result:
                return None

            return {
                "job_id": job_id,
                "status": job_result.job_status.value,
                "enqueue_time": job_result.enqueue_time,
                "start_time": job_result.start_time,
                "finish_time": job_result.finish_time,
                "result": job_result.result,
                "error": (
                    str(job_result.result)
                    if job_result.job_status.value == "failed"
                    else None
                ),
            }
        except Exception as exc:
            logger.error("Failed to get job %s status: %s", job_id, exc)
            return None

    @staticmethod
    def _get_redis_settings() -> RedisSettings:
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

        return RedisSettings(
            host=host,
            port=port,
            database=database,
            password=settings.redis_password or None,
        )
