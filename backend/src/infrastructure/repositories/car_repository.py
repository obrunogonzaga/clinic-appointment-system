"""
MongoDB implementation of CarRepository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.domain.entities.car import Car
from src.domain.repositories.car_repository_interface import (
    CarRepositoryInterface,
)


class CarRepository(CarRepositoryInterface):
    """
    MongoDB implementation of car repository.

    This repository handles all database operations for cars
    using MongoDB as the storage backend.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize the repository with a database connection.

        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection = database.cars

    async def create(self, car: Car) -> Car:
        """
        Create a new car in the database.

        Args:
            car: Car entity to create

        Returns:
            Created car with generated ID
        """
        # Convert to dict for MongoDB
        data = car.model_dump()

        # Convert UUID to string for MongoDB storage
        data["id"] = str(data["id"])

        # Insert into database
        await self.collection.insert_one(data)

        # MongoDB generates _id, but we use our own UUID
        return car

    async def find_by_id(self, car_id: str) -> Optional[Car]:
        """
        Find a car by ID.

        Args:
            car_id: Unique identifier of the car

        Returns:
            Car if found, None otherwise
        """
        doc = await self.collection.find_one({"id": car_id})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Car(**doc)

    async def find_by_nome(self, nome: str) -> Optional[Car]:
        """
        Find a car by name.

        Args:
            nome: Car name to search for

        Returns:
            Car if found, None otherwise
        """
        doc = await self.collection.find_one({"nome": nome})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Car(**doc)

    async def find_by_placa(self, placa: str) -> Optional[Car]:
        """
        Find a car by license plate.

        Args:
            placa: License plate to search for

        Returns:
            Car if found, None otherwise
        """
        doc = await self.collection.find_one({"placa": placa})

        if doc is None:
            return None

        # Remove MongoDB's _id field
        doc.pop("_id", None)

        return Car(**doc)

    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Car]:
        """
        Find all cars with optional filters.

        Args:
            filters: Optional dictionary of filters to apply
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of cars matching the criteria
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
        cars = []
        async for doc in cursor:
            doc.pop("_id", None)
            cars.append(Car(**doc))

        return cars

    async def find_by_filters(
        self,
        nome: Optional[str] = None,
        unidade: Optional[str] = None,
        placa: Optional[str] = None,
        modelo: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Car]:
        """
        Find cars by specific filters.

        Args:
            nome: Filter by car name (partial match)
            unidade: Filter by unit (partial match)
            placa: Filter by license plate (exact match)
            modelo: Filter by model (partial match)
            status: Filter by car status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of cars matching the filters
        """
        # Build MongoDB query
        query = {}

        if nome:
            query["nome"] = {"$regex": nome, "$options": "i"}

        if unidade:
            query["unidade"] = {"$regex": unidade, "$options": "i"}

        if placa:
            query["placa"] = placa

        if modelo:
            query["modelo"] = {"$regex": modelo, "$options": "i"}

        if status:
            query["status"] = status

        # Execute query
        cursor = self.collection.find(query).skip(skip).limit(limit)
        cursor = cursor.sort("nome", ASCENDING)

        # Convert to entities
        cars = []
        async for doc in cursor:
            doc.pop("_id", None)
            cars.append(Car(**doc))

        return cars

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count cars with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of cars matching the criteria
        """
        query = {}
        if filters:
            query.update(filters)

        return await self.collection.count_documents(query)

    async def update(
        self, car_id: str, update_data: Dict[str, Any]
    ) -> Optional[Car]:
        """
        Update a car.

        Args:
            car_id: ID of the car to update
            update_data: Dictionary with fields to update

        Returns:
            Updated car if found, None otherwise
        """
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update document
        result = await self.collection.update_one(
            {"id": car_id}, {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        # Return updated car
        return await self.find_by_id(car_id)

    async def delete(self, car_id: str) -> bool:
        """
        Delete a car.

        Args:
            car_id: ID of the car to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        result = await self.collection.delete_one({"id": car_id})
        return result.deleted_count > 0

    async def get_active_cars(self) -> List[Car]:
        """
        Get all active cars.

        Returns:
            List of cars with status "Ativo"
        """
        cursor = self.collection.find({"status": "Ativo"})
        cursor = cursor.sort("nome", ASCENDING)

        cars = []
        async for doc in cursor:
            doc.pop("_id", None)
            cars.append(Car(**doc))

        return cars

    async def exists_by_nome(
        self, nome: str, exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if a car with the given name already exists.

        Args:
            nome: Car name to check
            exclude_id: Optional car ID to exclude from check (for updates)

        Returns:
            True if name exists, False otherwise
        """
        query = {"nome": nome}

        if exclude_id:
            query["id"] = {"$ne": exclude_id}

        count = await self.collection.count_documents(query)
        return count > 0

    async def exists_by_placa(
        self, placa: str, exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if a car with the given license plate already exists.

        Args:
            placa: License plate to check
            exclude_id: Optional car ID to exclude from check (for updates)

        Returns:
            True if license plate exists, False otherwise
        """
        query = {"placa": placa}

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
        filtered_values = [
            v for v in values if v is not None and str(v).strip()
        ]
        return sorted(filtered_values)

    async def get_car_stats(self) -> Dict[str, Any]:
        """
        Get car statistics for dashboard.

        Returns:
            Dictionary with car statistics
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_cars": {"$sum": 1},
                    "active_cars": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "Ativo"]}, 1, 0]
                        }
                    },
                    "inactive_cars": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "Inativo"]}, 1, 0]
                        }
                    },
                    "maintenance_cars": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "Manutenção"]}, 1, 0]
                        }
                    },
                    "sold_cars": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "Vendido"]}, 1, 0]
                        }
                    },
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_cars": 0,
                "active_cars": 0,
                "inactive_cars": 0,
                "maintenance_cars": 0,
                "sold_cars": 0,
            }

        stats = result[0]
        return {
            "total_cars": stats["total_cars"],
            "active_cars": stats["active_cars"],
            "inactive_cars": stats["inactive_cars"],
            "maintenance_cars": stats["maintenance_cars"],
            "sold_cars": stats["sold_cars"],
        }

    async def find_or_create_from_string(self, car_string: str) -> Car:
        """
        Find a car by the string format or create if not found.

        Used during Excel import to automatically register cars.

        Args:
            car_string: String like "CENTER 3 CARRO 1 - UND84"

        Returns:
            Car entity (existing or newly created)
        """
        # Extract car info from string
        car_name, unit = Car.extract_car_info_from_string(car_string)

        # Try to find existing car by name and unit
        query = {"nome": car_name, "unidade": unit}
        doc = await self.collection.find_one(query)

        if doc:
            # Car exists, return it
            doc.pop("_id", None)
            return Car(**doc)

        # Car doesn't exist, create new one
        new_car = Car(nome=car_name, unidade=unit, status="Ativo")

        # Save to database
        await self.create(new_car)

        return new_car

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
                ([("nome", ASCENDING)], "idx_nome"),
                ([("unidade", ASCENDING)], "idx_unidade"),
                ([("placa", ASCENDING)], "idx_placa"),
                ([("modelo", ASCENDING)], "idx_modelo"),
                ([("status", ASCENDING)], "idx_status"),
                ([("created_at", DESCENDING)], "idx_created_at"),
                # Compound indexes for common filter combinations
                (
                    [("status", ASCENDING), ("nome", ASCENDING)],
                    "idx_status_nome",
                ),
                (
                    [("unidade", ASCENDING), ("nome", ASCENDING)],
                    "idx_unidade_nome",
                ),
                (
                    [("nome", ASCENDING), ("unidade", ASCENDING)],
                    "idx_nome_unidade",
                ),
            ]

            for index_spec, index_name in indexes:
                if index_name not in existing_indexes:
                    await self.collection.create_index(
                        index_spec, name=index_name
                    )

            # Create unique compound index for nome + unidade
            unique_indexes = [
                (
                    [("nome", ASCENDING), ("unidade", ASCENDING)],
                    "idx_nome_unidade_unique",
                    True,
                ),
            ]

            for index_spec, index_name, unique in unique_indexes:
                if index_name not in existing_indexes:
                    await self.collection.create_index(
                        index_spec, name=index_name, unique=unique
                    )

        except Exception as e:
            # Log error but don't fail startup
            print(f"Warning: Could not create car indexes: {e}")
