#!/usr/bin/env python3
"""
ARQ background worker entry point.

This script starts the ARQ worker that processes background tasks like
appointment data normalization (address and document parsing via OpenAI).

Usage:
    python workers.py

The worker will connect to Redis and start processing jobs from the queue.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from arq import run_worker

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from {env_path}")
else:
    print(f"⚠ Warning: .env file not found at {env_path}")

from src.workers.config import WorkerSettings
from src.workers.normalization_tasks import normalize_appointment


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


async def startup(ctx):
    """Worker startup hook."""
    logger.info("=" * 60)
    logger.info("Starting ARQ Background Worker")
    logger.info("=" * 60)
    logger.info("Tasks registered:")
    for func in WorkerSettings.functions:
        logger.info("  - %s", func.__name__)
    logger.info("Redis: %s:%s", WorkerSettings.redis_settings.host, WorkerSettings.redis_settings.port)
    logger.info("Max concurrent jobs: %d", WorkerSettings.max_jobs)
    logger.info("Job timeout: %d seconds", WorkerSettings.job_timeout)

    # Check environment variables
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    if openrouter_key:
        logger.info("✓ OPENROUTER_API_KEY is set (length: %d)", len(openrouter_key))
    else:
        logger.warning("⚠ OPENROUTER_API_KEY is NOT set!")

    mongodb_url = os.getenv("MONGODB_URL", "")
    if mongodb_url:
        # Mask password in URL for logging
        masked_url = mongodb_url
        if "@" in masked_url:
            parts = masked_url.split("@")
            creds = parts[0].split("://")[1]
            if ":" in creds:
                user = creds.split(":")[0]
                masked_url = masked_url.replace(creds, f"{user}:***")
        logger.info("✓ MONGODB_URL is set: %s", masked_url)
    else:
        logger.warning("⚠ MONGODB_URL is NOT set!")

    address_norm_enabled = os.getenv("ADDRESS_NORMALIZATION_ENABLED", "false")
    logger.info("Address normalization: %s", address_norm_enabled)

    logger.info("=" * 60)


async def shutdown(ctx):
    """Worker shutdown hook."""
    logger.info("=" * 60)
    logger.info("Shutting down ARQ Background Worker")
    logger.info("=" * 60)


# Register task functions
WorkerSettings.functions = [normalize_appointment]

# Add lifecycle hooks
WorkerSettings.on_startup = startup
WorkerSettings.on_shutdown = shutdown


def main():
    """Main entry point for the worker."""
    try:
        logger.info("Initializing ARQ worker...")
        run_worker(WorkerSettings)
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
        sys.exit(0)
    except Exception as exc:
        logger.error("Worker failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
