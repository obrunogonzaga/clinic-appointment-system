"""Tag repository contract for persistence implementations."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from src.domain.entities.tag import Tag


class TagRepositoryInterface(ABC):
    """Interface describing persistence operations for tags."""

    @abstractmethod
    async def create(self, tag: Tag) -> Tag:
        """Persist a new tag entity."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, tag_id: str) -> Optional[Tag]:
        """Retrieve a tag by its identifier."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_ids(self, tag_ids: List[str]) -> List[Tag]:
        """Retrieve multiple tags given their identifiers."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_normalized_name(self, normalized_name: str) -> Optional[Tag]:
        """Retrieve a tag by its normalized (lowercase) name."""
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        include_inactive: bool = True,
    ) -> Tuple[List[Tag], int]:
        """List tags with optional search and pagination, returning items and total count."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, tag_id: str, update_data: Dict[str, object]) -> Optional[Tag]:
        """Update persisted tag fields."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, tag_id: str) -> bool:
        """Delete tag permanently."""
        raise NotImplementedError

    @abstractmethod
    async def ensure_indexes(self) -> None:
        """Create required database indexes."""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_normalized_name(
        self, normalized_name: str, exclude_id: Optional[str] = None
    ) -> bool:
        """Check if a tag with the normalized name exists (optionally excluding an ID)."""
        raise NotImplementedError
