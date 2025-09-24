"""API endpoints for managing appointment tags."""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.tag_dto import (
    TagCreateDTO,
    TagResponseDTO,
    TagUpdateDTO,
)
from src.application.services.tag_service import TagService
from src.domain.entities.user import User
from src.infrastructure.container import (
    get_appointment_repository,
    get_tag_repository,
)
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.infrastructure.repositories.tag_repository import TagRepository
from src.presentation.api.responses import (
    BaseResponse,
    DataResponse,
    ListResponse,
)
from src.presentation.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user,
)

router = APIRouter()


async def get_tag_service(
    tag_repository: TagRepository = Depends(get_tag_repository),
    appointment_repository: AppointmentRepository = Depends(
        get_appointment_repository
    ),
) -> TagService:
    """Resolve TagService with configured repositories."""

    return TagService(tag_repository, appointment_repository)


@router.get(
    "/",
    response_model=ListResponse[TagResponseDTO],
    summary="Listar tags",
    description="Retorna as tags disponíveis para seleção.",
)
async def list_tags_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Filtro por nome"),
    include_inactive: bool = Query(
        False,
        description="Inclui tags inativas (apenas administradores)",
    ),
    current_user: User = Depends(get_current_active_user),
    service: TagService = Depends(get_tag_service),
) -> ListResponse[TagResponseDTO]:
    """List all tags respecting pagination and permissions."""

    # Apenas administradores podem visualizar tags inativas
    effective_include_inactive = (
        include_inactive and current_user.has_admin_privileges()
    )

    result = await service.list_tags(
        page=page,
        page_size=page_size,
        search=search,
        include_inactive=effective_include_inactive,
    )

    total = result["total"]
    per_page = result["page_size"]
    pages = max(1, math.ceil(total / per_page)) if total else 1

    return ListResponse(
        success=result["success"],
        message=result.get("message"),
        data=result["tags"],
        total=total,
        page=result["page"],
        per_page=per_page,
        pages=pages,
    )


@router.post(
    "/",
    response_model=DataResponse[TagResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Criar tag",
)
async def create_tag_endpoint(
    payload: TagCreateDTO,
    service: TagService = Depends(get_tag_service),
    _: User = Depends(get_current_admin_user),
) -> DataResponse[TagResponseDTO]:
    """Create a new tag entry."""

    result = await service.create_tag(payload)
    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "conflict":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=result["message"]
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
        )

    return DataResponse(
        success=True,
        message=result["message"],
        data=result["tag"],
    )


@router.patch(
    "/{tag_id}",
    response_model=DataResponse[TagResponseDTO],
    summary="Atualizar tag",
)
async def update_tag_endpoint(
    tag_id: str,
    payload: TagUpdateDTO,
    service: TagService = Depends(get_tag_service),
    _: User = Depends(get_current_admin_user),
) -> DataResponse[TagResponseDTO]:
    """Update tag attributes."""

    result = await service.update_tag(tag_id, payload)
    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=result["message"]
            )
        if error_code == "conflict":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=result["message"]
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
        )

    return DataResponse(
        success=True,
        message=result["message"],
        data=result["tag"],
    )


@router.delete(
    "/{tag_id}",
    response_model=BaseResponse,
    summary="Remover tag",
)
async def delete_tag_endpoint(
    tag_id: str,
    service: TagService = Depends(get_tag_service),
    _: User = Depends(get_current_admin_user),
) -> BaseResponse:
    """Delete a tag when no appointment is referencing it."""

    result = await service.delete_tag(tag_id)
    if not result["success"]:
        error_code = result.get("error_code")
        status_map = {
            "not_found": status.HTTP_404_NOT_FOUND,
            "in_use": status.HTTP_409_CONFLICT,
        }
        raise HTTPException(
            status_code=status_map.get(error_code, status.HTTP_400_BAD_REQUEST),
            detail=result["message"],
        )

    return BaseResponse(success=True, message=result["message"])
