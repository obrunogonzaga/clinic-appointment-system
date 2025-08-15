"""
MongoDB implementation of CollectorRepository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING
from src.domain.entities.collector import Collector
from src.domain.repositories.collector_repository_interface import (
    CollectorRepositoryInterface,
)


class CollectorRepository(CollectorRepositoryInterface):
    """
    MongoDB implementation of collector repository.

    This repository handles all database operations for collectors
    using MongoDB as the storage backend.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize the repository with a database connection.

        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection = database.collectors

    async def create(self, collector: Collector) -> Collector:
        """
        Create a new collector in the database.

        Args:
            collector: Collector entity to create

        Returns:
            Created collector with generated ID
        """
        # Convert to dict for MongoDB
        data = collector.model_dump()

        # Convert UUID to string for MongoDB storage
        data["id"] = str(data["id"])

        # Insert into database
        await self.collection.insert_one(data)

        # MongoDB generates _id, but we use our own UUID
        return collector

    async def find_by_id(self, collector_id: str) -> Optional[Collector]:
        """
        Find a collector by ID.

        Args:
            collector_id: Unique identifier of the collector

        Returns:
            Collector if found, None otherwise
        """
        doc = await self.collection.find_one({"id": collector_id})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Collector(**doc)

    async def find_by_cpf(self, cpf: str) -> Optional[Collector]:
        """
        Find a collector by CPF number.

        Args:
            cpf: CPF number to search for

        Returns:
            Collector if found, None otherwise
        """
        doc = await self.collection.find_one({"cpf": cpf})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Collector(**doc)

    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Collector]:
        """
        Find all collectors with optional filters.

        Args:
            filters: Optional dictionary of filters to apply
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of collectors matching the criteria
        """
        query = filters or {}

        cursor = self.collection.find(query)
        cursor = cursor.skip(skip).limit(limit)
        cursor = cursor.sort("nome_completo", ASCENDING)

        collectors = []
        async for doc in cursor:
            doc.pop("_id", None)
            collectors.append(Collector(**doc))

        return collectors

    async def find_by_filters(
        self,
        nome_completo: Optional[str] = None,
        cpf: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Collector]:
        """
        Find collectors by specific filters.

        Args:
            nome_completo: Filter by collector name (partial match)
            cpf: Filter by CPF number (exact match)
            telefone: Filter by phone number (exact match)
            email: Filter by email (exact match)
            status: Filter by collector status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of collectors matching the filters
        """
        query = {}

        # Build query based on provided filters
        if nome_completo:
            query["nome_completo"] = {"$regex": nome_completo, "$options": "i"}

        if cpf:
            query["cpf"] = cpf

        if telefone:
            query["telefone"] = telefone

        if email:
            query["email"] = email

        if status:
            query["status"] = status

        cursor = self.collection.find(query)
        cursor = cursor.skip(skip).limit(limit)
        cursor = cursor.sort("nome_completo", ASCENDING)

        collectors = []
        async for doc in cursor:
            doc.pop("_id", None)
            collectors.append(Collector(**doc))

        return collectors

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count collectors with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of collectors matching the criteria
        """
        query = filters or {}

        return await self.collection.count_documents(query)

    async def update(
        self, collector_id: str, update_data: Dict[str, Any]
    ) -> Optional[Collector]:
        """
        Update a collector.

        Args:
            collector_id: ID of the collector to update
            update_data: Dictionary with fields to update

        Returns:
            Updated collector if found, None otherwise
        """
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update document
        result = await self.collection.update_one(
            {"id": collector_id}, {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        # Return updated collector
        return await self.find_by_id(collector_id)

    async def delete(self, collector_id: str) -> bool:
        """
        Delete a collector.

        Args:
            collector_id: ID of the collector to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        result = await self.collection.delete_one({"id": collector_id})
        return result.deleted_count > 0

    async def get_active_collectors(self) -> List[Collector]:
        """
        Get all active collectors.

        Returns:
            List of collectors with status "Ativo"
        """
        cursor = self.collection.find({"status": "Ativo"})
        cursor = cursor.sort("nome_completo", ASCENDING)

        collectors = []
        async for doc in cursor:
            doc.pop("_id", None)
            collectors.append(Collector(**doc))

        return collectors

    async def exists_by_cpf(
        self, cpf: str, exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if a collector with the given CPF already exists.

        Args:
            cpf: CPF number to check
            exclude_id: Optional collector ID to exclude from check (for updates)

        Returns:
            True if CPF exists, False otherwise
        """
        query = {"cpf": cpf}

        if exclude_id:
            query["id"] = {"$ne": exclude_id}

        doc = await self.collection.find_one(query, {"_id": 1})
        return doc is not None

    async def get_distinct_values(self, field: str) -> List[str]:
        """
        Get distinct values for a specific field.

        Args:
            field: Field name to get distinct values for

        Returns:
            List of unique values for the field
        """
        values = await self.collection.distinct(field)

        # Filter out None values and convert to strings
        return [str(v) for v in values if v is not None]

    async def get_collector_stats(self) -> Dict[str, Any]:
        """
        Get collector statistics for dashboard.

        Returns:
            Dictionary with collector statistics
        """
        pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]

        stats = {
            "total_collectors": 0,
            "active_collectors": 0,
            "inactive_collectors": 0,
            "suspended_collectors": 0,
        }

        async for result in self.collection.aggregate(pipeline):
            status = result["_id"] or "Ativo"
            count = result["count"]

            stats["total_collectors"] += count

            if status == "Ativo":
                stats["active_collectors"] = count
            elif status == "Inativo":
                stats["inactive_collectors"] = count
            elif status == "Suspenso":
                stats["suspended_collectors"] = count

        return stats

    async def create_indexes(self) -> None:
        """
        Create database indexes for optimal query performance.
        """
        # Unique index on CPF
        await self.collection.create_index("cpf", unique=True)

        # Index on ID for fast lookups
        await self.collection.create_index("id", unique=True)

        # Index on status for filtering
        await self.collection.create_index("status")

        # Text index on name for search
        await self.collection.create_index([("nome_completo", "text")])

        # Compound index for filtering by multiple fields
        await self.collection.create_index(
            [("status", ASCENDING), ("nome_completo", ASCENDING)]
        )
