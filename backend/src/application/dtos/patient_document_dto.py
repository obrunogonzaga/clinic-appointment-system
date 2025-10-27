"""DTOs for patient document operations."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field

from src.domain.entities.patient_document import PatientDocument, PatientDocumentStatus


class PatientDocumentPresignRequestDTO(BaseModel):
    """Payload required to request an upload pre-signed URL."""

    file_name: str = Field(..., description="Nome do arquivo a ser enviado")
    content_type: str = Field(..., description="MIME type informado pelo cliente")
    file_size: int = Field(..., ge=1, description="Tamanho do arquivo em bytes")
    patient_id: str = Field(..., description="Identificador do paciente")


class PatientDocumentPresignResponseDTO(BaseModel):
    """Response containing the pre-signed URL and metadata."""

    document_id: str = Field(..., description="Identificador do documento gerado")
    upload_url: str = Field(..., description="URL pré-assinada para envio via PUT")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Cabeçalhos obrigatórios para o upload",
    )
    storage_key: str = Field(..., description="Chave do objeto no bucket")
    expires_at: datetime = Field(
        ..., description="Momento em que a URL deixa de ser válida"
    )


class PatientDocumentConfirmRequestDTO(BaseModel):
    """Payload to confirm that the client uploaded the document successfully."""

    etag: Optional[str] = Field(
        None,
        description="ETag retornado pelo provedor S3/R2 após o upload",
    )


class PatientDocumentMetadataDTO(BaseModel):
    """Serializable representation of patient document metadata."""

    id: str
    appointment_id: str
    patient_id: str
    tenant_id: Optional[str]
    file_name: str
    sanitized_file_name: str
    storage_key: str
    content_type: str
    file_size: int
    status: PatientDocumentStatus
    uploader_user_id: Optional[str]
    created_at: datetime
    uploaded_at: Optional[datetime]
    source_ip: Optional[str]
    etag: Optional[str]
    deleted_at: Optional[datetime]
    deleted_by: Optional[str]
    hard_deleted_at: Optional[datetime]

    @classmethod
    def from_entity(cls, document: PatientDocument) -> "PatientDocumentMetadataDTO":
        return cls(
            id=str(document.id),
            appointment_id=document.appointment_id,
            patient_id=document.patient_id,
            tenant_id=document.tenant_id,
            file_name=document.file_name,
            sanitized_file_name=document.sanitized_file_name,
            storage_key=document.storage_key,
            content_type=document.content_type,
            file_size=document.file_size,
            status=document.status,
            uploader_user_id=document.uploader_user_id,
            created_at=document.created_at,
            uploaded_at=document.uploaded_at,
            source_ip=document.source_ip,
            etag=document.etag,
            deleted_at=document.deleted_at,
            deleted_by=document.deleted_by,
            hard_deleted_at=document.hard_deleted_at,
        )


class PatientDocumentDownloadURLDTO(BaseModel):
    """Response containing a pre-signed URL for downloading the document."""

    download_url: str = Field(..., description="URL pré-assinada para download via GET")
    expires_at: datetime = Field(..., description="Momento de expiração da URL")
