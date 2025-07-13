"""
Dependency injection container for managing application dependencies.
"""

from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.infrastructure.config import Settings, get_settings


class Container:
    """
    Dependency injection container for managing application resources.

    This container manages the lifecycle of shared resources like
    database connections and configuration settings.
    """

    def __init__(self) -> None:
        """Initialize the container with empty resources."""
        self._settings: Optional[Settings] = None
        self._mongodb_client: Optional[Any] = None  # Actually AsyncIOMotorClient
        self._database: Optional[Any] = None  # Actually AsyncIOMotorDatabase

    @property
    def settings(self) -> Settings:
        """
        Get application settings.

        Returns:
            Settings: Application configuration
        """
        if self._settings is None:
            self._settings = get_settings()
        return self._settings

    @property
    def mongodb_client(self) -> Any:  # Actually returns AsyncIOMotorClient
        """
        Get MongoDB client instance.

        Returns:
            AsyncIOMotorClient: MongoDB client
        """
        if self._mongodb_client is None:
            from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore

            self._mongodb_client = AsyncIOMotorClient(
                self.settings.mongodb_url,
                maxPoolSize=10,
                minPoolSize=1,
            )
        return self._mongodb_client

    @property
    def database(self) -> Any:  # Actually returns AsyncIOMotorDatabase
        """
        Get MongoDB database instance.

        Returns:
            AsyncIOMotorDatabase: MongoDB database
        """
        if self._database is None:
            self._database = self.mongodb_client[self.settings.database_name]
        return self._database

    async def startup(self) -> None:
        """
        Initialize resources on application startup.
        """
        # Test database connection
        try:
            await self.mongodb_client.admin.command("ping")
            print(f"✅ Connected to MongoDB at {self.settings.mongodb_url}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def shutdown(self) -> None:
        """
        Cleanup resources on application shutdown.
        """
        if self._mongodb_client is not None:
            self._mongodb_client.close()
            print("✅ Closed MongoDB connection")


# Global container instance
container = Container()


# Dependency injection functions
async def get_database() -> (
    AsyncGenerator[Any, None]
):  # Actually yields AsyncIOMotorDatabase
    """
    Dependency for getting database instance.

    Yields:
        AsyncIOMotorDatabase: Database instance
    """
    yield container.database


async def get_app_settings() -> Settings:
    """
    Dependency for getting settings instance.

    Returns:
        Settings: Application settings
    """
    return container.settings