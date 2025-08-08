"""
MongoDB implementation of DriverRepository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.domain.entities.driver import Driver
from src.domain.repositories.driver_repository_interface import (
    DriverRepositoryInterface,
)


class DriverRepository(DriverRepositoryInterface):
    """
    MongoDB implementation of driver repository.

    This repository handles all database operations for drivers
    using MongoDB as the storage backend.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize the repository with a database connection.

        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection = database.drivers

    async def create(self, driver: Driver) -> Driver:
        """
        Create a new driver in the database.

        Args:
            driver: Driver entity to create

        Returns:
            Created driver with generated ID
        """
        # Convert to dict for MongoDB
        data = driver.model_dump()

        # Convert UUID to string for MongoDB storage
        data["id"] = str(data["id"])

        # Insert into database
        await self.collection.insert_one(data)

        # MongoDB generates _id, but we use our own UUID
        return driver

    async def find_by_id(self, driver_id: str) -> Optional[Driver]:
        """
        Find a driver by ID.

        Args:
            driver_id: Unique identifier of the driver

        Returns:
            Driver if found, None otherwise
        """
        doc = await self.collection.find_one({"id": driver_id})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Driver(**doc)

    async def find_by_cnh(self, cnh: str) -> Optional[Driver]:
        """
        Find a driver by CNH number.

        Args:
            cnh: CNH number to search for

        Returns:
            Driver if found, None otherwise
        """
        doc = await self.collection.find_one({"cnh": cnh})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Driver(**doc)

    async def find_all(
        self, filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100
    ) -> List[Driver]:
        """
        Find all drivers with optional filters.

        Args:
            filters: Optional dictionary of filters to apply
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of drivers matching the criteria
        """
        # Build MongoDB query
        query = {}
        if filters:
            query.update(filters)

        # Execute query with pagination
        cursor = self.collection.find(query).skip(skip).limit(limit)

        # Sort by creation date (newest first)
        cursor = cursor.sort("created_at", DESCENDING)

        # Convert documents to entities
        drivers = []
        async for doc in cursor:
            doc.pop("_id", None)
            drivers.append(Driver(**doc))

        return drivers

    async def find_by_filters(
        self,
        nome_completo: Optional[str] = None,
        cnh: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Driver]:
        """
        Find drivers by specific filters.

        Args:
            nome_completo: Filter by driver name (partial match)
            cnh: Filter by CNH number (exact match)
            telefone: Filter by phone number (exact match)
            email: Filter by email (exact match)
            status: Filter by driver status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of drivers matching the filters
        """
        # Build MongoDB query
        query = {}

        if nome_completo:
            query["nome_completo"] = {"$regex": nome_completo, "$options": "i"}

        if cnh:
            query["cnh"] = cnh

        if telefone:
            query["telefone"] = telefone

        if email:
            query["email"] = {"$regex": email, "$options": "i"}

        if status:
            query["status"] = status

        # Execute query
        cursor = self.collection.find(query).skip(skip).limit(limit)
        cursor = cursor.sort("nome_completo", ASCENDING)

        # Convert to entities
        drivers = []
        async for doc in cursor:
            doc.pop("_id", None)
            drivers.append(Driver(**doc))

        return drivers

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count drivers with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of drivers matching the criteria
        """
        query = {}
        if filters:
            query.update(filters)

        return await self.collection.count_documents(query)

    async def update(
        self, driver_id: str, update_data: Dict[str, Any]
    ) -> Optional[Driver]:
        """
        Update a driver.

        Args:
            driver_id: ID of the driver to update
            update_data: Dictionary with fields to update

        Returns:
            Updated driver if found, None otherwise
        """
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update document
        result = await self.collection.update_one(
            {"id": driver_id}, {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        # Return updated driver
        return await self.find_by_id(driver_id)

    async def delete(self, driver_id: str) -> bool:
        """
        Delete a driver.

        Args:
            driver_id: ID of the driver to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        result = await self.collection.delete_one({"id": driver_id})
        return result.deleted_count > 0

    async def get_active_drivers(self) -> List[Driver]:
        """
        Get all active drivers.

        Returns:
            List of drivers with status "Ativo"
        """
        cursor = self.collection.find({"status": "Ativo"})
        cursor = cursor.sort("nome_completo", ASCENDING)

        drivers = []
        async for doc in cursor:
            doc.pop("_id", None)
            drivers.append(Driver(**doc))

        return drivers

    async def exists_by_cnh(self, cnh: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if a driver with the given CNH already exists.

        Args:
            cnh: CNH number to check
            exclude_id: Optional driver ID to exclude from check (for updates)

        Returns:
            True if CNH exists, False otherwise
        """
        query = {"cnh": cnh}

        if exclude_id:
            query["id"] = {"$ne": exclude_id}

        count = await self.collection.count_documents(query)
        return count > 0

    async def get_distinct_values(self, field: str) -> List[str]:
        """
        Get distinct values for a specific field.

        Useful for populating filter dropdowns.

        Args:
            field: Field name to get distinct values for

        Returns:
            List of unique values for the field
        """
        # Get distinct values, filtering out None/empty values
        values = await self.collection.distinct(field)

        # Filter out None and empty strings, sort alphabetically
        filtered_values = [v for v in values if v is not None and str(v).strip()]
        return sorted(filtered_values)

    async def create_indexes(self) -> None:
        """
        Create database indexes for better query performance.

        This method should be called during application startup.
        """
        try:
            # Get existing indexes
            existing_indexes = await self.collection.index_information()

            # Define indexes to create with custom names
            indexes = [
                # Single field indexes
                ([("cnh", ASCENDING)], "idx_cnh"),
                ([("nome_completo", ASCENDING)], "idx_nome_completo"),
                ([("telefone", ASCENDING)], "idx_telefone"),
                ([("email", ASCENDING)], "idx_email"),
                ([("status", ASCENDING)], "idx_status"),
                ([("created_at", DESCENDING)], "idx_created_at"),
                # Compound indexes for common filter combinations
                (
                    [("status", ASCENDING), ("nome_completo", ASCENDING)],
                    "idx_status_nome",
                ),
                ([("nome_completo", ASCENDING), ("cnh", ASCENDING)], "idx_nome_cnh"),
            ]

            for index_spec, index_name in indexes:
                if index_name not in existing_indexes:
                    await self.collection.create_index(index_spec, name=index_name)

            # Create unique index for CNH
            unique_indexes = [
                ([("cnh", ASCENDING)], "idx_cnh_unique", True),
            ]

            for index_spec, index_name, unique in unique_indexes:
                if index_name not in existing_indexes:
                    await self.collection.create_index(
                        index_spec, name=index_name, unique=unique
                    )

        except Exception as e:
            # Log error but don't fail startup
            print(f"Warning: Could not create driver indexes: {e}")

    async def get_driver_stats(self) -> Dict[str, Any]:
        """
        Get driver statistics for dashboard.

        Returns:
            Dictionary with driver statistics
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_drivers": {"$sum": 1},
                    "active_drivers": {
                        "$sum": {"$cond": [{"$eq": ["$status", "Ativo"]}, 1, 0]}
                    },
                    "inactive_drivers": {
                        "$sum": {"$cond": [{"$eq": ["$status", "Inativo"]}, 1, 0]}
                    },
                    "suspended_drivers": {
                        "$sum": {"$cond": [{"$eq": ["$status", "Suspenso"]}, 1, 0]}
                    },
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_drivers": 0,
                "active_drivers": 0,
                "inactive_drivers": 0,
                "suspended_drivers": 0,
            }

        stats = result[0]
        return {
            "total_drivers": stats["total_drivers"],
            "active_drivers": stats["active_drivers"],
            "inactive_drivers": stats["inactive_drivers"],
            "suspended_drivers": stats["suspended_drivers"],
        }
