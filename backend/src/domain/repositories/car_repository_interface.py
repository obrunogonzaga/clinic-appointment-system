"""
Car repository interface defining the contract for data access.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.domain.entities.car import Car


class CarRepositoryInterface(ABC):
    """
    Interface for car repository operations.

    This interface defines the contract that must be implemented
    by concrete repository classes.
    """

    @abstractmethod
    async def create(self, car: Car) -> Car:
        """
        Create a new car.

        Args:
            car: Car entity to create

        Returns:
            Created car with generated ID
        """
        pass

    @abstractmethod
    async def find_by_id(self, car_id: str) -> Optional[Car]:
        """
        Find a car by ID.

        Args:
            car_id: Unique identifier of the car

        Returns:
            Car if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_nome(self, nome: str) -> Optional[Car]:
        """
        Find a car by name.

        Args:
            nome: Car name to search for

        Returns:
            Car if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_placa(self, placa: str) -> Optional[Car]:
        """
        Find a car by license plate.

        Args:
            placa: License plate to search for

        Returns:
            Car if found, None otherwise
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count cars with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of cars matching the criteria
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, car_id: str) -> bool:
        """
        Delete a car.

        Args:
            car_id: ID of the car to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_active_cars(self) -> List[Car]:
        """
        Get all active cars.

        Returns:
            List of cars with status "Ativo"
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_distinct_values(self, field: str) -> List[str]:
        """
        Get distinct values for a specific field.

        Useful for populating filter dropdowns.

        Args:
            field: Field name to get distinct values for

        Returns:
            List of unique values for the field
        """
        pass

    @abstractmethod
    async def get_car_stats(self) -> Dict[str, Any]:
        """
        Get car statistics for dashboard.

        Returns:
            Dictionary with car statistics
        """
        pass

    @abstractmethod
    async def find_or_create_from_string(self, car_string: str) -> Car:
        """
        Find a car by the string format or create if not found.
        
        Used during Excel import to automatically register cars.

        Args:
            car_string: String like "CENTER 3 CARRO 1 - UND84"

        Returns:
            Car entity (existing or newly created)
        """
        pass