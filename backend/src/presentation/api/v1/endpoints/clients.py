"""API endpoints for client management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.client_dto import (
    ClientCreateDTO,
    ClientDetailResponseDTO,
    ClientFilterDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientUpdateDTO,
)
from src.application.services.client_service import ClientService
from src.domain.entities.user import User
from src.presentation.api.responses import DataResponse
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import get_client_service


router = APIRouter()


@router.get(
    "/",
    response_model=ClientListResponseDTO,
    summary="Listar clientes",
    description="Retorna a lista de clientes com filtros opcionais e paginação.",
)
async def list_clients(
    search: str = Query(None, description="Buscar por nome"),
    cpf: str = Query(None, description="Filtrar por CPF"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Itens por página"),
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> ClientListResponseDTO:
    """List clients with pagination."""

    del current_user  # Context is enforced by dependency
    filters = ClientFilterDTO(search=search, cpf=cpf, page=page, page_size=page_size)
    return await service.list_clients(filters)


@router.post(
    "/",
    response_model=DataResponse[ClientResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Criar cliente",
    description="Cria um cliente manualmente a partir da tela de gestão.",
)
async def create_client(
    payload: ClientCreateDTO,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> DataResponse[ClientResponseDTO]:
    """Create client manually."""

    del current_user
    result = await service.create_client(payload)
    if not result["success"]:
        status_code = status.HTTP_400_BAD_REQUEST
        if "CPF já cadastrado" in result.get("message", ""):
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=result["message"])

    return DataResponse(
        success=True,
        message=result["message"],
        data=result["client"],
    )


@router.put(
    "/{client_id}",
    response_model=DataResponse[ClientResponseDTO],
    summary="Atualizar cliente",
    description="Atualiza os dados cadastrais de um cliente existente.",
)
async def update_client(
    client_id: str,
    payload: ClientUpdateDTO,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> DataResponse[ClientResponseDTO]:
    """Update client data."""

    del current_user
    result = await service.update_client(client_id, payload)
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])

    return DataResponse(
        success=True,
        message=result["message"],
        data=result["client"],
    )


@router.get(
    "/{client_id}",
    response_model=ClientDetailResponseDTO,
    summary="Detalhes do cliente",
    description="Retorna os dados do cliente e histórico de agendamentos.",
)
async def get_client_detail(
    client_id: str,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> ClientDetailResponseDTO:
    """Get client detail and appointment history."""

    del current_user
    result = await service.get_client_detail(client_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("message"))

    return ClientDetailResponseDTO(**result)
