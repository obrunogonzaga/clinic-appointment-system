"""Patient document entity and status definitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from src.domain.base import Entity


class PatientDocumentStatus(str, Enum):
    """Possible lifecycle states for a patient document."""

    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    DELETED = "deleted"


class PatientDocument(Entity):
    """Metadata stored for each patient document uploaded to object storage."""

    appointment_id: str = Field(..., description="Agendamento associado")
    patient_id: str = Field(..., description="Identificador único do paciente")
    tenant_id: Optional[str] = Field(
        None, description="Identificador do tenant/cliente ao qual o documento pertence"
    )
    file_name: str = Field(..., description="Nome original do arquivo")
    sanitized_file_name: str = Field(
        ..., description="Nome sanitizado utilizado no objeto no storage"
    )
    storage_key: str = Field(..., description="Caminho da chave no bucket S3/R2")
    content_type: str = Field(..., description="MIME type detectado")
    file_size: int = Field(..., ge=0, description="Tamanho do arquivo em bytes")
    status: PatientDocumentStatus = Field(
        default=PatientDocumentStatus.PENDING, description="Status do upload"
    )
    uploader_user_id: Optional[str] = Field(
        None, description="Usuário responsável pelo envio"
    )
    uploaded_at: Optional[datetime] = Field(
        None, description="Momento em que o upload foi confirmado"
    )
    source_ip: Optional[str] = Field(
        None, description="Endereço IP registrado na confirmação"
    )
    etag: Optional[str] = Field(
        None, description="ETag retornado pelo provedor S3/R2"
    )
    deleted_at: Optional[datetime] = Field(
        None, description="Momento da exclusão lógica"
    )
    deleted_by: Optional[str] = Field(
        None, description="Usuário que realizou a exclusão lógica"
    )
    hard_deleted_at: Optional[datetime] = Field(
        None, description="Momento da remoção definitiva do objeto"
    )

    @field_validator("file_name", "sanitized_file_name", mode="before")
    @classmethod
    def _strip_strings(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("content_type")
    @classmethod
    def _validate_content_type(cls, value: str) -> str:
        if not value:
            raise ValueError("content_type não pode ser vazio")
        return value

    @field_validator("patient_id")
    @classmethod
    def _validate_patient_id(cls, value: str) -> str:
        if not value:
            raise ValueError("patient_id é obrigatório")
        return value

    def is_deleted(self) -> bool:
        """Return True when the document is soft deleted."""

        return self.deleted_at is not None

    def is_upload_complete(self) -> bool:
        """Return True if the document finished upload flow successfully."""

        return self.status == PatientDocumentStatus.UPLOADED
