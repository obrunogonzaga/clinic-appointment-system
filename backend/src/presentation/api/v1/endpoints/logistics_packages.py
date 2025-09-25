"""API endpoints for logistics packages."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.logistics_package_dto import (
    LogisticsPackageCreateDTO,
    LogisticsPackageResponseDTO,
    LogisticsPackageUpdateDTO,
)
from src.application.services.logistics_package_service import (
    LogisticsPackageService,
)
from src.infrastructure.container import (
    get_car_repository,
    get_collector_repository,
    get_driver_repository,
    get_logistics_package_repository,
)
from src.presentation.api.responses import BaseResponse, DataResponse, ListResponse
from src.presentation.dependencies.auth import get_current_active_user

router = APIRouter()


async def get_logistics_package_service(
    logistics_package_repository=Depends(get_logistics_package_repository),
    driver_repository=Depends(get_driver_repository),
    collector_repository=Depends(get_collector_repository),
    car_repository=Depends(get_car_repository),
) -> LogisticsPackageService:
    """Resolve service com dependências configuradas."""

    return LogisticsPackageService(
        logistics_package_repository,
        driver_repository,
        collector_repository,
        car_repository,
    )


@router.get(
    "/",
    response_model=ListResponse[LogisticsPackageResponseDTO],
    summary="Listar pacotes logísticos",
    description="Retorna os pacotes logísticos cadastrados com opção de filtrar por status.",
)
async def list_logistics_packages(
    status_filter: Optional[str] = Query(
        None, description="Filtrar por status (Ativo ou Inativo)"
    ),
    service: LogisticsPackageService = Depends(get_logistics_package_service),
    current_user=Depends(get_current_active_user),
) -> ListResponse[LogisticsPackageResponseDTO]:
    """Lista pacotes logísticos."""

    result = await service.list_packages(status=status_filter)
    packages = result.get("packages", [])
    total = len(packages)

    return ListResponse(
        success=True,
        message=result.get("message"),
        data=packages,
        total=total,
        page=1,
        per_page=max(total, 1),
        pages=1,
    )


@router.get(
    "/active",
    response_model=ListResponse[LogisticsPackageResponseDTO],
    summary="Listar pacotes logísticos ativos",
    description="Retorna apenas os pacotes com status Ativo.",
)
async def list_active_logistics_packages(
    service: LogisticsPackageService = Depends(get_logistics_package_service),
    current_user=Depends(get_current_active_user),
) -> ListResponse[LogisticsPackageResponseDTO]:
    """Lista apenas pacotes ativos."""

    result = await service.list_active_packages()
    packages = result.get("packages", [])
    total = len(packages)

    return ListResponse(
        success=True,
        message=result.get("message"),
        data=packages,
        total=total,
        page=1,
        per_page=max(total, 1),
        pages=1,
    )


@router.get(
    "/{package_id}",
    response_model=DataResponse[LogisticsPackageResponseDTO],
    summary="Obter pacote logístico",
)
async def get_logistics_package(
    package_id: str,
    service: LogisticsPackageService = Depends(get_logistics_package_service),
    current_user=Depends(get_current_active_user),
) -> DataResponse[LogisticsPackageResponseDTO]:
    """Recupera um pacote específico."""

    result = await service.get_package(package_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return DataResponse(
        success=True,
        message=result.get("message"),
        data=result["package"],
    )


@router.post(
    "/",
    response_model=DataResponse[LogisticsPackageResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Criar pacote logístico",
)
async def create_logistics_package(
    package_data: LogisticsPackageCreateDTO,
    service: LogisticsPackageService = Depends(get_logistics_package_service),
    current_user=Depends(get_current_active_user),
) -> DataResponse[LogisticsPackageResponseDTO]:
    """Cria um novo pacote logístico."""

    result = await service.create_package(package_data)
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Não foi possível criar o pacote."),
        )

    return DataResponse(
        success=True,
        message="Pacote logístico criado com sucesso.",
        data=result["package"],
    )


@router.patch(
    "/{package_id}",
    response_model=DataResponse[LogisticsPackageResponseDTO],
    summary="Atualizar pacote logístico",
)
async def update_logistics_package(
    package_id: str,
    update_data: LogisticsPackageUpdateDTO,
    service: LogisticsPackageService = Depends(get_logistics_package_service),
    current_user=Depends(get_current_active_user),
) -> DataResponse[LogisticsPackageResponseDTO]:
    """Atualiza informações de um pacote logístico."""

    result = await service.update_package(package_id, update_data)
    if not result["success"]:
        error_code = result.get("error_code", "validation")
        status_code_value = 404 if error_code == "not_found" else 400
        raise HTTPException(status_code=status_code_value, detail=result["message"])

    return DataResponse(
        success=True,
        message=result.get("message", "Pacote logístico atualizado."),
        data=result["package"],
    )


@router.delete(
    "/{package_id}",
    response_model=BaseResponse,
    summary="Remover pacote logístico",
    status_code=status.HTTP_200_OK,
)
async def delete_logistics_package(
    package_id: str,
    service: LogisticsPackageService = Depends(get_logistics_package_service),
    current_user=Depends(get_current_active_user),
) -> BaseResponse:
    """Remove um pacote logístico."""

    result = await service.delete_package(package_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return BaseResponse(success=True, message=result["message"])

