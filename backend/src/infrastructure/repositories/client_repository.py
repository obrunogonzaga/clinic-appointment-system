"""MongoDB implementation of ClientRepository."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

from src.domain.entities.client import Client, ConvenioInfo
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

    async def get_or_create(self, client: Client) -> Tuple[Client, bool]:
        data = client.model_dump()
        data["id"] = str(data["id"])

        result = await self.collection.update_one(
            {"cpf": data["cpf"]},
            {"$setOnInsert": data},
            upsert=True,
        )

        doc = await self.collection.find_one({"cpf": data["cpf"]})
        if not doc:
            raise ValueError("Failed to retrieve client after upsert operation")

        doc.pop("_id", None)
        created = result.upserted_id is not None
        return Client(**doc), created

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
        last_address: Optional[str] = None,
        last_address_normalized: Optional[Dict[str, Optional[str]]] = None,
    ) -> Optional[Client]:
        update_payload: Dict[str, Any] = {
            "$addToSet": {"appointment_ids": appointment_id},
            "$set": {"updated_at": datetime.utcnow()},
        }

        if last_appointment_at is not None:
            update_payload["$set"]["last_appointment_at"] = last_appointment_at

        if last_address is not None:
            update_payload["$set"]["last_address"] = last_address

        if last_address_normalized is not None:
            update_payload["$set"][
                "last_address_normalized"
            ] = last_address_normalized

        await self.collection.update_one({"id": client_id}, update_payload)
        return await self.find_by_id(client_id)

    async def upsert_convenio(
        self,
        client_id: str,
        convenio: ConvenioInfo,
    ) -> Optional[Client]:
        """Add or update a health insurance in the client's convenio history."""

        client = await self.find_by_id(client_id)
        if not client:
            return None

        convenios = client.convenios_historico or []
        convenio_dict = convenio.model_dump()

        # Check if this convenio already exists (by numero_convenio + nome_convenio)
        existing_idx = None
        for idx, existing in enumerate(convenios):
            existing_dict = (
                existing.model_dump()
                if isinstance(existing, ConvenioInfo)
                else existing
            )
            if existing_dict.get("numero_convenio") == convenio_dict.get(
                "numero_convenio"
            ) and existing_dict.get("nome_convenio") == convenio_dict.get(
                "nome_convenio"
            ):
                existing_idx = idx
                break

        if existing_idx is not None:
            # Update existing convenio
            convenios[existing_idx] = convenio
        else:
            # Add new convenio
            convenios.append(convenio)

        # Update in database
        await self.collection.update_one(
            {"id": client_id},
            {
                "$set": {
                    "convenios_historico": [c.model_dump() for c in convenios],
                    "updated_at": datetime.utcnow(),
                }
            },
        )

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
