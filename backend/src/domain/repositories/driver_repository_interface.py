"""
Driver repository interface defining the contract for data access.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.domain.entities.driver import Driver


class DriverRepositoryInterface(ABC):
    """
    Interface for driver repository operations.

    This interface defines the contract that must be implemented
    by concrete repository classes.
    """

    @abstractmethod
    async def create(self, driver: Driver) -> Driver:
        """
        Create a new driver.

        Args:
            driver: Driver entity to create

        Returns:
            Created driver with generated ID
        """
        pass

    @abstractmethod
    async def find_by_id(self, driver_id: str) -> Optional[Driver]:
        """
        Find a driver by ID.

        Args:
            driver_id: Unique identifier of the driver

        Returns:
            Driver if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_cnh(self, cnh: str) -> Optional[Driver]:
        """
        Find a driver by CNH number.

        Args:
            cnh: CNH number to search for

        Returns:
            Driver if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count drivers with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of drivers matching the criteria
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, driver_id: str) -> bool:
        """
        Delete a driver.

        Args:
            driver_id: ID of the driver to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_active_drivers(self) -> List[Driver]:
        """
        Get all active drivers.

        Returns:
            List of drivers with status "Ativo"
        """
        pass

    @abstractmethod
    async def exists_by_cnh(
        self, cnh: str, exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if a driver with the given CNH already exists.

        Args:
            cnh: CNH number to check
            exclude_id: Optional driver ID to exclude from check (for updates)

        Returns:
            True if CNH exists, False otherwise
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
    async def get_driver_stats(self) -> Dict[str, Any]:
        """
        Get driver statistics for dashboard.

        Returns:
            Dictionary with driver statistics
        """
        pass
