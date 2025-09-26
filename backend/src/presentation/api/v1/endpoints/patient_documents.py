"""Endpoints to manage patient documents and Cloudflare R2 uploads."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status

from src.application.dtos.patient_document_dto import (
    PatientDocumentConfirmRequestDTO,
    PatientDocumentDownloadURLDTO,
    PatientDocumentMetadataDTO,
    PatientDocumentPresignRequestDTO,
    PatientDocumentPresignResponseDTO,
)
from src.application.services.patient_document_service import (
    PatientDocumentService,
)
from src.domain.entities.user import User
from src.presentation.api.responses import DataResponse, ListResponse
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import get_patient_document_service

router = APIRouter()


def _resolve_user_identifier(user: User) -> str:
    return getattr(user, "id", None) or getattr(user, "email", "unknown")


def _resolve_tenant_id(user: User, header_tenant: Optional[str]) -> Optional[str]:
    if header_tenant:
        return header_tenant
    for attr in ("tenant_id", "department"):
        if hasattr(user, attr):
            value = getattr(user, attr)
            if value:
                return str(value)
    metadata = getattr(user, "metadata", None)
    if metadata is not None:
        dept = getattr(metadata, "department", None)
        if dept:
            return str(dept)
    return None


def _ensure_user_can_manage_documents(user: User) -> None:
    role_value = getattr(user, "role", None)
    if getattr(user, "is_admin", False):
        return
    if role_value is not None:
        role = getattr(role_value, "value", role_value)
        if str(role) in {"admin", "colaborador"}:
            return
    # Legacy users without role: allow collaborators by default
    if role_value is None and not getattr(user, "is_admin", False):
        # Collaborators are represented by non-admin active users
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Usuário não possui permissão para gerenciar documentos",
    )


@router.post(
    "/{appointment_id}/documents/presign-upload",
    response_model=DataResponse[PatientDocumentPresignResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar URL pré-assinada para upload",
)
async def presign_patient_document_upload(
    appointment_id: str,
    payload: PatientDocumentPresignRequestDTO,
    service: PatientDocumentService = Depends(get_patient_document_service),
    current_user: User = Depends(get_current_active_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> DataResponse[PatientDocumentPresignResponseDTO]:
    """Create pre-signed URL to upload a new patient document."""

    _ensure_user_can_manage_documents(current_user)
    tenant_id = _resolve_tenant_id(current_user, x_tenant_id)

    result = await service.generate_presigned_upload(
        appointment_id,
        payload,
        uploader_user_id=_resolve_user_identifier(current_user),
        tenant_id=tenant_id,
    )
    return DataResponse(
        success=True,
        message="URL de upload gerada com sucesso",
        data=result,
    )


@router.post(
    "/{appointment_id}/documents/{document_id}/confirm",
    response_model=DataResponse[PatientDocumentMetadataDTO],
    summary="Confirmar upload do documento",
)
async def confirm_patient_document_upload(
    appointment_id: str,
    document_id: str,
    payload: PatientDocumentConfirmRequestDTO,
    request: Request,
    service: PatientDocumentService = Depends(get_patient_document_service),
    current_user: User = Depends(get_current_active_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> DataResponse[PatientDocumentMetadataDTO]:
    """Confirm that the document was successfully uploaded to R2."""

    _ensure_user_can_manage_documents(current_user)
    tenant_id = _resolve_tenant_id(current_user, x_tenant_id)
    source_ip = request.client.host if request.client else None

    document = await service.confirm_upload(
        appointment_id,
        document_id,
        payload,
        user_id=_resolve_user_identifier(current_user),
        source_ip=source_ip,
        tenant_id=tenant_id,
    )
    return DataResponse(
        success=True,
        message="Upload confirmado",
        data=document,
    )


@router.get(
    "/{appointment_id}/documents",
    response_model=ListResponse[PatientDocumentMetadataDTO],
    summary="Listar documentos do paciente",
)
async def list_patient_documents(
    appointment_id: str,
    service: PatientDocumentService = Depends(get_patient_document_service),
    current_user: User = Depends(get_current_active_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> ListResponse[PatientDocumentMetadataDTO]:
    """List metadata of patient documents for a given appointment."""

    _ensure_user_can_manage_documents(current_user)
    tenant_id = _resolve_tenant_id(current_user, x_tenant_id)

    documents = await service.list_documents(
        appointment_id,
        tenant_id=tenant_id,
        include_deleted=False,
    )
    total = len(documents)
    return ListResponse(
        success=True,
        message="Documentos recuperados com sucesso",
        data=list(documents),
        total=total,
        page=1,
        per_page=total if total > 0 else 0,
        pages=1,
    )


@router.get(
    "/{appointment_id}/documents/{document_id}/download-url",
    response_model=DataResponse[PatientDocumentDownloadURLDTO],
    summary="Gerar URL de download do documento",
)
async def generate_patient_document_download_url(
    appointment_id: str,
    document_id: str,
    service: PatientDocumentService = Depends(get_patient_document_service),
    current_user: User = Depends(get_current_active_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> DataResponse[PatientDocumentDownloadURLDTO]:
    """Generate a pre-signed GET URL for the stored document."""

    _ensure_user_can_manage_documents(current_user)
    tenant_id = _resolve_tenant_id(current_user, x_tenant_id)

    download = await service.generate_download_url(
        appointment_id,
        document_id,
        tenant_id=tenant_id,
    )
    return DataResponse(
        success=True,
        message="URL de download gerada",
        data=download,
    )


@router.delete(
    "/{appointment_id}/documents/{document_id}",
    response_model=DataResponse[PatientDocumentMetadataDTO],
    summary="Excluir documento",
)
async def delete_patient_document(
    appointment_id: str,
    document_id: str,
    hard: bool = Query(
        False,
        description="Quando verdadeiro remove também do storage (hard delete)",
    ),
    service: PatientDocumentService = Depends(get_patient_document_service),
    current_user: User = Depends(get_current_active_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> DataResponse[PatientDocumentMetadataDTO]:
    """Soft delete (default) or hard delete a patient document."""

    _ensure_user_can_manage_documents(current_user)
    tenant_id = _resolve_tenant_id(current_user, x_tenant_id)

    document = await service.delete_document(
        appointment_id,
        document_id,
        tenant_id=tenant_id,
        user_id=_resolve_user_identifier(current_user),
        hard=hard,
    )
    message = "Documento removido permanentemente" if hard else "Documento removido"
    return DataResponse(
        success=True,
        message=message,
        data=document,
    )
