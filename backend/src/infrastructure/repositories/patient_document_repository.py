"""MongoDB implementation for patient document repository."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, IndexModel

from src.domain.entities.patient_document import PatientDocument
from src.domain.repositories.patient_document_repository_interface import (
    PatientDocumentRepositoryInterface,
)


class PatientDocumentRepository(PatientDocumentRepositoryInterface):
    """Persist patient document metadata on MongoDB collections."""

    COLLECTION_NAME = "patient_documents"

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._database = database
        self._collection = database[self.COLLECTION_NAME]

    async def ensure_indexes(self) -> None:
        """Create indexes to speed up lookups."""

        indexes = [
            IndexModel([("appointment_id", ASCENDING)], name="appointment_idx"),
            IndexModel([("patient_id", ASCENDING)], name="patient_idx"),
            IndexModel([("tenant_id", ASCENDING)], name="tenant_idx"),
            IndexModel([("created_at", ASCENDING)], name="created_at_idx"),
            IndexModel([("deleted_at", ASCENDING)], name="deleted_at_idx"),
        ]
        try:
            await self._collection.create_indexes(indexes)
        except Exception:
            # Ignore indexing errors (already exists, etc.)
            pass

    async def create(self, document: PatientDocument) -> PatientDocument:
        payload = document.model_dump()
        payload["id"] = str(document.id)
        await self._collection.insert_one(payload)
        return document

    async def get_by_id(self, document_id: str) -> Optional[PatientDocument]:
        doc = await self._collection.find_one({"id": document_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return PatientDocument(**doc)

    async def list_by_appointment(
        self,
        appointment_id: str,
        *,
        tenant_id: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[PatientDocument]:
        query: Dict[str, object] = {"appointment_id": appointment_id}
        if tenant_id is not None:
            query["tenant_id"] = tenant_id
        if not include_deleted:
            query["deleted_at"] = {"$exists": False}

        cursor = self._collection.find(query).sort("created_at", ASCENDING)
        results: List[PatientDocument] = []
        async for raw in cursor:
            raw.pop("_id", None)
            results.append(PatientDocument(**raw))
        return results

    async def update_fields(
        self, document_id: str, updates: Dict[str, object]
    ) -> Optional[PatientDocument]:
        if not updates:
            return await self.get_by_id(document_id)

        updates = {**updates, "updated_at": datetime.utcnow()}
        result = await self._collection.find_one_and_update(
            {"id": document_id},
            {"$set": updates},
            return_document=True,
        )
        if not result:
            return None
        result.pop("_id", None)
        return PatientDocument(**result)

    async def delete_permanently(self, document_id: str) -> bool:
        delete_result = await self._collection.delete_one({"id": document_id})
        return delete_result.deleted_count > 0
