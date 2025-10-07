"""Background jobs monitoring endpoints."""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.services.task_service import TaskService
from src.infrastructure.container import Container
from src.presentation.dependencies.auth import get_current_user


router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_task_service() -> TaskService:
    """Dependency to get task service."""
    container = Container()
    return container.task_service()


@router.get(
    "/{job_id}/status",
    summary="Get background job status",
    description="Get the current status and details of a background normalization job",
)
async def get_job_status(
    job_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: Dict = Depends(get_current_user),
) -> Dict:
    """
    Get the status of a background job.

    Args:
        job_id: ID of the job to check
        task_service: Task service dependency
        current_user: Authenticated user

    Returns:
        Job status information including:
        - job_id: Job identifier
        - status: Current status (queued, in_progress, complete, not_found, failed)
        - enqueue_time: When job was enqueued
        - start_time: When job started processing (if started)
        - finish_time: When job completed (if completed)
        - result: Job result data (if completed)
        - error: Error message (if failed)
    """
    try:
        job_info = await task_service.get_job_status(job_id)

        if not job_info:
            return {
                "success": False,
                "message": "Job não encontrado",
                "job_id": job_id,
                "status": "not_found",
            }

        return {
            "success": True,
            "message": "Status do job obtido com sucesso",
            "job": job_info,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status do job: {str(exc)}",
        ) from exc
