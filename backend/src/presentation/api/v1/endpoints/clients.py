"""Client management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.client_dto import (
    ClientCreateDTO,
    ClientDetailResponseDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientUpdateDTO,
)
from src.application.services.client_service import ClientService
from src.infrastructure.container import get_client_repository
from src.infrastructure.repositories.client_repository import ClientRepository
from src.presentation.api.responses import DataResponse

router = APIRouter()


async def get_client_service(
    repository: ClientRepository = Depends(get_client_repository),
) -> ClientService:
    """Dependency that provides a client service instance."""

    return ClientService(repository)


@router.get(
    "/",
    response_model=ClientListResponseDTO,
    summary="Listar clientes",
    description="Retorna a lista de clientes com suporte a busca e paginação.",
)
async def list_clients(
    search: str | None = Query(None, description="Filtro por nome ou CPF"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Itens por página"),
    service: ClientService = Depends(get_client_service),
) -> ClientListResponseDTO:
    """Return paginated list of clients."""

    result = await service.list_clients(search=search, page=page, page_size=page_size)
    return result


@router.post(
    "/",
    response_model=DataResponse[ClientResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar cliente",
    description="Cria um novo cliente manualmente.",
)
async def create_client(
    payload: ClientCreateDTO,
    service: ClientService = Depends(get_client_service),
) -> DataResponse[ClientResponseDTO]:
    """Create a new client entry."""

    result = await service.create_client(payload)
    if not result["success"]:
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get("error_code") == "duplicate":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=result["message"])

    return DataResponse(
        success=True,
        message=result["message"],
        data=result["client"],
    )


@router.get(
    "/{client_id}",
    response_model=ClientDetailResponseDTO,
    summary="Detalhar cliente",
    description="Retorna os dados completos do cliente com histórico de agendamentos.",
)
async def get_client(
    client_id: str,
    service: ClientService = Depends(get_client_service),
) -> ClientDetailResponseDTO:
    """Retrieve client with full history."""

    result = await service.get_client_detail(client_id)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)
    return result


@router.put(
    "/{client_id}",
    response_model=DataResponse[ClientResponseDTO],
    summary="Atualizar cliente",
    description="Atualiza informações cadastrais de um cliente existente.",
)
async def update_client(
    client_id: str,
    payload: ClientUpdateDTO,
    service: ClientService = Depends(get_client_service),
) -> DataResponse[ClientResponseDTO]:
    """Update client data."""

    result = await service.update_client(client_id, payload)
    if not result["success"]:
        if result.get("error_code") == "not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])

    return DataResponse(
        success=True,
        message=result["message"],
        data=result["client"],
    )
