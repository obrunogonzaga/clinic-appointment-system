"""MongoDB repository for patient documents."""

from __future__ import annotations

from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from src.domain.entities.patient_document import DocumentStatus, PatientDocument
from src.domain.repositories.patient_document_repository_interface import (
    PatientDocumentRepositoryInterface,
)


class PatientDocumentRepository(PatientDocumentRepositoryInterface):
    """MongoDB implementation for storing patient document metadata."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database
        self.collection = database.patient_documents

    async def create_indexes(self) -> None:
        """Create indexes required for common access patterns."""

        await self.collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("appointment_id", ASCENDING),
                ("status", ASCENDING),
            ],
            name="tenant_appointment_status_idx",
        )
        await self.collection.create_index(
            [("tenant_id", ASCENDING), ("id", ASCENDING)],
            unique=True,
            name="tenant_document_unique_idx",
        )

    async def create(self, document: PatientDocument) -> PatientDocument:
        data = document.model_dump()
        data["id"] = str(document.id)
        await self.collection.insert_one(data)
        return document

    async def update(self, document: PatientDocument) -> PatientDocument:
        data = document.model_dump()
        data["id"] = str(document.id)

        updated = await self.collection.find_one_and_update(
            {"id": str(document.id), "tenant_id": document.tenant_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )

        if updated is None:
            return document

        updated.pop("_id", None)
        return PatientDocument(**updated)

    async def find_by_id(
        self, document_id: str, tenant_id: str
    ) -> Optional[PatientDocument]:
        doc = await self.collection.find_one(
            {"id": document_id, "tenant_id": tenant_id}
        )
        if doc is None:
            return None

        doc.pop("_id", None)
        return PatientDocument(**doc)

    async def list_by_appointment(
        self, appointment_id: str, tenant_id: str, include_deleted: bool = False
    ) -> List[PatientDocument]:
        query: dict[str, object] = {
            "appointment_id": appointment_id,
            "tenant_id": tenant_id,
        }

        if not include_deleted:
            query["status"] = {
                "$nin": [
                    DocumentStatus.SOFT_DELETED.value,
                    DocumentStatus.HARD_DELETED.value,
                ]
            }

        cursor = self.collection.find(query).sort("created_at", DESCENDING)
        documents: List[PatientDocument] = []
        async for doc in cursor:
            doc.pop("_id", None)
            documents.append(PatientDocument(**doc))

        return documents
