"""
Driver API endpoints.
"""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.application.dtos.driver_dto import (
    ActiveDriverListResponseDTO,
    DriverCreateDTO,
    DriverDeleteResponseDTO,
    DriverFilterOptionsDTO,
    DriverListResponseDTO,
    DriverResponseDTO,
    DriverStatsDTO,
    DriverUpdateDTO,
    DriverValidationErrorDTO,
)
from src.application.services.driver_service import DriverService
from src.infrastructure.repositories.driver_repository import DriverRepository
from src.presentation.api.responses import BaseResponse, DataResponse

router = APIRouter()


# Dependency to get driver repository
async def get_driver_repository() -> DriverRepository:
    """Get driver repository instance."""
    from src.infrastructure.container import get_driver_repository

    return await get_driver_repository()


# Dependency to get driver service
async def get_driver_service(
    driver_repository: DriverRepository = Depends(get_driver_repository),
) -> DriverService:
    """Get driver service instance."""
    return DriverService(driver_repository)


@router.post(
    "/",
    response_model=DataResponse[DriverResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new driver",
    description="Register a new driver in the system",
)
async def create_driver(
    driver_data: DriverCreateDTO,
    service: DriverService = Depends(get_driver_service),
) -> DataResponse[DriverResponseDTO]:
    """
    Create a new driver.

    Args:
        driver_data: Driver creation data
        service: Driver service instance

    Returns:
        DataResponse[DriverResponseDTO]: Created driver
    """
    try:
        result = await service.create_driver(driver_data)

        if not result["success"]:
            status_code = 400
            if "CNH já cadastrada" in result["message"]:
                status_code = 409  # Conflict

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return DataResponse(
            success=True, message=result["message"], data=result["driver"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/",
    response_model=DriverListResponseDTO,
    summary="Get drivers with filters",
    description="Get drivers with optional filters and pagination",
)
async def get_drivers(
    nome_completo: str = Query(None, description="Filtrar por nome completo"),
    cnh: str = Query(None, description="Filtrar por CNH"),
    telefone: str = Query(None, description="Filtrar por telefone"),
    email: str = Query(None, description="Filtrar por email"),
    status: str = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Itens por página"),
    service: DriverService = Depends(get_driver_service),
) -> DriverListResponseDTO:
    """
    Get drivers with filters and pagination.

    Args:
        nome_completo: Filter by driver name
        cnh: Filter by CNH
        telefone: Filter by phone
        email: Filter by email
        status: Filter by status
        page: Page number
        page_size: Items per page
        service: Driver service instance

    Returns:
        DriverListResponseDTO: Filtered drivers
    """
    try:
        result = await service.get_drivers_with_filters(
            nome_completo=nome_completo,
            cnh=cnh,
            telefone=telefone,
            email=email,
            status=status,
            page=page,
            page_size=page_size,
        )

        return DriverListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            drivers=result["drivers"],
            pagination=result["pagination"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/active",
    response_model=ActiveDriverListResponseDTO,
    summary="Get active drivers",
    description="Get all active drivers (for dropdowns)",
)
async def get_active_drivers(
    service: DriverService = Depends(get_driver_service),
) -> ActiveDriverListResponseDTO:
    """
    Get active drivers.

    Args:
        service: Driver service instance

    Returns:
        ActiveDriverListResponseDTO: Active drivers
    """
    try:
        result = await service.get_active_drivers()

        return ActiveDriverListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            drivers=result["drivers"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/filter-options",
    response_model=DriverFilterOptionsDTO,
    summary="Get filter options",
    description="Get available filter options for drivers",
)
async def get_filter_options(
    service: DriverService = Depends(get_driver_service),
) -> DriverFilterOptionsDTO:
    """
    Get available filter options.

    Args:
        service: Driver service instance

    Returns:
        DriverFilterOptionsDTO: Available filter options
    """
    try:
        result = await service.get_filter_options()

        return DriverFilterOptionsDTO(
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
    response_model=DriverStatsDTO,
    summary="Get driver statistics",
    description="Get driver statistics for dashboard",
)
async def get_driver_stats(
    service: DriverService = Depends(get_driver_service),
) -> DriverStatsDTO:
    """
    Get driver statistics.

    Args:
        service: Driver service instance

    Returns:
        DriverStatsDTO: Driver statistics
    """
    try:
        result = await service.get_driver_stats()

        return DriverStatsDTO(
            success=result["success"],
            message=result.get("message"),
            stats=result["stats"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/{driver_id}",
    response_model=DataResponse[DriverResponseDTO],
    summary="Get driver by ID",
    description="Get a specific driver by ID",
)
async def get_driver(
    driver_id: str, service: DriverService = Depends(get_driver_service)
) -> DataResponse[DriverResponseDTO]:
    """
    Get driver by ID.

    Args:
        driver_id: Driver ID
        service: Driver service instance

    Returns:
        DataResponse[DriverResponseDTO]: Driver data
    """
    try:
        result = await service.get_driver_by_id(driver_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])

        return DataResponse(
            success=True, message="Motorista encontrado", data=result["driver"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{driver_id}",
    response_model=DataResponse[DriverResponseDTO],
    summary="Update driver",
    description="Update driver information",
)
async def update_driver(
    driver_id: str,
    driver_data: DriverUpdateDTO,
    service: DriverService = Depends(get_driver_service),
) -> DataResponse[DriverResponseDTO]:
    """
    Update driver.

    Args:
        driver_id: Driver ID
        driver_data: Driver update data
        service: Driver service instance

    Returns:
        DataResponse[DriverResponseDTO]: Updated driver
    """
    try:
        result = await service.update_driver(driver_id, driver_data)

        if not result["success"]:
            status_code = 400
            if "não encontrado" in result["message"]:
                status_code = 404
            elif "CNH já cadastrada" in result["message"]:
                status_code = 409

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return DataResponse(
            success=True, message=result["message"], data=result["driver"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.put(
    "/{driver_id}/status",
    response_model=DataResponse[DriverResponseDTO],
    summary="Update driver status",
    description="Update the status of a driver",
)
async def update_driver_status(
    driver_id: str,
    new_status: str = Query(..., description="Novo status"),
    service: DriverService = Depends(get_driver_service),
) -> DataResponse[DriverResponseDTO]:
    """
    Update driver status.

    Args:
        driver_id: Driver ID
        new_status: New status value
        service: Driver service instance

    Returns:
        DataResponse[DriverResponseDTO]: Updated driver
    """
    try:
        result = await service.update_driver_status(driver_id, new_status)

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    400 if "não encontrado" not in result["message"] else 404
                ),
                detail=result["message"],
            )

        return DataResponse(
            success=True, message=result["message"], data=result["driver"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.delete(
    "/{driver_id}",
    response_model=BaseResponse,
    summary="Delete driver",
    description="Delete a driver by ID",
)
async def delete_driver(
    driver_id: str, service: DriverService = Depends(get_driver_service)
) -> BaseResponse:
    """
    Delete driver.

    Args:
        driver_id: Driver ID
        service: Driver service instance

    Returns:
        BaseResponse: Delete result
    """
    try:
        result = await service.delete_driver(driver_id)

        if not result["success"]:
            raise HTTPException(
                status_code=(
                    404 if "não encontrado" in result["message"] else 400
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
