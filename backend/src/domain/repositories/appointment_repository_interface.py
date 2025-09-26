"""
Appointment repository interface defining the contract for data access.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.entities.appointment import Appointment


class AppointmentRepositoryInterface(ABC):
    """
    Interface for appointment repository operations.

    This interface defines the contract that must be implemented
    by concrete repository classes.
    """

    @abstractmethod
    async def create(self, appointment: Appointment) -> Appointment:
        """
        Create a new appointment.

        Args:
            appointment: Appointment entity to create

        Returns:
            Created appointment with generated ID
        """
        pass

    @abstractmethod
    async def create_many(
        self, appointments: List[Appointment]
    ) -> List[Appointment]:
        """
        Create multiple appointments in bulk.

        Args:
            appointments: List of appointment entities to create

        Returns:
            List of created appointments with generated IDs
        """
        pass

    @abstractmethod
    async def find_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """
        Find an appointment by ID.

        Args:
            appointment_id: Unique identifier of the appointment

        Returns:
            Appointment if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
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
        pass

    @abstractmethod
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
            driver_id: Filter by assigned driver id
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of appointments matching the filters
        """
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count appointments with optional filters.

        Args:
            filters: Optional dictionary of filters to apply

        Returns:
            Total count of appointments matching the criteria
        """
        pass

    @abstractmethod
    async def update(
        self, appointment_id: str, update_data: Dict[str, Any]
    ) -> Optional[Appointment]:
        """
        Update an appointment.

        Args:
            appointment_id: ID of the appointment to update
            update_data: Dictionary with fields to update

        Returns:
            Updated appointment if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, appointment_id: str) -> bool:
        """
        Delete an appointment.

        Args:
            appointment_id: ID of the appointment to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def delete_many(self, filters: Dict[str, Any]) -> int:
        """
        Delete multiple appointments matching filters.

        Args:
            filters: Dictionary of filters to identify appointments to delete

        Returns:
            Number of appointments deleted
        """
        pass

    @abstractmethod
    async def count_by_tag(self, tag_id: str) -> int:
        """Return how many appointments reference the given tag identifier."""
        pass

    @abstractmethod
    async def update_tag_references(
        self, tag_id: str, name: str, color: str
    ) -> int:
        """Update embedded tag data for all appointments referencing a tag."""
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
    async def get_appointment_stats(self) -> Dict[str, Any]:
        """
        Get appointment statistics for dashboard.

        Returns:
            Dictionary with appointment statistics
        """
        pass

    @abstractmethod
    async def get_admin_dashboard_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Aggregate analytics required by the administrative dashboard."""
        pass
