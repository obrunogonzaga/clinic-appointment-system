"""Interface para repositórios de clientes."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.domain.entities.client import Client, ClientAppointmentHistoryEntry


class ClientRepositoryInterface(ABC):
    """Contrato para persistência de clientes."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Persist a new client entity."""

    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Update an existing client entity."""

    @abstractmethod
    async def find_by_id(self, client_id: str) -> Optional[Client]:
        """Retrieve a client by identifier."""

    @abstractmethod
    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        """Retrieve a client using CPF as unique key."""

    @abstractmethod
    async def list_clients(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Client], int]:
        """List clients applying optional search and pagination."""

    @abstractmethod
    async def ensure_indexes(self) -> None:
        """Ensure database indexes for the collection exist."""

    @abstractmethod
    async def append_history_entry(
        self, client_id: str, entry: ClientAppointmentHistoryEntry
    ) -> None:
        """Append a history entry without duplications."""
