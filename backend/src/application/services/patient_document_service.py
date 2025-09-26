"""Business logic for managing patient document uploads."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from src.application.dtos.patient_document_dto import (
    PatientDocumentConfirmRequestDTO,
    PatientDocumentDownloadURLDTO,
    PatientDocumentMetadataDTO,
    PatientDocumentPresignRequestDTO,
    PatientDocumentPresignResponseDTO,
)
from src.domain.base import DomainException, DomainValidationException
from src.domain.entities.patient_document import (
    PatientDocument,
    PatientDocumentStatus,
)
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)
from src.domain.repositories.patient_document_repository_interface import (
    PatientDocumentRepositoryInterface,
)
from src.infrastructure.config import Settings
from src.infrastructure.services.r2_storage_service import R2StorageService


class PatientDocumentService:
    """Coordinate patient document flows between storage and persistence."""

    def __init__(
        self,
        document_repository: PatientDocumentRepositoryInterface,
        appointment_repository: AppointmentRepositoryInterface,
        storage_service: R2StorageService,
        settings: Settings,
    ) -> None:
        self._documents = document_repository
        self._appointments = appointment_repository
        self._storage = storage_service
        self._settings = settings

    async def generate_presigned_upload(
        self,
        appointment_id: str,
        request: PatientDocumentPresignRequestDTO,
        *,
        uploader_user_id: str,
        tenant_id: Optional[str],
    ) -> PatientDocumentPresignResponseDTO:
        await self._ensure_appointment_exists(appointment_id)
        self._validate_file_constraints(
            request.file_name, request.content_type, request.file_size
        )
        sanitized_filename = self._sanitize_filename(request.file_name)
        patient_segment = self._sanitize_path_segment(request.patient_id)
        now = datetime.utcnow()
        object_key = (
            f"patients/{patient_segment}/appointments/{appointment_id}/"
            f"{now:%Y/%m}/{uuid4().hex}_{sanitized_filename}"
        )

        document = PatientDocument(
            appointment_id=appointment_id,
            patient_id=request.patient_id,
            tenant_id=tenant_id,
            file_name=request.file_name,
            sanitized_file_name=sanitized_filename,
            storage_key=object_key,
            content_type=request.content_type,
            file_size=request.file_size,
            uploader_user_id=uploader_user_id,
        )
        await self._documents.create(document)

        expires_at = self._storage.build_expiration()
        upload_url = self._storage.generate_presigned_put(
            object_key,
            content_type=request.content_type,
            expires_in=self._settings.r2_presign_ttl_seconds,
        )

        return PatientDocumentPresignResponseDTO(
            document_id=str(document.id),
            upload_url=upload_url,
            headers={"Content-Type": request.content_type},
            storage_key=object_key,
            expires_at=expires_at,
        )

    async def confirm_upload(
        self,
        appointment_id: str,
        document_id: str,
        request: PatientDocumentConfirmRequestDTO,
        *,
        user_id: str,
        source_ip: Optional[str],
        tenant_id: Optional[str],
    ) -> PatientDocumentMetadataDTO:
        document = await self._documents.get_by_id(document_id)
        if not document or document.appointment_id != appointment_id:
            raise DomainException("Documento não encontrado para este agendamento")
        self._ensure_tenant_access(document, tenant_id)

        if document.is_deleted():
            raise DomainException("Documento removido não pode ser confirmado")
        if document.status == PatientDocumentStatus.UPLOADED:
            return PatientDocumentMetadataDTO.from_entity(document)

        updates = {
            "status": PatientDocumentStatus.UPLOADED,
            "uploaded_at": datetime.utcnow(),
            "uploader_user_id": document.uploader_user_id or user_id,
            "source_ip": source_ip,
        }
        if request.etag:
            updates["etag"] = request.etag

        updated = await self._documents.update_fields(document_id, updates)
        if not updated:
            raise DomainException(
                "Não foi possível atualizar o status do documento após o upload"
            )
        return PatientDocumentMetadataDTO.from_entity(updated)

    async def list_documents(
        self,
        appointment_id: str,
        *,
        tenant_id: Optional[str],
        include_deleted: bool = False,
    ) -> List[PatientDocumentMetadataDTO]:
        await self._ensure_appointment_exists(appointment_id)
        documents = await self._documents.list_by_appointment(
            appointment_id,
            tenant_id=tenant_id,
            include_deleted=include_deleted,
        )
        return [PatientDocumentMetadataDTO.from_entity(doc) for doc in documents]

    async def generate_download_url(
        self,
        appointment_id: str,
        document_id: str,
        *,
        tenant_id: Optional[str],
    ) -> PatientDocumentDownloadURLDTO:
        document = await self._documents.get_by_id(document_id)
        if not document or document.appointment_id != appointment_id:
            raise DomainException("Documento não encontrado para este agendamento")
        self._ensure_tenant_access(document, tenant_id)
        if not document.is_upload_complete():
            raise DomainException(
                "Documento ainda não disponível para download"
            )
        if document.is_deleted():
            raise DomainException("Documento removido não pode ser baixado")

        expires_at = self._storage.build_expiration()
        download_url = self._storage.generate_presigned_get(
            document.storage_key,
            expires_in=self._settings.r2_presign_ttl_seconds,
        )
        return PatientDocumentDownloadURLDTO(
            download_url=download_url,
            expires_at=expires_at,
        )

    async def delete_document(
        self,
        appointment_id: str,
        document_id: str,
        *,
        tenant_id: Optional[str],
        user_id: str,
        hard: bool = False,
    ) -> PatientDocumentMetadataDTO:
        document = await self._documents.get_by_id(document_id)
        if not document or document.appointment_id != appointment_id:
            raise DomainException("Documento não encontrado para este agendamento")
        self._ensure_tenant_access(document, tenant_id)

        if hard:
            # Remove file first to avoid dangling metadata when storage fails.
            self._storage.delete_object(document.storage_key)
            updated = await self._documents.update_fields(
                document_id,
                {
                    "status": PatientDocumentStatus.DELETED,
                    "deleted_at": datetime.utcnow(),
                    "deleted_by": user_id,
                    "hard_deleted_at": datetime.utcnow(),
                },
            )
            # Keep metadata for audit purposes even on hard delete
            if not updated:
                raise DomainException("Falha ao registrar exclusão do documento")
            return PatientDocumentMetadataDTO.from_entity(updated)

        updates = {
            "status": PatientDocumentStatus.DELETED,
            "deleted_at": datetime.utcnow(),
            "deleted_by": user_id,
        }
        updated = await self._documents.update_fields(document_id, updates)
        if not updated:
            raise DomainException("Falha ao excluir documento")
        return PatientDocumentMetadataDTO.from_entity(updated)

    async def _ensure_appointment_exists(self, appointment_id: str) -> None:
        appointment = await self._appointments.find_by_id(appointment_id)
        if not appointment:
            raise DomainException("Agendamento não encontrado")

    def _validate_file_constraints(
        self, file_name: str, content_type: str, file_size: int
    ) -> None:
        if content_type not in self._settings.allowed_mime_list:
            raise DomainValidationException(
                "Tipo de arquivo não permitido", field="content_type"
            )
        if file_size > self._settings.patient_doc_max_upload_bytes:
            raise DomainValidationException(
                "Arquivo excede o tamanho máximo permitido",
                field="file_size",
            )
        extension = file_name.lower().rsplit(".", maxsplit=1)
        if len(extension) == 2:
            allowed_extensions = {
                "pdf": "application/pdf",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "webp": "image/webp",
                "heic": "image/heic",
            }
            ext = extension[1]
            if ext not in allowed_extensions:
                raise DomainValidationException(
                    "Extensão de arquivo não permitida", field="file_name"
                )
            if allowed_extensions[ext] != content_type:
                raise DomainValidationException(
                    "Extensão e MIME type não conferem", field="content_type"
                )

    def _sanitize_filename(self, file_name: str) -> str:
        name_part, dot, extension = file_name.rpartition(".")
        base = name_part if dot else extension
        ext = extension if dot else ""
        base = self._slugify(base) or "documento"
        if ext:
            return f"{base}.{ext.lower()}"
        return base

    def _sanitize_path_segment(self, raw: str) -> str:
        slug = self._slugify(raw)
        return slug or "unknown"

    def _slugify(self, raw: str) -> str:
        normalized = (
            unicodedata.normalize("NFKD", raw)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        normalized = normalized.lower()
        normalized = re.sub(r"[^a-z0-9-_]+", "-", normalized)
        normalized = normalized.strip("-")
        normalized = re.sub(r"-+", "-", normalized)
        return normalized

    def _ensure_tenant_access(
        self, document: PatientDocument, tenant_id: Optional[str]
    ) -> None:
        if document.tenant_id and tenant_id and document.tenant_id != tenant_id:
            raise DomainException("Documento não pertence a este tenant")
        if document.tenant_id and tenant_id is None:
            raise DomainException("Tenant obrigatório para acessar este documento")
