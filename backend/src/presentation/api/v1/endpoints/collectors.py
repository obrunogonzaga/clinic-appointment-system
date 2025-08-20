"""
Collector API endpoints.
"""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.application.dtos.collector_dto import (
    ActiveCollectorListResponseDTO,
    CollectorCreateDTO,
    CollectorDeleteResponseDTO,
    CollectorFilterOptionsDTO,
    CollectorListResponseDTO,
    CollectorResponseDTO,
    CollectorStatsDTO,
    CollectorUpdateDTO,
    CollectorValidationErrorDTO,
)
from src.application.services.collector_service import CollectorService
from src.infrastructure.repositories.collector_repository import (
    CollectorRepository,
)
from src.presentation.api.responses import BaseResponse, DataResponse

router = APIRouter()


# Dependency to get collector repository
async def get_collector_repository() -> CollectorRepository:
    """Get collector repository instance."""
    from src.infrastructure.container import get_collector_repository

    return await get_collector_repository()


# Dependency to get collector service
async def get_collector_service(
    collector_repository: CollectorRepository = Depends(
        get_collector_repository
    ),
) -> CollectorService:
    """Get collector service instance."""
    return CollectorService(collector_repository)


@router.post(
    "/",
    response_model=DataResponse[CollectorResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new collector",
    description="Register a new collector in the system",
)
async def create_collector(
    collector_data: CollectorCreateDTO,
    service: CollectorService = Depends(get_collector_service),
) -> DataResponse[CollectorResponseDTO]:
    """
    Create a new collector.

    Args:
        collector_data: Collector creation data
        service: Collector service instance

    Returns:
        DataResponse[CollectorResponseDTO]: Created collector
    """
    try:
        result = await service.create_collector(collector_data)

        if not result["success"]:
            status_code = 400
            if "CPF já cadastrado" in result["message"]:
                status_code = 409  # Conflict

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return DataResponse(
            success=True, message=result["message"], data=result["collector"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/",
    response_model=CollectorListResponseDTO,
    summary="Get collectors with filters",
    description="Get collectors with optional filters and pagination",
)
async def get_collectors(
    nome_completo: str = Query(None, description="Filtrar por nome completo"),
    cpf: str = Query(None, description="Filtrar por CPF"),
    telefone: str = Query(None, description="Filtrar por telefone"),
    email: str = Query(None, description="Filtrar por email"),
    status: str = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Itens por página"),
    service: CollectorService = Depends(get_collector_service),
) -> CollectorListResponseDTO:
    """
    Get collectors with filters and pagination.

    Args:
        nome_completo: Filter by collector name
        cpf: Filter by CPF
        telefone: Filter by phone
        email: Filter by email
        status: Filter by status
        page: Page number
        page_size: Items per page
        service: Collector service instance

    Returns:
        CollectorListResponseDTO: Filtered collectors
    """
    try:
        result = await service.get_collectors_with_filters(
            nome_completo=nome_completo,
            cpf=cpf,
            telefone=telefone,
            email=email,
            status=status,
            page=page,
            page_size=page_size,
        )

        return CollectorListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            collectors=result["collectors"],
            pagination=result["pagination"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/active",
    response_model=ActiveCollectorListResponseDTO,
    summary="Get active collectors",
    description="Get all active collectors (for dropdowns)",
)
async def get_active_collectors(
    service: CollectorService = Depends(get_collector_service),
) -> ActiveCollectorListResponseDTO:
    """
    Get active collectors.

    Args:
        service: Collector service instance

    Returns:
        ActiveCollectorListResponseDTO: Active collectors
    """
    try:
        result = await service.get_active_collectors()

        return ActiveCollectorListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            collectors=result["collectors"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/filter-options",
    response_model=CollectorFilterOptionsDTO,
    summary="Get filter options",
    description="Get available filter options for collectors",
)
async def get_filter_options(
    service: CollectorService = Depends(get_collector_service),
) -> CollectorFilterOptionsDTO:
    """
    Get available filter options.

    Args:
        service: Collector service instance

    Returns:
        CollectorFilterOptionsDTO: Available filter options
    """
    try:
        result = await service.get_filter_options()

        return CollectorFilterOptionsDTO(
            success=result["success"],
            message=result.get("message"),
            statuses=result["statuses"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=CollectorStatsDTO,
    summary="Get collector statistics",
    description="Get collector statistics for dashboard",
)
async def get_collector_stats(
    service: CollectorService = Depends(get_collector_service),
) -> CollectorStatsDTO:
    """
    Get collector statistics.

    Args:
        service: Collector service instance

    Returns:
        CollectorStatsDTO: Collector statistics
    """
    try:
        result = await service.get_collector_stats()

        return CollectorStatsDTO(
            success=result["success"],
            message=result.get("message"),
            stats=result["stats"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/{collector_id}",
    response_model=DataResponse[CollectorResponseDTO],
    summary="Get collector by ID",
    description="Get a specific collector by ID",
)
async def get_collector(
    collector_id: str,
    service: CollectorService = Depends(get_collector_service),
) -> DataResponse[CollectorResponseDTO]:
    """
    Get collector by ID.

    Args:
        collector_id: Collector ID
        service: Collector service instance

    Returns:
        DataResponse[CollectorResponseDTO]: Collector data
    """
    try:
        result = await service.get_collector_by_id(collector_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])

        return DataResponse(
            success=True,
            message="Coletora encontrada",
            data=result["collector"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{collector_id}",
    response_model=DataResponse[CollectorResponseDTO],
    summary="Update collector",
    description="Update collector information",
)
async def update_collector(
    collector_id: str,
    collector_data: CollectorUpdateDTO,
    service: CollectorService = Depends(get_collector_service),
) -> DataResponse[CollectorResponseDTO]:
    """
    Update collector.

    Args:
        collector_id: Collector ID
        collector_data: Collector update data
        service: Collector service instance

    Returns:
        DataResponse[CollectorResponseDTO]: Updated collector
    """
    try:
        result = await service.update_collector(collector_id, collector_data)

        if not result["success"]:
            status_code = 400
            if "não encontrada" in result["message"]:
                status_code = 404
            elif "CPF já cadastrado" in result["message"]:
                status_code = 409

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return DataResponse(
            success=True, message=result["message"], data=result["collector"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{collector_id}/status",
    response_model=DataResponse[CollectorResponseDTO],
    summary="Update collector status",
    description="Update the status of a collector",
)
async def update_collector_status(
    collector_id: str,
    new_status: str = Query(..., description="Novo status"),
    service: CollectorService = Depends(get_collector_service),
) -> DataResponse[CollectorResponseDTO]:
    """
    Update collector status.

    Args:
        collector_id: Collector ID
        new_status: New status value
        service: Collector service instance

    Returns:
        DataResponse[CollectorResponseDTO]: Updated collector
    """
    try:
        result = await service.update_collector_status(
            collector_id, new_status
        )

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    400 if "não encontrada" not in result["message"] else 404
                ),
                detail=result["message"],
            )

        return DataResponse(
            success=True, message=result["message"], data=result["collector"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.delete(
    "/{collector_id}",
    response_model=BaseResponse,
    summary="Delete collector",
    description="Delete a collector by ID",
)
async def delete_collector(
    collector_id: str,
    service: CollectorService = Depends(get_collector_service),
) -> BaseResponse:
    """
    Delete collector.

    Args:
        collector_id: Collector ID
        service: Collector service instance

    Returns:
        BaseResponse: Delete result
    """
    try:
        result = await service.delete_collector(collector_id)

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    404 if "não encontrada" in result["message"] else 400
                ),
                detail=result["message"],
            )

        return BaseResponse(success=True, message=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )
