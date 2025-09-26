"""API endpoints for managing patient documents linked to appointments."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query, status

from src.application.dtos.patient_document_dto import (
    ConfirmUploadRequestDTO,
    DownloadUrlResponseDTO,
    PatientDocumentDTO,
    PatientDocumentListResponseDTO,
    PresignUploadRequestDTO,
    PresignUploadResponseDTO,
)
from src.application.services.patient_document_service import PatientDocumentService
from src.infrastructure.container import (
    get_app_settings,
    get_patient_document_repository,
    get_r2_storage_client,
)
from src.presentation.api.responses import DataResponse
from src.presentation.dependencies import get_request_context

router = APIRouter(
    prefix="/appointments/{appointment_id}/documents",
    tags=["Appointment Documents"],
)


async def get_patient_document_service() -> PatientDocumentService:
    repository = await get_patient_document_repository()
    storage = await get_r2_storage_client()
    settings = await get_app_settings()
    return PatientDocumentService(repository, storage, settings)


@router.post(
    "/presign",
    response_model=DataResponse[PresignUploadResponseDTO],
    status_code=status.HTTP_201_CREATED,
)
async def create_document_presign_url(
    payload: PresignUploadRequestDTO,
    appointment_id: str = Path(..., description="ID do agendamento"),
    service: PatientDocumentService = Depends(get_patient_document_service),
    context=Depends(get_request_context),
) -> DataResponse[PresignUploadResponseDTO]:
    """Return a presigned URL for uploading a new document."""

    result = await service.create_presigned_upload(
        appointment_id=appointment_id,
        payload=payload,
        context=context,
    )
    return DataResponse(
        data=result,
        message="URL pré-assinada gerada com sucesso",
    )


@router.post(
    "/{document_id}/confirm",
    response_model=DataResponse[PatientDocumentDTO],
)
async def confirm_document_upload(
    payload: ConfirmUploadRequestDTO,
    appointment_id: str = Path(..., description="ID do agendamento"),
    document_id: str = Path(..., description="ID do documento"),
    service: PatientDocumentService = Depends(get_patient_document_service),
    context=Depends(get_request_context),
) -> DataResponse[PatientDocumentDTO]:
    """Mark a document upload as complete after PUT to storage."""

    document = await service.confirm_upload(
        appointment_id=appointment_id,
        document_id=document_id,
        payload=payload,
        context=context,
    )
    return DataResponse(data=document, message="Upload confirmado com sucesso")


@router.get(
    "",
    response_model=DataResponse[PatientDocumentListResponseDTO],
)
async def list_documents(
    appointment_id: str = Path(..., description="ID do agendamento"),
    service: PatientDocumentService = Depends(get_patient_document_service),
    context=Depends(get_request_context),
) -> DataResponse[PatientDocumentListResponseDTO]:
    """List active documents for a specific appointment."""

    documents = await service.list_documents(
        appointment_id=appointment_id,
        context=context,
    )
    return DataResponse(data=documents)


@router.get(
    "/{document_id}/download",
    response_model=DataResponse[DownloadUrlResponseDTO],
)
async def get_download_url(
    appointment_id: str = Path(..., description="ID do agendamento"),
    document_id: str = Path(..., description="ID do documento"),
    service: PatientDocumentService = Depends(get_patient_document_service),
    context=Depends(get_request_context),
) -> DataResponse[DownloadUrlResponseDTO]:
    """Generate a temporary download URL for a document."""

    download = await service.create_download_url(
        appointment_id=appointment_id,
        document_id=document_id,
        context=context,
    )
    return DataResponse(data=download)


@router.delete(
    "/{document_id}",
    response_model=DataResponse[PatientDocumentDTO],
)
async def delete_document(
    appointment_id: str = Path(..., description="ID do agendamento"),
    document_id: str = Path(..., description="ID do documento"),
    hard: bool = Query(False, description="Define se a exclusão será definitiva"),
    service: PatientDocumentService = Depends(get_patient_document_service),
    context=Depends(get_request_context),
) -> DataResponse[PatientDocumentDTO]:
    """Soft delete by default, or hard delete when requested by admins."""

    document = await service.delete_document(
        appointment_id=appointment_id,
        document_id=document_id,
        hard_delete=hard,
        context=context,
    )
    message = "Documento removido permanentemente" if hard else "Documento removido"
    return DataResponse(data=document, message=message)
