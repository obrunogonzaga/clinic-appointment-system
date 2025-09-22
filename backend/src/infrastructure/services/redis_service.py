"""
Redis service for caching and rate limiting.
"""

import json
from typing import Any, Optional
from datetime import timedelta
import logging

import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError

from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class RedisService:
    """
    Service for managing Redis connections and operations.
    
    Provides async Redis operations with automatic reconnection
    and fallback to memory storage if Redis is unavailable.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize Redis service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379')
        self.redis_password = getattr(settings, 'redis_password', None)
        self.redis_db = getattr(settings, 'redis_db', 0)
        self.redis: Optional[aioredis.Redis] = None
        self.connected = False
        self.memory_cache = {}  # Fallback memory cache
        
    async def connect(self) -> bool:
        """
        Connect to Redis server.
        
        Returns:
            True if connection successful
        """
        try:
            self.redis = await redis.from_url(
                self.redis_url,
                password=self.redis_password,
                db=self.redis_db,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=10,
            )
            
            # Test connection
            await self.redis.ping()
            self.connected = True
            logger.info("Redis connection established")
            return True
            
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            logger.info("Using in-memory cache as fallback")
            self.connected = False
            return False
            
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("Redis connection closed")
            
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if self.connected and self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                # Fall through to memory cache
                
        # Fallback to memory cache
        return self.memory_cache.get(key)
        
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            
        Returns:
            True if successful
        """
        # Serialize complex objects
        if not isinstance(value, (str, int, float, bool)):
            value = json.dumps(value)
            
        if self.connected and self.redis:
            try:
                if expire:
                    await self.redis.setex(key, expire, value)
                else:
                    await self.redis.set(key, value)
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                # Fall through to memory cache
                
        # Fallback to memory cache
        self.memory_cache[key] = value
        # Note: Memory cache doesn't support expiration
        return True
        
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted
        """
        if self.connected and self.redis:
            try:
                await self.redis.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                # Fall through to memory cache
                
        # Fallback to memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            return True
        return False
        
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        if self.connected and self.redis:
            try:
                return await self.redis.exists(key) > 0
            except Exception as e:
                logger.error(f"Redis exists error: {e}")
                # Fall through to memory cache
                
        # Fallback to memory cache
        return key in self.memory_cache
        
    async def increment(
        self, 
        key: str, 
        amount: int = 1,
        expire: Optional[int] = None
    ) -> int:
        """
        Increment counter in cache.
        
        Args:
            key: Counter key
            amount: Amount to increment
            expire: Expiration time in seconds
            
        Returns:
            New counter value
        """
        if self.connected and self.redis:
            try:
                value = await self.redis.incrby(key, amount)
                if expire and value == amount:  # First increment
                    await self.redis.expire(key, expire)
                return value
            except Exception as e:
                logger.error(f"Redis increment error: {e}")
                # Fall through to memory cache
                
        # Fallback to memory cache
        current = self.memory_cache.get(key, 0)
        new_value = current + amount
        self.memory_cache[key] = new_value
        return new_value
        
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get time-to-live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiry, None if key doesn't exist
        """
        if self.connected and self.redis:
            try:
                ttl = await self.redis.ttl(key)
                return ttl if ttl >= 0 else None
            except Exception as e:
                logger.error(f"Redis TTL error: {e}")
                
        # Memory cache doesn't support TTL
        return -1 if key in self.memory_cache else None
        
    async def set_hash(self, key: str, field: str, value: Any) -> bool:
        """
        Set field in hash.
        
        Args:
            key: Hash key
            field: Field name
            value: Field value
            
        Returns:
            True if successful
        """
        if not isinstance(value, (str, int, float, bool)):
            value = json.dumps(value)
            
        if self.connected and self.redis:
            try:
                await self.redis.hset(key, field, value)
                return True
            except Exception as e:
                logger.error(f"Redis hset error: {e}")
                
        # Fallback to memory cache
        if key not in self.memory_cache:
            self.memory_cache[key] = {}
        self.memory_cache[key][field] = value
        return True
        
    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        """
        Get field from hash.
        
        Args:
            key: Hash key
            field: Field name
            
        Returns:
            Field value or None
        """
        if self.connected and self.redis:
            try:
                value = await self.redis.hget(key, field)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            except Exception as e:
                logger.error(f"Redis hget error: {e}")
                
        # Fallback to memory cache
        if key in self.memory_cache and isinstance(self.memory_cache[key], dict):
            return self.memory_cache[key].get(field)
        return None
        
    async def get_all_hash(self, key: str) -> dict:
        """
        Get all fields from hash.
        
        Args:
            key: Hash key
            
        Returns:
            Dictionary of all fields
        """
        if self.connected and self.redis:
            try:
                data = await self.redis.hgetall(key)
                # Try to deserialize JSON values
                result = {}
                for field, value in data.items():
                    try:
                        result[field] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[field] = value
                return result
            except Exception as e:
                logger.error(f"Redis hgetall error: {e}")
                
        # Fallback to memory cache
        return self.memory_cache.get(key, {})
        
    async def add_to_set(self, key: str, *values: Any) -> int:
        """
        Add values to a set.
        
        Args:
            key: Set key
            values: Values to add
            
        Returns:
            Number of values added
        """
        if self.connected and self.redis:
            try:
                return await self.redis.sadd(key, *values)
            except Exception as e:
                logger.error(f"Redis sadd error: {e}")
                
        # Fallback to memory cache (using list as simple set)
        if key not in self.memory_cache:
            self.memory_cache[key] = set()
        before = len(self.memory_cache[key])
        self.memory_cache[key].update(values)
        return len(self.memory_cache[key]) - before
        
    async def is_in_set(self, key: str, value: Any) -> bool:
        """
        Check if value is in set.
        
        Args:
            key: Set key
            value: Value to check
            
        Returns:
            True if value is in set
        """
        if self.connected and self.redis:
            try:
                return await self.redis.sismember(key, value)
            except Exception as e:
                logger.error(f"Redis sismember error: {e}")
                
        # Fallback to memory cache
        if key in self.memory_cache and isinstance(self.memory_cache[key], set):
            return value in self.memory_cache[key]
        return False
        
    async def get_set_members(self, key: str) -> set:
        """
        Get all members of a set.
        
        Args:
            key: Set key
            
        Returns:
            Set of all members
        """
        if self.connected and self.redis:
            try:
                return await self.redis.smembers(key)
            except Exception as e:
                logger.error(f"Redis smembers error: {e}")
                
        # Fallback to memory cache
        return self.memory_cache.get(key, set())
        
    def is_available(self) -> bool:
        """
        Check if Redis is available.
        
        Returns:
            True if Redis is connected
        """
        return self.connected