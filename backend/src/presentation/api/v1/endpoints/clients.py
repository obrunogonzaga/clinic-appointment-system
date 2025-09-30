"""API endpoints for managing clients."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.client_dto import (
    ClientCreateDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientUpdateDTO,
)
from src.application.services.client_service import ClientService
from src.domain.entities.user import User
from src.infrastructure.container import get_client_repository
from src.infrastructure.repositories.client_repository import ClientRepository
from src.presentation.dependencies.auth import get_current_active_user

router = APIRouter()


async def get_client_service(
    client_repository: ClientRepository = Depends(get_client_repository),
) -> ClientService:
    """Resolve the client service with Mongo repository implementation."""

    return ClientService(client_repository)


@router.get(
    "/",
    response_model=ClientListResponseDTO,
    summary="Listar clientes",
    description="Retorna a lista de clientes com suporte a filtro por nome ou CPF.",
)
async def list_clients(
    search: str | None = Query(
        default=None, description="Filtro por nome, e-mail ou CPF"
    ),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> ClientListResponseDTO:
    """List clients applying optional search and pagination."""

    result = await service.list_clients(search=search, page=page, page_size=page_size)

    return ClientListResponseDTO(
        success=result["success"],
        message=result.get("message"),
        clients=result["clients"],
        pagination=result["pagination"],
    )


@router.post(
    "/",
    response_model=ClientResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cliente",
    description="Cria um novo cliente manualmente a partir da tela de gestão.",
)
async def create_client(
    client_data: ClientCreateDTO,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> ClientResponseDTO:
    """Create a client manually."""

    result = await service.create_client(client_data)
    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "duplicate":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=result["message"]
            )
        if error_code == "validation":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Erro interno"),
        )

    return ClientResponseDTO(
        success=True,
        message=result.get("message"),
        client=result["client"],
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponseDTO,
    summary="Detalhar cliente",
    description="Retorna os dados completos de um cliente, incluindo histórico.",
)
async def get_client(
    client_id: str,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> ClientResponseDTO:
    """Retrieve a client by identifier."""

    result = await service.get_client(client_id)
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])

    return ClientResponseDTO(success=True, client=result["client"])


@router.put(
    "/{client_id}",
    response_model=ClientResponseDTO,
    summary="Atualizar cliente",
    description="Atualiza dados cadastrais de um cliente existente.",
)
async def update_client(
    client_id: str,
    payload: ClientUpdateDTO,
    service: ClientService = Depends(get_client_service),
    current_user: User = Depends(get_current_active_user),
) -> ClientResponseDTO:
    """Update an existing client."""

    result = await service.update_client(client_id, payload)
    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
        if error_code == "validation":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Erro interno"),
        )

    return ClientResponseDTO(
        success=True,
        message=result.get("message"),
        client=result["client"],
    )
