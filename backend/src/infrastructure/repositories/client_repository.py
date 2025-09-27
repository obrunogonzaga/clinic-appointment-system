"""MongoDB implementation for client repository."""

import re
from typing import List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.domain.entities.client import Client, ClientAppointmentHistoryEntry
from src.domain.repositories.client_repository_interface import (
    ClientRepositoryInterface,
)


class ClientRepository(ClientRepositoryInterface):
    """Persistência de clientes usando MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database
        self.collection = database.clients

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("cpf", unique=True)
        await self.collection.create_index([("nome", ASCENDING)])
        await self.collection.create_index(
            [("ultimo_agendamento_em", DESCENDING)], name="idx_last_appointment"
        )

    async def create(self, client: Client) -> Client:
        data = self._to_document(client)
        await self.collection.insert_one(data)
        return client

    async def update(self, client: Client) -> Client:
        data = self._to_document(client)
        await self.collection.update_one({"id": data["id"]}, {"$set": data})
        return client

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        doc = await self.collection.find_one({"id": client_id})
        if not doc:
            return None
        return self._from_document(doc)

    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        doc = await self.collection.find_one({"cpf": cpf})
        if not doc:
            return None
        return self._from_document(doc)

    async def list_clients(
        self, search: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Client], int]:
        query: dict = {}
        if search:
            text = search.strip()
            digits = re.sub(r"\D", "", text)
            or_filters = []
            if text:
                or_filters.append({"nome": {"$regex": re.escape(text), "$options": "i"}})
            if digits:
                or_filters.append({"cpf": {"$regex": digits}})
            if or_filters:
                query = {"$or": or_filters}

        cursor = (
            self.collection.find(query)
            .sort("ultimo_agendamento_em", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        items: List[Client] = []
        async for doc in cursor:
            items.append(self._from_document(doc))

        total = await self.collection.count_documents(query)
        return items, total

    async def append_history_entry(
        self, client_id: str, entry: ClientAppointmentHistoryEntry
    ) -> None:
        await self.collection.update_one(
            {"id": client_id, "historico_agendamentos.appointment_id": {"$ne": entry.appointment_id}},
            {
                "$push": {
                    "historico_agendamentos": entry.model_dump(),
                },
                "$inc": {"total_agendamentos": 1},
            },
        )

    def _to_document(self, client: Client) -> dict:
        data = client.model_dump()
        data["id"] = str(data["id"])
        data["historico_agendamentos"] = [
            entry.model_dump() for entry in client.historico_agendamentos
        ]
        return data

    def _from_document(self, doc: dict) -> Client:
        document = dict(doc)
        document.pop("_id", None)
        history = [
            ClientAppointmentHistoryEntry(**entry)
            for entry in document.get("historico_agendamentos", [])
        ]
        document["historico_agendamentos"] = history
        return Client(**document)
