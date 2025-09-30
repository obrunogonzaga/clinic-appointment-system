"""MongoDB implementation of ClientRepository."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

from src.domain.entities.client import Client
from src.domain.repositories.client_repository_interface import (
    ClientRepositoryInterface,
)
from src.domain.utils import normalize_cpf


class ClientRepository(ClientRepositoryInterface):
    """MongoDB persistence for clients."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.clients

    async def create(self, client: Client) -> Client:
        data = client.model_dump()
        data["id"] = str(data["id"])
        await self.collection.insert_one(data)
        return client

    async def update(
        self, client_id: str, update_data: Dict[str, Any]
    ) -> Optional[Client]:
        if not update_data:
            return await self.find_by_id(client_id)

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"id": client_id},
            {"$set": update_data},
        )
        return await self.find_by_id(client_id)

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        doc = await self.collection.find_one({"id": client_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return Client(**doc)

    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        normalized = normalize_cpf(cpf)
        if not normalized:
            return None

        doc = await self.collection.find_one({"cpf": normalized})
        if not doc:
            return None
        doc.pop("_id", None)
        return Client(**doc)

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Client]:
        query: Dict[str, Any] = {}
        if filters:
            query.update(filters)

        cursor = self.collection.find(query).skip(skip).limit(limit)
        cursor = cursor.sort("nome_completo", ASCENDING)

        clients: List[Client] = []
        async for doc in cursor:
            doc.pop("_id", None)
            clients.append(Client(**doc))
        return clients

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query: Dict[str, Any] = {}
        if filters:
            query.update(filters)
        return await self.collection.count_documents(query)

    async def add_appointment(
        self,
        client_id: str,
        appointment_id: str,
        last_appointment_at: Optional[datetime] = None,
    ) -> Optional[Client]:
        update_payload: Dict[str, Any] = {
            "$addToSet": {"appointment_ids": appointment_id},
            "$set": {"updated_at": datetime.utcnow()},
        }

        if last_appointment_at is not None:
            update_payload["$set"]["last_appointment_at"] = last_appointment_at

        await self.collection.update_one({"id": client_id}, update_payload)
        return await self.find_by_id(client_id)

    async def create_indexes(self) -> None:
        indexes = [
            ([("cpf", ASCENDING)], {"unique": True, "name": "idx_unique_cpf"}),
            ([("nome_completo", ASCENDING)], {"name": "idx_nome_completo"}),
        ]

        existing_indexes = await self.collection.index_information()
        for keys, options in indexes:
            name = options.get("name")
            if name not in existing_indexes:
                await self.collection.create_index(keys, **options)
