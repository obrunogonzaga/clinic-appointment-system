"""
MongoDB implementation of AppointmentRepository.
"""

import asyncio
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.domain.entities.appointment import Appointment
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)


_PENDING_STATUS_VALUES: Tuple[str, ...] = (
    "Pendente",
    "Autorização",
    "Autorizacao",
    "Cadastrar",
    "Agendado",
    "Alterar",
    "Recoleta",
)
_PENDING_STATUS_VALUES_LOWER: Tuple[str, ...] = tuple(
    status.lower() for status in _PENDING_STATUS_VALUES
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

        # Check for special "unscheduled" marker
        if data_inicio == "unscheduled" and data_fim == "unscheduled":
            # Filter for appointments without a date
            query["data_agendamento"] = None
        elif data_inicio or data_fim:
            date_filter = {}
            if data_inicio:
                date_filter["$gte"] = data_inicio
            if data_fim:
                date_filter["$lt"] = data_fim
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

    async def count_by_tag(self, tag_id: str) -> int:
        """Count appointments that reference a given tag identifier."""
        return await self.collection.count_documents({"tags.id": tag_id})

    async def update_tag_references(
        self, tag_id: str, name: str, color: str
    ) -> int:
        """Propagate tag updates to embedded tag summaries."""
        try:
            result = await self.collection.update_many(
                {"tags.id": tag_id},
                {
                    "$set": {
                        "tags.$[tag].name": name,
                        "tags.$[tag].color": color,
                        "updated_at": datetime.utcnow(),
                    }
                },
                array_filters=[{"tag.id": tag_id}],
            )
            return result.modified_count
        except NotImplementedError as error:  # mongomock doesn't support array filters
            if "array filters" not in str(error).lower():
                raise

            modified = 0
            cursor = self.collection.find({"tags.id": tag_id})
            async for document in cursor:
                tags = document.get("tags", [])
                updated = False
                for tag in tags:
                    if tag.get("id") == tag_id:
                        tag["name"] = name
                        tag["color"] = color
                        updated = True

                if updated:
                    await self.collection.update_one(
                        {"id": document["id"]},
                        {
                            "$set": {
                                "tags": tags,
                                "updated_at": datetime.utcnow(),
                            }
                        },
                    )
                    modified += 1

            return modified

    async def find_duplicates(
        self, appointments: List[Appointment]
    ) -> List[str]:
        """
        Find duplicate appointments based on key fields.

        An appointment is considered duplicate if another appointment exists with:
        - Same patient name
        - Same appointment date
        - Same appointment time
        - Same unit name

        Args:
            appointments: List of appointments to check for duplicates

        Returns:
            List[str]: List of appointment IDs that are duplicates
        """
        if not appointments:
            return []

        duplicate_ids = []

        for appointment in appointments:
            # Only run duplicate checks when date and time are provided
            if not (appointment.data_agendamento and appointment.hora_agendamento):
                continue

            query = {
                "nome_paciente": appointment.nome_paciente,
                "data_agendamento": appointment.data_agendamento,
                "hora_agendamento": appointment.hora_agendamento,
                "nome_unidade": appointment.nome_unidade,
            }

            existing = await self.collection.find_one(query)
            if existing:
                duplicate_ids.append(str(appointment.id))

        return duplicate_ids

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

    async def get_appointment_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, any]:
        """
        Get appointment statistics for dashboard.

        Returns:
            Dictionary with appointment statistics
        """
        match_stage: Dict[str, Any] = {}
        date_conditions: Dict[str, Any] = {}
        if start_date is not None:
            date_conditions["$gte"] = start_date
        if end_date is not None:
            date_conditions["$lt"] = end_date
        if date_conditions:
            match_stage["data_agendamento"] = {**date_conditions}

        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
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
        )

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

    async def get_admin_dashboard_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Aggregate analytics required by the administrative dashboard."""

        if start_date >= end_date:
            raise ValueError("start_date must be earlier than end_date")

        date_filter: Dict[str, Any] = {"$ne": None}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lt"] = end_date

        base_match = {"data_agendamento": date_filter}

        status_pipeline = [
            {"$match": deepcopy(base_match)},
            {
                "$group": {
                    "_id": {"$ifNull": ["$status", "Indefinido"]},
                    "count": {"$sum": 1},
                }
            },
        ]

        trend_pipeline = [
            {"$match": deepcopy(base_match)},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$data_agendamento",
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        top_units_pipeline = [
            {"$match": deepcopy(base_match)},
            {
                "$group": {
                    "_id": {
                        "unit": {"$ifNull": ["$nome_unidade", "Unidade não informada"]},
                        "brand": {"$ifNull": ["$nome_marca", "Marca não informada"]},
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]

        assignments_pipeline = [
            {"$match": deepcopy(base_match)},
            {
                "$group": {
                    "_id": None,
                    "drivers": {"$addToSet": "$driver_id"},
                    "collectors": {"$addToSet": "$collector_id"},
                    "cars": {"$addToSet": "$car_id"},
                }
            },
        ]

        today_utc = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        pending_future_pipeline = [
            {
                "$match": {
                    "$and": [
                        {
                            "$expr": {
                                "$in": [
                                    {
                                        "$toLower": {
                                            "$ifNull": ["$status", ""]
                                        }
                                    },
                                    list(_PENDING_STATUS_VALUES_LOWER),
                                ]
                            }
                        },
                        {
                            "$or": [
                                {"data_agendamento": None},
                                {"data_agendamento": {"$exists": False}},
                                {"data_agendamento": {"$gte": today_utc}},
                            ]
                        },
                    ]
                }
            },
            {"$count": "count"},
        ]

        (
            status_result,
            trend_result,
            top_units_result,
            assignments_result,
            pending_future_result,
        ) = await asyncio.gather(
            self.collection.aggregate(status_pipeline).to_list(None),
            self.collection.aggregate(trend_pipeline).to_list(None),
            self.collection.aggregate(top_units_pipeline).to_list(None),
            self.collection.aggregate(assignments_pipeline).to_list(1),
            self.collection.aggregate(pending_future_pipeline).to_list(1),
        )

        status_counts: Dict[str, int] = {
            item["_id"]: int(item["count"]) for item in status_result
        }

        trend_points = [
            {"date": item["_id"], "value": int(item["count"])}
            for item in trend_result
        ]

        top_units = [
            {
                "unit": item["_id"]["unit"],
                "brand": item["_id"]["brand"],
                "count": int(item["count"]),
            }
            for item in top_units_result
        ]

        assignments_summary = {
            "drivers": 0,
            "collectors": 0,
            "cars": 0,
        }
        if assignments_result:
            assignment_record = assignments_result[0]
            assignments_summary = {
                "drivers": len(
                    [value for value in assignment_record.get("drivers", []) if value]
                ),
                "collectors": len(
                    [value for value in assignment_record.get("collectors", []) if value]
                ),
                "cars": len(
                    [value for value in assignment_record.get("cars", []) if value]
                ),
            }

        pending_future_total = (
            int(pending_future_result[0]["count"])
            if pending_future_result
            else 0
        )

        return {
            "status_counts": status_counts,
            "trend": trend_points,
            "top_units": top_units,
            "resource_assignments": assignments_summary,
            "total": sum(status_counts.values()),
            "pending_future_total": pending_future_total,
        }
