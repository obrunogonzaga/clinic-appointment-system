"""
Dependency injection container for managing application dependencies.
"""

from typing import Any, AsyncGenerator, Optional

from src.infrastructure.config import Settings, get_settings
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)
from src.infrastructure.repositories.car_repository import CarRepository
from src.infrastructure.repositories.client_repository import ClientRepository
from src.infrastructure.repositories.collector_repository import (
    CollectorRepository,
)
from src.infrastructure.repositories.driver_repository import DriverRepository
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.notification_repository import NotificationRepository
from src.infrastructure.repositories.tag_repository import TagRepository
from src.infrastructure.repositories.logistics_package_repository import (
    LogisticsPackageRepository,
)
from src.infrastructure.services.redis_service import RedisService
from src.infrastructure.services.rate_limiter import RateLimiter


class Container:
    """
    Dependency injection container for managing application resources.

    This container manages the lifecycle of shared resources like
    database connections and configuration settings.
    """

    def __init__(self) -> None:
        """Initialize the container with empty resources."""
        self._settings: Optional[Settings] = None
        self._mongodb_client: Optional[Any] = (
            None  # Actually AsyncIOMotorClient
        )
        self._database: Optional[Any] = None  # Actually AsyncIOMotorDatabase
        self._appointment_repository: Optional[AppointmentRepository] = None
        self._car_repository: Optional[CarRepository] = None
        self._driver_repository: Optional[DriverRepository] = None
        self._collector_repository: Optional[CollectorRepository] = None
        self._client_repository: Optional[ClientRepository] = None
        self._user_repository: Optional[UserRepository] = None
        self._notification_repository: Optional[NotificationRepository] = None
        self._tag_repository: Optional[TagRepository] = None
        self._logistics_package_repository: Optional[
            LogisticsPackageRepository
        ] = None
        self._redis_service: Optional[RedisService] = None
        self._rate_limiter: Optional[RateLimiter] = None

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

    @property
    def car_repository(self) -> CarRepository:
        """
        Get car repository instance.

        Returns:
            CarRepository: Repository instance
        """
        if self._car_repository is None:
            self._car_repository = CarRepository(self.database)
        return self._car_repository

    @property
    def driver_repository(self) -> DriverRepository:
        """
        Get driver repository instance.

        Returns:
            DriverRepository: Repository instance
        """
        if self._driver_repository is None:
            self._driver_repository = DriverRepository(self.database)
        return self._driver_repository

    @property
    def collector_repository(self) -> CollectorRepository:
        """
        Get collector repository instance.

        Returns:
            CollectorRepository: Repository instance
        """
        if self._collector_repository is None:
            self._collector_repository = CollectorRepository(self.database)
        return self._collector_repository

    @property
    def client_repository(self) -> ClientRepository:
        """Get client repository instance."""

        if self._client_repository is None:
            self._client_repository = ClientRepository(self.database)
        return self._client_repository

    @property
    def logistics_package_repository(self) -> LogisticsPackageRepository:
        """Get logistics package repository instance."""

        if self._logistics_package_repository is None:
            self._logistics_package_repository = LogisticsPackageRepository(
                self.database
            )
        return self._logistics_package_repository

    @property
    def user_repository(self) -> UserRepository:
        """
        Get user repository instance.

        Returns:
            UserRepository: Repository instance
        """
        if self._user_repository is None:
            self._user_repository = UserRepository(self.database)
        return self._user_repository
    
    @property
    def notification_repository(self) -> NotificationRepository:
        """
        Get notification repository instance.

        Returns:
            NotificationRepository: Repository instance
        """
        if self._notification_repository is None:
            self._notification_repository = NotificationRepository(self.database)
        return self._notification_repository
    
    @property
    def tag_repository(self) -> TagRepository:
        """Get tag repository instance."""
        if self._tag_repository is None:
            self._tag_repository = TagRepository(self.database)
        return self._tag_repository
    
    @property
    def redis_service(self) -> RedisService:
        """
        Get Redis service instance.

        Returns:
            RedisService: Redis service instance
        """
        if self._redis_service is None:
            self._redis_service = RedisService(self.settings)
        return self._redis_service
    
    @property
    def rate_limiter(self) -> RateLimiter:
        """
        Get rate limiter instance.

        Returns:
            RateLimiter: Rate limiter instance
        """
        if self._rate_limiter is None:
            self._rate_limiter = RateLimiter(self.settings, self.redis_service)
        return self._rate_limiter

    async def startup(self) -> None:
        """
        Initialize resources on application startup.
        """
        # Initialize Redis service
        try:
            await self.redis_service.connect()
            print(f"✅ Connected to Redis")
        except Exception as e:
            print(f"⚠️ Redis connection failed (using in-memory fallback): {e}")
        
        # Test database connection
        try:
            await self.mongodb_client.admin.command("ping")
            print(f"✅ Connected to MongoDB at {self.settings.mongodb_url}")

            # Create database indexes
            await self.appointment_repository.create_indexes()
            await self.car_repository.create_indexes()
            await self.driver_repository.create_indexes()
            await self.collector_repository.create_indexes()
            await self.client_repository.create_indexes()
            await self.user_repository.ensure_indexes()
            await self.notification_repository.create_indexes()
            await self.tag_repository.ensure_indexes()
            await self.logistics_package_repository.create_indexes()
            print("✅ Database indexes created")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def shutdown(self) -> None:
        """
        Cleanup resources on application shutdown.
        """
        # Disconnect Redis
        if self._redis_service is not None:
            await self._redis_service.disconnect()
            print("✅ Closed Redis connection")
        
        # Close MongoDB
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


async def get_car_repository() -> CarRepository:
    """
    Dependency for getting car repository instance.

    Returns:
        CarRepository: Repository instance
    """
    return container.car_repository


async def get_driver_repository() -> DriverRepository:
    """
    Dependency for getting driver repository instance.

    Returns:
        DriverRepository: Repository instance
    """
    return container.driver_repository


async def get_collector_repository() -> CollectorRepository:
    """
    Dependency for getting collector repository instance.

    Returns:
        CollectorRepository: Repository instance
    """
    return container.collector_repository


async def get_client_repository() -> ClientRepository:
    """Dependency for getting client repository instance."""

    return container.client_repository


async def get_user_repository() -> UserRepository:
    """
    Dependency for getting user repository instance.

    Returns:
        UserRepository: Repository instance
    """
    return container.user_repository


async def get_tag_repository() -> TagRepository:
    """Dependency for getting tag repository instance."""
    return container.tag_repository


async def get_logistics_package_repository() -> LogisticsPackageRepository:
    """Dependency for getting logistics package repository instance."""

    return container.logistics_package_repository
