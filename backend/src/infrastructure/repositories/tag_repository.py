"""MongoDB persistence implementation for tags."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

from src.domain.entities.tag import Tag
from src.domain.repositories.tag_repository_interface import (
    TagRepositoryInterface,
)


class TagRepository(TagRepositoryInterface):
    """MongoDB-backed repository for managing tag persistence."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database
        self.collection = database.tags

    @staticmethod
    def _serialize(tag: Tag) -> Dict[str, object]:
        data = tag.model_dump(mode="python")
        data["id"] = str(data["id"])
        data["normalized_name"] = tag.normalized_name()
        return data

    @staticmethod
    def _deserialize(document: Dict[str, object]) -> Tag:
        payload = dict(document)
        payload.pop("_id", None)
        payload.pop("normalized_name", None)
        return Tag(**payload)

    async def create(self, tag: Tag) -> Tag:
        await self.collection.insert_one(self._serialize(tag))
        return tag

    async def find_by_id(self, tag_id: str) -> Optional[Tag]:
        document = await self.collection.find_one({"id": tag_id})
        if not document:
            return None
        return self._deserialize(document)

    async def find_by_ids(self, tag_ids: List[str]) -> List[Tag]:
        if not tag_ids:
            return []
        cursor = self.collection.find({"id": {"$in": tag_ids}})
        tags: List[Tag] = []
        async for document in cursor:
            tags.append(self._deserialize(document))
        return tags

    async def find_by_normalized_name(self, normalized_name: str) -> Optional[Tag]:
        document = await self.collection.find_one(
            {"normalized_name": normalized_name}
        )
        if not document:
            return None
        return self._deserialize(document)

    async def list(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        include_inactive: bool = True,
    ) -> Tuple[List[Tag], int]:
        query: Dict[str, object] = {}
        if search:
            query["name"] = {"$regex": search.strip(), "$options": "i"}
        if not include_inactive:
            query["is_active"] = True

        total = await self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort("name", ASCENDING)
            .skip(max(skip, 0))
            .limit(max(limit, 1))
        )

        tags: List[Tag] = []
        async for document in cursor:
            tags.append(self._deserialize(document))
        return tags, total

    async def update(self, tag_id: str, update_data: Dict[str, object]) -> Optional[Tag]:
        update_payload = dict(update_data)
        if "name" in update_payload and isinstance(update_payload["name"], str):
            update_payload["normalized_name"] = update_payload["name"].strip().lower()
        update_payload["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one(
            {"id": tag_id}, {"$set": update_payload}
        )
        if result.matched_count == 0:
            return None
        document = await self.collection.find_one({"id": tag_id})
        if not document:
            return None
        return self._deserialize(document)

    async def delete(self, tag_id: str) -> bool:
        result = await self.collection.delete_one({"id": tag_id})
        return result.deleted_count > 0

    async def ensure_indexes(self) -> None:
        try:
            await self.collection.create_index("id", unique=True)
            await self.collection.create_index(
                "normalized_name", unique=True, name="ux_tag_normalized_name"
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"Warning: could not create tag indexes: {exc}")

    async def exists_by_normalized_name(
        self, normalized_name: str, exclude_id: Optional[str] = None
    ) -> bool:
        query: Dict[str, object] = {"normalized_name": normalized_name}
        if exclude_id:
            query["id"] = {"$ne": exclude_id}
        existing = await self.collection.find_one(query, {"id": 1})
        return existing is not None
