"""Interface for logistics package repository implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.logistics_package import LogisticsPackage


class LogisticsPackageRepositoryInterface(ABC):
    """Repository contract for managing logistics packages."""

    @abstractmethod
    async def create(self, package: LogisticsPackage) -> LogisticsPackage:
        """Persist a new logistics package."""

    @abstractmethod
    async def find_by_id(self, package_id: str) -> Optional[LogisticsPackage]:
        """Retrieve a logistics package by its identifier."""

    @abstractmethod
    async def find_all(
        self, *, status: Optional[str] = None
    ) -> List[LogisticsPackage]:
        """List packages, optionally filtering by status."""

    @abstractmethod
    async def update(
        self, package_id: str, changes: dict
    ) -> Optional[LogisticsPackage]:
        """Apply partial changes to an existing package."""

    @abstractmethod
    async def delete(self, package_id: str) -> bool:
        """Remove a package permanently."""

    @abstractmethod
    async def create_indexes(self) -> None:
        """Ensure collection indexes exist."""

