"""
MongoDB implementation of AppointmentRepository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.domain.entities.appointment import Appointment
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)


class AppointmentRepository(AppointmentRepositoryInterface):
    """
    MongoDB implementation of appointment repository.

    This repository handles all database operations for appointments
    using MongoDB as the storage backend.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize the repository with a database connection.

        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection = database.appointments

    async def create(self, appointment: Appointment) -> Appointment:
        """
        Create a new appointment in the database.

        Args:
            appointment: Appointment entity to create

        Returns:
            Created appointment with generated ID
        """
        # Convert to dict for MongoDB
        data = appointment.model_dump()

        # Convert UUID to string for MongoDB storage
        data["id"] = str(data["id"])

        # Insert into database
        await self.collection.insert_one(data)

        # MongoDB generates _id, but we use our own UUID
        return appointment

    async def create_many(
        self, appointments: List[Appointment]
    ) -> List[Appointment]:
        """
        Create multiple appointments in bulk.

        Args:
            appointments: List of appointment entities to create

        Returns:
            List of created appointments
        """
        if not appointments:
            return []

        # Convert all appointments to dict format
        docs = []
        for appointment in appointments:
            data = appointment.model_dump()
            data["id"] = str(data["id"])
            docs.append(data)

        # Bulk insert
        await self.collection.insert_many(docs)

        return appointments

    async def find_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """
        Find an appointment by ID.

        Args:
            appointment_id: Unique identifier of the appointment

        Returns:
            Appointment if found, None otherwise
        """
        doc = await self.collection.find_one({"id": appointment_id})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Appointment(**doc)

    async def find_all(
        self,
        filters: Optional[Dict[str, any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Appointment]:
        """
        Find all appointments with optional filters.

        Args:
            filters: Optional dictionary of filters to apply
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of appointments matching the criteria
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
        appointments = []
        async for doc in cursor:
            doc.pop("_id", None)
            appointments.append(Appointment(**doc))

        return appointments

    async def find_by_filters(
        self,
        nome_unidade: Optional[str] = None,
        nome_marca: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        status: Optional[str] = None,
        driver_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Appointment]:
        """
        Find appointments by specific filters.

        Args:
            nome_unidade: Filter by unit name
            nome_marca: Filter by brand name
            data_inicio: Filter by start date
            data_fim: Filter by end date
            status: Filter by appointment status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of appointments matching the filters
        """
        # Build MongoDB query
        query = {}

        if nome_unidade:
            query["nome_unidade"] = {"$regex": nome_unidade, "$options": "i"}

        if nome_marca:
            query["nome_marca"] = {"$regex": nome_marca, "$options": "i"}

        if data_inicio or data_fim:
            date_filter = {}
            if data_inicio:
                date_filter["$gte"] = data_inicio
            if data_fim:
                date_filter["$lte"] = data_fim
            query["data_agendamento"] = date_filter

        if status:
            query["status"] = status

        if driver_id is not None:
            query["driver_id"] = driver_id

        # Execute query
        cursor = self.collection.find(query).skip(skip).limit(limit)
        cursor = cursor.sort("data_agendamento", ASCENDING)

        # Convert to entities
        appointments = []
        async for doc in cursor:
            doc.pop("_id", None)
            appointments.append(Appointment(**doc))

        return appointments

    async def count(self, filters: Optional[Dict[str, any]] = None) -> int:
        """
        Count appointments with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of appointments matching the criteria
        """
        query = {}
        if filters:
            query.update(filters)

        return await self.collection.count_documents(query)

    async def update(
        self, appointment_id: str, update_data: Dict[str, any]
    ) -> Optional[Appointment]:
        """
        Update an appointment.

        Args:
            appointment_id: ID of the appointment to update
            update_data: Dictionary with fields to update

        Returns:
            Updated appointment if found, None otherwise
        """
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update document
        result = await self.collection.update_one(
            {"id": appointment_id}, {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        # Return updated appointment
        return await self.find_by_id(appointment_id)

    async def delete(self, appointment_id: str) -> bool:
        """
        Delete an appointment.

        Args:
            appointment_id: ID of the appointment to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        result = await self.collection.delete_one({"id": appointment_id})
        return result.deleted_count > 0

    async def delete_many(self, filters: Dict[str, any]) -> int:
        """
        Delete multiple appointments matching filters.

        Args:
            filters: Dictionary of filters to identify appointments to delete

        Returns:
            Number of appointments deleted
        """
        result = await self.collection.delete_many(filters)
        return result.deleted_count

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
        filtered_values = [
            v for v in values if v is not None and str(v).strip()
        ]
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
                ([("nome_unidade", ASCENDING)], "idx_nome_unidade"),
                ([("nome_marca", ASCENDING)], "idx_nome_marca"),
                ([("data_agendamento", ASCENDING)], "idx_data_agendamento"),
                ([("status", ASCENDING)], "idx_status"),
                ([("created_at", DESCENDING)], "idx_created_at"),
                # Compound indexes for common filter combinations
                (
                    [("nome_unidade", ASCENDING), ("nome_marca", ASCENDING)],
                    "idx_unidade_marca",
                ),
                (
                    [("data_agendamento", ASCENDING), ("status", ASCENDING)],
                    "idx_data_status",
                ),
                (
                    [
                        ("nome_unidade", ASCENDING),
                        ("data_agendamento", ASCENDING),
                    ],
                    "idx_unidade_data",
                ),
            ]

            for index_spec, index_name in indexes:
                if index_name not in existing_indexes:
                    await self.collection.create_index(
                        index_spec, name=index_name
                    )

        except Exception as e:
            # Log error but don't fail startup
            print(f"Warning: Could not create indexes: {e}")

    async def get_appointment_stats(self) -> Dict[str, any]:
        """
        Get appointment statistics for dashboard.

        Returns:
            Dictionary with appointment statistics
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_appointments": {"$sum": 1},
                    "confirmed_appointments": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "Confirmado"]}, 1, 0]
                        }
                    },
                    "cancelled_appointments": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "Cancelado"]}, 1, 0]
                        }
                    },
                    "units": {"$addToSet": "$nome_unidade"},
                    "brands": {"$addToSet": "$nome_marca"},
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_appointments": 0,
                "confirmed_appointments": 0,
                "cancelled_appointments": 0,
                "total_units": 0,
                "total_brands": 0,
            }

        stats = result[0]
        return {
            "total_appointments": stats["total_appointments"],
            "confirmed_appointments": stats["confirmed_appointments"],
            "cancelled_appointments": stats["cancelled_appointments"],
            "total_units": len(stats["units"]),
            "total_brands": len(stats["brands"]),
        }
