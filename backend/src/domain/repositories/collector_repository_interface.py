"""
Collector repository interface defining the contract for data access.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.domain.entities.collector import Collector


class CollectorRepositoryInterface(ABC):
    """
    Interface for collector repository operations.

    This interface defines the contract that must be implemented
    by concrete repository classes.
    """

    @abstractmethod
    async def create(self, collector: Collector) -> Collector:
        """
        Create a new collector.

        Args:
            collector: Collector entity to create

        Returns:
            Created collector with generated ID
        """
        pass

    @abstractmethod
    async def find_by_id(self, collector_id: str) -> Optional[Collector]:
        """
        Find a collector by ID.

        Args:
            collector_id: Unique identifier of the collector

        Returns:
            Collector if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_cpf(self, cpf: str) -> Optional[Collector]:
        """
        Find a collector by CPF number.

        Args:
            cpf: CPF number to search for

        Returns:
            Collector if found, None otherwise
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count collectors with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of collectors matching the criteria
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(self, collector_id: str) -> bool:
        """
        Delete a collector.

        Args:
            collector_id: ID of the collector to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_active_collectors(self) -> List[Collector]:
        """
        Get all active collectors.

        Returns:
            List of collectors with status "Ativo"
        """
        pass

    @abstractmethod
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
    async def get_collector_stats(self) -> Dict[str, Any]:
        """
        Get collector statistics for dashboard.

        Returns:
            Dictionary with collector statistics
        """
        pass
