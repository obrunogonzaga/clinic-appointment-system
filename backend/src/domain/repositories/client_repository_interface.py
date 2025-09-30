"""Interface definition for client repositories."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.client import Client


class ClientRepositoryInterface(ABC):
    """Abstract repository contract for client persistence."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Persist a new client."""

    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Persist changes to an existing client."""

    @abstractmethod
    async def find_by_id(self, client_id: str) -> Optional[Client]:
        """Retrieve a client by its identifier."""

    @abstractmethod
    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        """Retrieve a client by CPF."""

    @abstractmethod
    async def find_by_filters(
        self, search: Optional[str], skip: int = 0, limit: int = 50
    ) -> List[Client]:
        """List clients with optional search and pagination."""

    @abstractmethod
    async def count(self, search: Optional[str] = None) -> int:
        """Count total clients for the provided search criteria."""

    @abstractmethod
    async def ensure_indexes(self) -> None:
        """Create database indexes if they do not exist."""
