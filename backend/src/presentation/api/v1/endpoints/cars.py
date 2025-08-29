"""
Car API endpoints.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.application.dtos.car_dto import (
    ActiveCarListResponseDTO,
    CarCreateDTO,
    CarDeleteResponseDTO,
    CarFilterDTO,
    CarFilterOptionsDTO,
    CarFromStringDTO,
    CarFromStringResponseDTO,
    CarListResponseDTO,
    CarResponseDTO,
    CarStatsDTO,
    CarUpdateDTO,
    CarValidationErrorDTO,
)
from src.application.services.car_service import CarService
from src.infrastructure.repositories.car_repository import CarRepository
from src.presentation.api.responses import BaseResponse, DataResponse

router = APIRouter()


# Dependency to get car repository
async def get_car_repository() -> CarRepository:
    """Get car repository instance."""
    from src.infrastructure.container import get_car_repository

    return await get_car_repository()


# Dependency to get car service
async def get_car_service(
    car_repository: CarRepository = Depends(get_car_repository),
) -> CarService:
    """Get car service instance."""
    return CarService(car_repository)


@router.post(
    "/",
    response_model=DataResponse[CarResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new car",
    description="Register a new car in the system",
)
async def create_car(
    car_data: CarCreateDTO,
    service: CarService = Depends(get_car_service),
) -> DataResponse[CarResponseDTO]:
    """
    Create a new car.

    Args:
        car_data: Car creation data
        service: Car service instance

    Returns:
        DataResponse[CarResponseDTO]: Created car
    """
    try:
        result = await service.create_car(car_data)

        if not result["success"]:
            status_code = 400
            if "já cadastrado" in result["message"]:
                status_code = 409  # Conflict

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return DataResponse(
            success=True, message=result["message"], data=result["car"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.get(
    "/",
    response_model=CarListResponseDTO,
    summary="List cars",
    description="Get a paginated list of cars with optional filters",
)
async def list_cars(
    nome: Optional[str] = Query(None, description="Filtrar por nome do carro"),
    unidade: Optional[str] = Query(None, description="Filtrar por unidade"),
    placa: Optional[str] = Query(None, description="Filtrar por placa"),
    modelo: Optional[str] = Query(None, description="Filtrar por modelo"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Itens por página"),
    service: CarService = Depends(get_car_service),
) -> CarListResponseDTO:
    """
    List cars with optional filters and pagination.

    Args:
        nome: Filter by car name
        unidade: Filter by unit
        placa: Filter by license plate
        modelo: Filter by model
        status: Filter by status
        page: Page number
        page_size: Items per page
        service: Car service instance

    Returns:
        CarListResponseDTO: Paginated list of cars
    """
    try:
        filters = CarFilterDTO(
            nome=nome,
            unidade=unidade,
            placa=placa,
            modelo=modelo,
            status=status,
            page=page,
            page_size=page_size,
        )

        result = await service.list_cars(filters)

        return CarListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            cars=result["cars"],
            pagination=result["pagination"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.get(
    "/{car_id}",
    response_model=DataResponse[CarResponseDTO],
    summary="Get car by ID",
    description="Get a specific car by its ID",
)
async def get_car(
    car_id: str,
    service: CarService = Depends(get_car_service),
) -> DataResponse[CarResponseDTO]:
    """
    Get a car by its ID.

    Args:
        car_id: Car unique identifier
        service: Car service instance

    Returns:
        DataResponse[CarResponseDTO]: Car data
    """
    try:
        result = await service.get_car_by_id(car_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=result["message"]
            )

        return DataResponse(
            success=True, message="Carro encontrado", data=result["car"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.put(
    "/{car_id}",
    response_model=DataResponse[CarResponseDTO],
    summary="Update car",
    description="Update an existing car",
)
async def update_car(
    car_id: str,
    car_data: CarUpdateDTO,
    service: CarService = Depends(get_car_service),
) -> DataResponse[CarResponseDTO]:
    """
    Update an existing car.

    Args:
        car_id: Car ID to update
        car_data: Updated car data
        service: Car service instance

    Returns:
        DataResponse[CarResponseDTO]: Updated car
    """
    try:
        result = await service.update_car(car_id, car_data)

        if not result["success"]:
            status_code = 400
            if "não encontrado" in result["message"]:
                status_code = 404
            elif "já existe" in result["message"]:
                status_code = 409  # Conflict

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return DataResponse(
            success=True, message=result["message"], data=result["car"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.delete(
    "/{car_id}",
    response_model=CarDeleteResponseDTO,
    summary="Delete car",
    description="Delete a car from the system",
)
async def delete_car(
    car_id: str,
    service: CarService = Depends(get_car_service),
) -> CarDeleteResponseDTO:
    """
    Delete a car.

    Args:
        car_id: Car ID to delete
        service: Car service instance

    Returns:
        CarDeleteResponseDTO: Deletion result
    """
    try:
        result = await service.delete_car(car_id)

        if not result["success"]:
            status_code = 400
            if "não encontrado" in result["message"]:
                status_code = 404

            raise HTTPException(
                status_code=status_code, detail=result["message"]
            )

        return CarDeleteResponseDTO(success=True, message=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.get(
    "/active/list",
    response_model=ActiveCarListResponseDTO,
    summary="Get active cars",
    description="Get all active cars for dropdowns",
)
async def get_active_cars(
    service: CarService = Depends(get_car_service),
) -> ActiveCarListResponseDTO:
    """
    Get all active cars for dropdowns.

    Args:
        service: Car service instance

    Returns:
        ActiveCarListResponseDTO: List of active cars
    """
    try:
        result = await service.get_active_cars()

        return ActiveCarListResponseDTO(
            success=result["success"],
            message=result.get("message"),
            cars=result["cars"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.get(
    "/filters/options",
    response_model=CarFilterOptionsDTO,
    summary="Get filter options",
    description="Get available filter options for cars",
)
async def get_filter_options(
    service: CarService = Depends(get_car_service),
) -> CarFilterOptionsDTO:
    """
    Get filter options for dropdowns.

    Args:
        service: Car service instance

    Returns:
        CarFilterOptionsDTO: Available filter options
    """
    try:
        result = await service.get_filter_options()

        return CarFilterOptionsDTO(
            success=result["success"],
            message=result.get("message"),
            statuses=result["statuses"],
            unidades=result["unidades"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.get(
    "/statistics/overview",
    response_model=CarStatsDTO,
    summary="Get car statistics",
    description="Get car statistics for dashboard",
)
async def get_car_stats(
    service: CarService = Depends(get_car_service),
) -> CarStatsDTO:
    """
    Get car statistics.

    Args:
        service: Car service instance

    Returns:
        CarStatsDTO: Car statistics
    """
    try:
        result = await service.get_car_stats()

        return CarStatsDTO(
            success=result["success"],
            message=result.get("message"),
            stats=result["stats"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )


@router.post(
    "/from-string",
    response_model=CarFromStringResponseDTO,
    summary="Find or create car from string",
    description="Find or create a car from appointment string format (used in Excel import)",
)
async def find_or_create_car_from_string(
    car_data: CarFromStringDTO,
    service: CarService = Depends(get_car_service),
) -> CarFromStringResponseDTO:
    """
    Find or create a car from appointment string format.

    This endpoint is used during Excel import to automatically
    register cars that don't exist yet.

    Args:
        car_data: Car string data
        service: Car service instance

    Returns:
        CarFromStringResponseDTO: Car data and creation info
    """
    try:
        result = await service.find_or_create_car_from_string(
            car_data.car_string
        )

        return CarFromStringResponseDTO(
            success=result["success"],
            message=result.get("message"),
            car=result.get("car"),
            created=result.get("created", False),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}",
        )
