"""MongoDB repository implementation for clients."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.domain.entities.client import Client
from src.domain.repositories.client_repository_interface import (
    ClientRepositoryInterface,
)


class ClientRepository(ClientRepositoryInterface):
    """Persistence layer for client management using MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.clients

    async def create(self, client: Client) -> Client:
        data = self._serialize(client)
        await self.collection.insert_one(data)
        return client

    async def update(self, client: Client) -> Client:
        data = self._serialize(client)
        await self.collection.update_one({"id": data["id"]}, {"$set": data})
        return client

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        document = await self.collection.find_one({"id": client_id})
        if not document:
            return None

        document.pop("_id", None)
        return Client(**document)

    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        document = await self.collection.find_one({"cpf": cpf})
        if not document:
            return None

        document.pop("_id", None)
        return Client(**document)

    async def find_by_filters(
        self, search: Optional[str], skip: int = 0, limit: int = 50
    ) -> List[Client]:
        query: Dict[str, Any] = {}
        or_conditions: List[Dict[str, Any]] = []

        if search:
            trimmed = search.strip()
            if trimmed:
                or_conditions.append({"nome_completo": {"$regex": trimmed, "$options": "i"}})
                or_conditions.append({"email": {"$regex": trimmed, "$options": "i"}})

            digits = re.sub(r"\D", "", trimmed)
            if digits:
                or_conditions.append({"cpf": {"$regex": digits}})
                or_conditions.append({"telefone": {"$regex": digits}})

        if or_conditions:
            query["$or"] = or_conditions

        cursor = (
            self.collection.find(query)
            .skip(skip)
            .limit(limit)
            .sort("nome_completo", ASCENDING)
        )

        clients: List[Client] = []
        async for document in cursor:
            document.pop("_id", None)
            clients.append(Client(**document))

        return clients

    async def count(self, search: Optional[str] = None) -> int:
        query: Dict[str, Any] = {}
        or_conditions: List[Dict[str, Any]] = []

        if search:
            trimmed = search.strip()
            if trimmed:
                or_conditions.append({"nome_completo": {"$regex": trimmed, "$options": "i"}})
                or_conditions.append({"email": {"$regex": trimmed, "$options": "i"}})

            digits = re.sub(r"\D", "", trimmed)
            if digits:
                or_conditions.append({"cpf": {"$regex": digits}})
                or_conditions.append({"telefone": {"$regex": digits}})

        if or_conditions:
            query["$or"] = or_conditions

        return int(await self.collection.count_documents(query))

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("cpf", unique=True)
        await self.collection.create_index("nome_completo", ASCENDING)
        await self.collection.create_index("created_at", DESCENDING)

    def _serialize(self, client: Client) -> Dict[str, Any]:
        data = client.model_dump()
        data["id"] = str(data["id"])

        history = data.get("appointment_history") or []
        if history:
            serialized_history = []
            for entry in history:
                serialized_entry = dict(entry)
                if "appointment_id" in serialized_entry:
                    serialized_entry["appointment_id"] = str(serialized_entry["appointment_id"])
                serialized_history.append(serialized_entry)
            data["appointment_history"] = serialized_history

        return data
