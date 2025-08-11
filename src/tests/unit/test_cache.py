"""Tests for Redis cache functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.infra.cache import RedisCache, cache_key_for_operation


class TestRedisCache:
    """Test Redis cache functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache = RedisCache()

    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation for operations."""
        # Test power operation
        key = cache_key_for_operation("power", base=2, exponent=3)
        assert key == "math:power:base=2&exponent=3"

        # Test fibonacci operation
        key = cache_key_for_operation("fibonacci", n=10)
        assert key == "math:fibonacci:n=10"

        # Test factorial operation
        key = cache_key_for_operation("factorial", n=5)
        assert key == "math:factorial:n=5"

    @pytest.mark.asyncio
    async def test_cache_operations_without_redis(self):
        """Test cache operations when Redis is not available."""
        # When Redis is not available, operations should gracefully fail
        result = await self.cache.get("test_key")
        assert result is None

        # Set should not raise error
        await self.cache.set("test_key", "test_value")

        # Delete should not raise error
        await self.cache.delete("test_key")

        # Exists should return False
        exists = await self.cache.exists("test_key")
        assert exists is False

    @pytest.mark.asyncio
    @patch("infra.cache.cache._redis")
    async def test_cache_operations_with_redis(self, mock_redis):
        """Test cache operations when Redis is available."""
        # Mock Redis client with async methods
        mock_redis.get = AsyncMock(return_value=b'"test_value"')
        mock_redis.exists = AsyncMock(return_value=True)
        mock_redis.setex = AsyncMock()
        mock_redis.delete = AsyncMock()

        # Set the mock redis client
        self.cache._redis = mock_redis

        # Test get operation
        result = await self.cache.get("test_key")
        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")

        # Test set operation
        await self.cache.set("test_key", "new_value", ttl=3600)
        mock_redis.setex.assert_called_once_with("test_key", 3600, "new_value")

        # Test exists operation
        exists = await self.cache.exists("test_key")
        assert exists is True
        mock_redis.exists.assert_called_once_with("test_key")

        # Test delete operation
        await self.cache.delete("test_key")
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    @patch("redis.asyncio.Redis")
    async def test_cache_connection_failure(self, mock_redis_class):
        """Test cache behavior when Redis connection fails."""
        # Mock Redis connection failure
        mock_redis_class.from_url.side_effect = Exception("Connection failed")

        # Connect should not raise error
        await self.cache.connect()

        # Operations should gracefully fail
        result = await self.cache.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    @patch("infra.cache.cache._redis")
    async def test_cache_json_serialization(self, mock_redis):
        """Test JSON serialization/deserialization in cache."""
        # Test complex data structure
        test_data = {"result": 42, "metadata": {"type": "power", "base": 2}}
        mock_redis.get = AsyncMock(
            return_value=b'{"result": 42, "metadata": {"type": "power", "base": 2}}'
        )
        mock_redis.setex = AsyncMock()

        # Set the mock redis client
        self.cache._redis = mock_redis

        # Test get with complex data
        result = await self.cache.get("test_key")
        assert result == test_data

        # Test set with complex data
        await self.cache.set("test_key", test_data)
        expected_json = (
            b'{"result": 42, "metadata": {"type": "power", "base": 2}}'
        )
        mock_redis.setex.assert_called_once_with(
            "test_key", 3600, expected_json
        )
