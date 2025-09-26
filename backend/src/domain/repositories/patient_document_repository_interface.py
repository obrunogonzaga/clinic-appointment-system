"""Repository contract for patient document metadata persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.domain.entities.patient_document import PatientDocument


class PatientDocumentRepositoryInterface(ABC):
    """Define operations for storing and retrieving patient documents metadata."""

    @abstractmethod
    async def create(self, document: PatientDocument) -> PatientDocument:
        """Persist a new patient document metadata entry."""

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[PatientDocument]:
        """Fetch a document by its identifier."""

    @abstractmethod
    async def list_by_appointment(
        self,
        appointment_id: str,
        *,
        tenant_id: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[PatientDocument]:
        """Return all documents associated with a specific appointment."""

    @abstractmethod
    async def update_fields(
        self, document_id: str, updates: Dict[str, object]
    ) -> Optional[PatientDocument]:
        """Apply partial updates to a document metadata entry."""

    @abstractmethod
    async def delete_permanently(self, document_id: str) -> bool:
        """Remove a document metadata entry from persistence."""
