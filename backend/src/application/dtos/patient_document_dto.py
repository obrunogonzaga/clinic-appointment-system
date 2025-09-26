"""DTOs for patient document operations."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from src.domain.entities.patient_document import DocumentStatus


class PresignUploadRequestDTO(BaseModel):
    """Input payload required to request a presigned upload URL."""

    patient_id: str = Field(..., description="Identificador do paciente")
    file_name: str = Field(..., description="Nome original do arquivo")
    content_type: str = Field(..., description="MIME type do arquivo")
    file_size: int = Field(..., gt=0, description="Tamanho do arquivo em bytes")


class PresignUploadResponseDTO(BaseModel):
    """Returned data for performing the direct upload."""

    document_id: str = Field(..., description="Identificador do documento")
    upload_url: str = Field(..., description="URL pré-assinada para upload")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Cabeçalhos adicionais necessários no upload",
    )
    expires_in: int = Field(..., description="Tempo de expiração do link em segundos")
    storage_key: str = Field(..., description="Chave do objeto no bucket")


class ConfirmUploadRequestDTO(BaseModel):
    """Payload utilizado para confirmar um upload concluído."""

    file_size: int = Field(..., gt=0, description="Tamanho final do arquivo em bytes")
    etag: Optional[str] = Field(
        None, description="ETag retornado pelo storage (quando disponível)"
    )


class PatientDocumentDTO(BaseModel):
    """Metadata exposta via API para documentos de paciente."""

    id: str = Field(..., description="Identificador do documento")
    appointment_id: str = Field(..., description="ID do agendamento")
    patient_id: str = Field(..., description="Identificador do paciente")
    original_file_name: str = Field(
        ..., description="Nome original do arquivo enviado"
    )
    sanitized_file_name: str = Field(
        ..., description="Nome sanitizado do arquivo"
    )
    content_type: str = Field(..., description="MIME type do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")
    status: DocumentStatus = Field(..., description="Status atual do documento")
    storage_key: str = Field(..., description="Chave do objeto no bucket")
    uploader_user_id: Optional[str] = Field(
        None, description="Usuário que realizou o upload"
    )
    source_ip: Optional[str] = Field(
        None, description="IP de origem registrado no upload"
    )
    created_at: datetime = Field(..., description="Data de criação do registro")
    uploaded_at: Optional[datetime] = Field(
        None, description="Data de confirmação do upload"
    )
    deleted_at: Optional[datetime] = Field(
        None, description="Data da exclusão lógica"
    )
    deleted_by: Optional[str] = Field(
        None, description="Usuário responsável pela exclusão"
    )
    etag: Optional[str] = Field(None, description="ETag informado pelo storage")


class PatientDocumentListResponseDTO(BaseModel):
    """Wrapper para resposta de listagem de documentos."""

    documents: List[PatientDocumentDTO] = Field(
        default_factory=list, description="Lista de documentos"
    )


class DownloadUrlResponseDTO(BaseModel):
    """Resposta contendo uma URL temporária de download."""

    url: str = Field(..., description="URL pré-assinada para download")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
