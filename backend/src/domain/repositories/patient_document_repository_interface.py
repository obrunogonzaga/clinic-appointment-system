"""Repository interface for patient documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.patient_document import PatientDocument


class PatientDocumentRepositoryInterface(ABC):
    """Contract for patient document persistence operations."""

    @abstractmethod
    async def create(self, document: PatientDocument) -> PatientDocument:
        """Persist a new patient document metadata entry."""

    @abstractmethod
    async def update(self, document: PatientDocument) -> PatientDocument:
        """Persist updates to an existing document."""

    @abstractmethod
    async def find_by_id(
        self, document_id: str, tenant_id: str
    ) -> Optional[PatientDocument]:
        """Fetch a document by identifier scoped to a tenant."""

    @abstractmethod
    async def list_by_appointment(
        self, appointment_id: str, tenant_id: str, include_deleted: bool = False
    ) -> List[PatientDocument]:
        """Return documents linked to an appointment."""

    @abstractmethod
    async def create_indexes(self) -> None:
        """Ensure required indexes exist in the persistence layer."""
