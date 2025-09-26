"""Patient document entity and status definitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from src.domain.base import Entity


class DocumentStatus(str, Enum):
    """Possible lifecycle states for a patient document."""

    PENDING = "pending"
    AVAILABLE = "available"
    SOFT_DELETED = "soft_deleted"
    HARD_DELETED = "hard_deleted"


class PatientDocument(Entity):
    """Metadata for a patient document stored in Cloudflare R2."""

    appointment_id: str = Field(..., description="ID do agendamento associado")
    tenant_id: str = Field(..., description="Tenant ao qual o documento pertence")
    patient_id: str = Field(..., description="Identificador lógico do paciente")
    original_file_name: str = Field(
        ..., description="Nome original do arquivo enviado pelo usuário"
    )
    sanitized_file_name: str = Field(
        ..., description="Nome do arquivo sanitizado utilizado no storage"
    )
    content_type: str = Field(..., description="MIME type do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")
    storage_key: str = Field(..., description="Chave completa utilizada no bucket")
    bucket: Optional[str] = Field(
        None, description="Nome do bucket onde o arquivo está armazenado"
    )
    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        description="Status atual do documento",
    )
    uploader_user_id: Optional[str] = Field(
        None, description="Usuário responsável pelo upload"
    )
    source_ip: Optional[str] = Field(
        None, description="Origem do upload para auditoria"
    )
    uploaded_at: Optional[datetime] = Field(
        None, description="Data de confirmação do upload"
    )
    deleted_at: Optional[datetime] = Field(
        None, description="Data de deleção lógica"
    )
    deleted_by: Optional[str] = Field(
        None, description="Usuário que realizou a deleção lógica"
    )
    hard_deleted_at: Optional[datetime] = Field(
        None, description="Data de remoção física no storage"
    )
    etag: Optional[str] = Field(
        None, description="ETag retornado pelo storage durante o upload"
    )

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, value: int) -> int:
        """Ensure file size is positive."""

        if value <= 0:
            raise ValueError("Tamanho do arquivo deve ser maior que zero")
        return value

    def mark_uploaded(self, *, uploaded_at: datetime, etag: Optional[str]) -> None:
        """Mark the document as fully uploaded and available."""

        self.status = DocumentStatus.AVAILABLE
        self.uploaded_at = uploaded_at
        self.etag = etag
        self.mark_as_updated()

    def mark_soft_deleted(self, *, deleted_at: datetime, user_id: str) -> None:
        """Perform a soft delete on the document."""

        self.status = DocumentStatus.SOFT_DELETED
        self.deleted_at = deleted_at
        self.deleted_by = user_id
        self.mark_as_updated()

    def mark_hard_deleted(self, *, deleted_at: datetime, user_id: str) -> None:
        """Mark the document as permanently deleted."""

        self.status = DocumentStatus.HARD_DELETED
        self.deleted_at = deleted_at
        self.deleted_by = user_id
        self.hard_deleted_at = deleted_at
        self.mark_as_updated()
