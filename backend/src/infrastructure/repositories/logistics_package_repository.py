"""MongoDB repository for logistics packages."""

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

from src.domain.entities.logistics_package import LogisticsPackage
from src.domain.repositories.logistics_package_repository_interface import (
    LogisticsPackageRepositoryInterface,
)


class LogisticsPackageRepository(LogisticsPackageRepositoryInterface):
    """Persist logistics packages on MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.logistics_packages

    async def create(self, package: LogisticsPackage) -> LogisticsPackage:
        payload = package.model_dump()
        payload["id"] = str(payload["id"])
        await self.collection.insert_one(payload)
        return package

    async def find_by_id(self, package_id: str) -> Optional[LogisticsPackage]:
        doc = await self.collection.find_one({"id": package_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return LogisticsPackage(**doc)

    async def find_all(
        self, *, status: Optional[str] = None
    ) -> List[LogisticsPackage]:
        filters: Dict[str, Any] = {}
        if status:
            filters["status"] = status

        cursor = self.collection.find(filters).sort("nome", ASCENDING)
        packages: List[LogisticsPackage] = []
        async for doc in cursor:
            doc.pop("_id", None)
            packages.append(LogisticsPackage(**doc))
        return packages

    async def update(
        self, package_id: str, changes: Dict[str, Any]
    ) -> Optional[LogisticsPackage]:
        if not changes:
            return await self.find_by_id(package_id)

        await self.collection.update_one({"id": package_id}, {"$set": changes})
        return await self.find_by_id(package_id)

    async def delete(self, package_id: str) -> bool:
        result = await self.collection.delete_one({"id": package_id})
        return result.deleted_count > 0

    async def create_indexes(self) -> None:
        await self.collection.create_index("id", unique=True)
        await self.collection.create_index("nome", unique=True)
        await self.collection.create_index("status")

