"""Redis cache implementation."""

import json
import pickle
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from config import settings
from infra.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache manager."""

    def __init__(self):
        self._redis: Optional[Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if not settings.redis_enabled:
            logger.info("Redis caching disabled")
            return

        try:
            self._redis = redis.from_url(
                settings.redis_url,
                password=settings.redis_password or None,
                db=settings.redis_db,
                decode_responses=False,  # We'll handle encoding ourselves
            )
            # Test connection
            await self._redis.ping()
            logger.info(
                "Connected to Redis",
                url=settings.redis_url,
                db=settings.redis_db,
            )
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self._redis = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.aclose()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None

        try:
            value = await self._redis.get(key)
            if value is None:
                return None

            # Try to deserialize with pickle first, then JSON
            try:
                return pickle.loads(value)
            except (pickle.PickleError, TypeError):
                try:
                    return json.loads(value.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return value.decode("utf-8")

        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        if not self._redis:
            return False

        try:
            # Serialize value
            if isinstance(value, (str, bytes)):
                serialized = value
            elif isinstance(value, (int, float)):
                serialized = pickle.dumps(value)
            else:
                try:
                    serialized = json.dumps(value).encode("utf-8")
                except (TypeError, ValueError):
                    serialized = pickle.dumps(value)

            ttl = ttl or settings.redis_ttl
            await self._redis.setex(key, ttl, serialized)
            return True

        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._redis:
            return False

        try:
            result = await self._redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._redis:
            return False

        try:
            result = await self._redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.warning("Cache exists check failed", key=key, error=str(e))
            return False


# Global cache instance
cache = RedisCache()


def cache_key_for_operation(operation_type: str, **params) -> str:
    """Generate cache key for math operations."""
    # Sort params for consistent keys
    sorted_params = sorted(params.items())
    param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
    return f"math:{operation_type}:{param_str}"
