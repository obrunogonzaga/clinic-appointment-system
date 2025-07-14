"""
Dependency injection container for managing application dependencies.
"""

from typing import Any, AsyncGenerator, Optional

from src.infrastructure.config import Settings, get_settings
from src.infrastructure.repositories.appointment_repository import AppointmentRepository


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
        self._appointment_repository: Optional[AppointmentRepository] = None

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
            from motor.motor_asyncio import AsyncIOMotorClient

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
    
    @property
    def appointment_repository(self) -> AppointmentRepository:
        """
        Get appointment repository instance.
        
        Returns:
            AppointmentRepository: Repository instance
        """
        if self._appointment_repository is None:
            self._appointment_repository = AppointmentRepository(self.database)
        return self._appointment_repository

    async def startup(self) -> None:
        """
        Initialize resources on application startup.
        """
        # Test database connection
        try:
            await self.mongodb_client.admin.command("ping")
            print(f"✅ Connected to MongoDB at {self.settings.mongodb_url}")
            
            # Create database indexes
            await self.appointment_repository.create_indexes()
            print("✅ Database indexes created")
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


async def get_appointment_repository() -> AppointmentRepository:
    """
    Dependency for getting appointment repository instance.

    Returns:
        AppointmentRepository: Repository instance
    """
    return container.appointment_repository
