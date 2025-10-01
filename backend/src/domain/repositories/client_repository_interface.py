"""Client repository interface defining persistence contract."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.entities.client import Client, ConvenioInfo


class ClientRepositoryInterface(ABC):
    """Interface for client repository operations."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client record."""

    @abstractmethod
    async def update(
        self, client_id: str, update_data: Dict[str, Any]
    ) -> Optional[Client]:
        """Update a client by identifier."""

    @abstractmethod
    async def find_by_id(self, client_id: str) -> Optional[Client]:
        """Find a client using its identifier."""

    @abstractmethod
    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        """Find a client using CPF."""

    @abstractmethod
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Client]:
        """List clients using optional filters with pagination."""

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count clients using optional filters."""

    @abstractmethod
    async def add_appointment(
        self,
        client_id: str,
        appointment_id: str,
        last_appointment_at: Optional[datetime] = None,
        last_address: Optional[str] = None,
        last_address_normalized: Optional[Dict[str, Optional[str]]] = None,
    ) -> Optional[Client]:
        """Link an appointment to a client and update last appointment metadata."""

    @abstractmethod
    async def upsert_convenio(
        self,
        client_id: str,
        convenio: ConvenioInfo,
    ) -> Optional[Client]:
        """Add or update a health insurance in the client's convenio history."""

    @abstractmethod
    async def create_indexes(self) -> None:
        """Ensure database indexes for client collection."""
