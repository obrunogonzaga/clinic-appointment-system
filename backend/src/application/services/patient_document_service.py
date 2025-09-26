"""Service layer for handling patient document lifecycle."""

from __future__ import annotations

import os
import unicodedata
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from src.application.common import RequestContext, UserRole
from src.application.dtos.patient_document_dto import (
    ConfirmUploadRequestDTO,
    DownloadUrlResponseDTO,
    PatientDocumentDTO,
    PatientDocumentListResponseDTO,
    PresignUploadRequestDTO,
    PresignUploadResponseDTO,
)
from src.domain.base import DomainValidationException, EntityNotFoundException
from src.domain.entities.patient_document import DocumentStatus, PatientDocument
from src.domain.repositories.patient_document_repository_interface import (
    PatientDocumentRepositoryInterface,
)
from src.infrastructure.config import Settings
from src.infrastructure.storage.r2_client import R2StorageClient


class PatientDocumentService:
    """Coordinate operations between API, storage and persistence."""

    def __init__(
        self,
        repository: PatientDocumentRepositoryInterface,
        storage_client: R2StorageClient,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._storage = storage_client
        self._settings = settings

    async def create_presigned_upload(
        self,
        *,
        appointment_id: str,
        payload: PresignUploadRequestDTO,
        context: RequestContext,
    ) -> PresignUploadResponseDTO:
        """Validate input, persist metadata and return upload instructions."""

        self._ensure_storage_requirements()
        self._validate_file_constraints(payload)

        sanitized_filename = self._sanitize_filename(payload.file_name)
        safe_patient_id = self._slugify(payload.patient_id)
        storage_key = self._build_storage_key(
            patient_id=safe_patient_id,
            appointment_id=appointment_id,
            filename=sanitized_filename,
        )

        document = PatientDocument(
            id=uuid4(),
            appointment_id=appointment_id,
            tenant_id=context.tenant_id,
            patient_id=payload.patient_id,
            original_file_name=payload.file_name,
            sanitized_file_name=sanitized_filename,
            content_type=payload.content_type,
            file_size=payload.file_size,
            storage_key=storage_key,
            bucket=self._storage.bucket,
            uploader_user_id=context.user_id,
            source_ip=context.source_ip,
        )

        await self._repository.create(document)

        presign = self._storage.generate_presigned_put(
            key=storage_key,
            content_type=payload.content_type,
        )

        return PresignUploadResponseDTO(
            document_id=str(document.id),
            upload_url=presign["url"],
            headers=presign.get("headers", {}),
            expires_in=self._settings.r2_presign_ttl_seconds,
            storage_key=storage_key,
        )

    async def confirm_upload(
        self,
        *,
        appointment_id: str,
        document_id: str,
        payload: ConfirmUploadRequestDTO,
        context: RequestContext,
    ) -> PatientDocumentDTO:
        """Mark a document as uploaded after a successful PUT to R2."""

        document = await self._get_document_or_404(document_id, context.tenant_id)
        self._ensure_same_appointment(document, appointment_id)

        if document.status not in {DocumentStatus.PENDING, DocumentStatus.AVAILABLE}:
            raise DomainValidationException(
                "Documento não pode ser confirmado no estado atual",
                field="status",
            )

        if payload.file_size > self._settings.patient_docs_max_upload_bytes:
            raise DomainValidationException(
                "Tamanho do arquivo excede o limite configurado",
                field="file_size",
            )

        document.file_size = payload.file_size
        document.mark_uploaded(uploaded_at=datetime.utcnow(), etag=payload.etag)
        updated = await self._repository.update(document)
        return self._to_dto(updated)

    async def list_documents(
        self, *, appointment_id: str, context: RequestContext
    ) -> PatientDocumentListResponseDTO:
        """Return all non-deleted documents for the appointment."""

        documents = await self._repository.list_by_appointment(
            appointment_id=appointment_id,
            tenant_id=context.tenant_id,
            include_deleted=False,
        )
        return PatientDocumentListResponseDTO(
            documents=[self._to_dto(doc) for doc in documents]
        )

    async def create_download_url(
        self,
        *,
        appointment_id: str,
        document_id: str,
        context: RequestContext,
    ) -> DownloadUrlResponseDTO:
        """Generate a presigned GET URL for the requested document."""

        document = await self._get_document_or_404(document_id, context.tenant_id)
        self._ensure_same_appointment(document, appointment_id)

        if document.status != DocumentStatus.AVAILABLE:
            raise DomainValidationException(
                "Documento não está disponível para download",
                field="status",
            )

        url = self._storage.generate_presigned_get(key=document.storage_key)
        return DownloadUrlResponseDTO(
            url=url, expires_in=self._settings.r2_presign_ttl_seconds
        )

    async def delete_document(
        self,
        *,
        appointment_id: str,
        document_id: str,
        hard_delete: bool,
        context: RequestContext,
    ) -> PatientDocumentDTO:
        """Soft delete (default) or hard delete a document."""

        document = await self._get_document_or_404(document_id, context.tenant_id)
        self._ensure_same_appointment(document, appointment_id)

        if document.status == DocumentStatus.HARD_DELETED:
            raise DomainValidationException(
                "Documento já foi removido permanentemente",
                field="status",
            )

        now = datetime.utcnow()

        if hard_delete:
            if context.role != UserRole.ADMIN:
                raise DomainValidationException(
                    "Somente administradores podem realizar exclusão definitiva",
                    field="role",
                )

            await self._storage.delete_object(key=document.storage_key)
            document.mark_hard_deleted(deleted_at=now, user_id=context.user_id)
        else:
            if document.status == DocumentStatus.SOFT_DELETED:
                raise DomainValidationException(
                    "Documento já está excluído",
                    field="status",
                )
            document.mark_soft_deleted(deleted_at=now, user_id=context.user_id)

        updated = await self._repository.update(document)
        return self._to_dto(updated)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_storage_requirements(self) -> None:
        if not self._settings.r2_access_key_id or not self._settings.r2_secret_access_key:
            raise DomainValidationException(
                "Credenciais do R2 não configuradas corretamente",
                field="R2_ACCESS_KEY_ID",
            )
        if not self._settings.r2_bucket_patient_docs:
            raise DomainValidationException(
                "Bucket de documentos não configurado",
                field="R2_BUCKET_PATIENT_DOCS",
            )

    def _validate_file_constraints(self, payload: PresignUploadRequestDTO) -> None:
        if (
            payload.content_type
            not in self._settings.allowed_patient_document_mime_types
        ):
            raise DomainValidationException(
                "Tipo de arquivo não permitido",
                field="content_type",
            )

        if payload.file_size > self._settings.patient_docs_max_upload_bytes:
            raise DomainValidationException(
                "Tamanho do arquivo excede o limite configurado",
                field="file_size",
            )

    async def _get_document_or_404(
        self, document_id: str, tenant_id: str
    ) -> PatientDocument:
        document = await self._repository.find_by_id(document_id, tenant_id)
        if not document:
            raise EntityNotFoundException("PatientDocument", document_id)
        return document

    @staticmethod
    def _ensure_same_appointment(
        document: PatientDocument, appointment_id: str
    ) -> None:
        if document.appointment_id != appointment_id:
            raise DomainValidationException(
                "Documento não pertence ao agendamento informado",
                field="appointment_id",
            )

    def _to_dto(self, document: PatientDocument) -> PatientDocumentDTO:
        return PatientDocumentDTO(
            id=str(document.id),
            appointment_id=document.appointment_id,
            patient_id=document.patient_id,
            original_file_name=document.original_file_name,
            sanitized_file_name=document.sanitized_file_name,
            content_type=document.content_type,
            file_size=document.file_size,
            status=document.status,
            storage_key=document.storage_key,
            uploader_user_id=document.uploader_user_id,
            source_ip=document.source_ip,
            created_at=document.created_at,
            uploaded_at=document.uploaded_at,
            deleted_at=document.deleted_at,
            deleted_by=document.deleted_by,
            etag=document.etag,
        )

    def _build_storage_key(
        self, *, patient_id: str, appointment_id: str, filename: str
    ) -> str:
        now = datetime.utcnow()
        return (
            f"patients/{patient_id}/appointments/{appointment_id}/"
            f"{now.year:04d}/{now.month:02d}/{uuid4()}_{filename}"
        )

    def _sanitize_filename(self, filename: str) -> str:
        name = Path(filename).name
        stem, ext = os.path.splitext(name)
        sanitized_stem = self._slugify(stem) or "documento"
        sanitized_ext = ext.lower()
        return f"{sanitized_stem}{sanitized_ext}"

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        allowed = [c if c.isalnum() else "-" for c in ascii_value]
        slug = "".join(allowed)
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-").lower()
