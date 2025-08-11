"""Integration tests for Redis cache and Kafka messaging."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from main import create_app
from config import settings


class TestCacheAndMessagingIntegration:
    """Test Redis cache and Kafka messaging integration."""

    @pytest.mark.asyncio
    @patch('infra.cache.cache')
    @patch('infra.messaging.messaging')
    async def test_power_calculation_with_cache_and_messaging(self, mock_messaging, mock_cache):
        """Test power calculation with caching and messaging."""
        # Setup mocks
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.set = AsyncMock()
        mock_cache.connect = AsyncMock()
        mock_cache.disconnect = AsyncMock()
        mock_messaging.start = AsyncMock()
        mock_messaging.stop = AsyncMock()
        mock_messaging.send_operation_event = AsyncMock()
        mock_messaging.send_api_event = AsyncMock()

        # Override settings for test
        settings.redis_enabled = True
        settings.kafka_enabled = True

        app = create_app()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Make power calculation request
            response = await client.post(
                "/api/v1/power",
                json={"base": 2, "exponent": 3}
            )

        assert response.status_code == 200
        result = response.json()
        assert result["result"] == 8

        # Verify cache was checked and set
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

        # Verify Kafka events were sent
        mock_messaging.send_operation_event.assert_called_once()
        mock_messaging.send_api_event.assert_called_once()

    @pytest.mark.asyncio
    @patch('infra.cache.cache')
    @patch('infra.messaging.messaging')
    async def test_fibonacci_calculation_with_cache_hit(self, mock_messaging, mock_cache):
        """Test fibonacci calculation with cache hit."""
        # Setup cache hit
        mock_cache.get.return_value = 55  # Cached result for fibonacci(10)
        mock_cache.connect = AsyncMock()
        mock_cache.disconnect = AsyncMock()
        mock_messaging.start = AsyncMock()
        mock_messaging.stop = AsyncMock()
        mock_messaging.send_api_event = AsyncMock()

        settings.redis_enabled = True
        settings.kafka_enabled = True

        app = create_app()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/fibonacci/10")

        assert response.status_code == 200
        result = response.json()
        assert result["result"] == 55

        # Verify cache was checked but not set (cache hit)
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()

        # API event should still be sent
        mock_messaging.send_api_event.assert_called_once()

    @pytest.mark.asyncio
    @patch('infra.cache.cache')
    @patch('infra.messaging.messaging')
    async def test_factorial_calculation_with_error_messaging(self, mock_messaging, mock_cache):
        """Test factorial calculation error handling with messaging."""
        # Setup mocks
        mock_cache.get.return_value = None
        mock_cache.connect = AsyncMock()
        mock_cache.disconnect = AsyncMock()
        mock_messaging.start = AsyncMock()
        mock_messaging.stop = AsyncMock()
        mock_messaging.send_operation_event = AsyncMock()
        mock_messaging.send_api_event = AsyncMock()

        settings.redis_enabled = True
        settings.kafka_enabled = True

        app = create_app()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Request factorial with too large number
            response = await client.post(
                "/api/v1/factorial",
                json={"n": 1000}  # Exceeds max_factorial_n
            )

        assert response.status_code == 400

        # Verify error operation event was sent
        mock_messaging.send_operation_event.assert_called_once()
        call_args = mock_messaging.send_operation_event.call_args
        assert 'error' in call_args[1]

        # API event should be sent for error response
        mock_messaging.send_api_event.assert_called_once()

    @pytest.mark.asyncio
    @patch('infra.cache.cache')
    @patch('infra.messaging.messaging')
    async def test_cache_and_messaging_disabled(self, mock_messaging, mock_cache):
        """Test operation when cache and messaging are disabled."""
        # Disable cache and messaging
        settings.redis_enabled = False
        settings.kafka_enabled = False

        app = create_app()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/power",
                json={"base": 3, "exponent": 2}
            )

        assert response.status_code == 200
        result = response.json()
        assert result["result"] == 9

        # Verify cache and messaging were not used
        mock_cache.connect.assert_not_called()
        mock_messaging.start.assert_not_called()

    @pytest.mark.asyncio
    @patch('infra.cache.cache')
    @patch('infra.messaging.messaging')
    async def test_service_resilience_to_cache_failures(self, mock_messaging, mock_cache):
        """Test service continues working when cache operations fail."""
        # Setup cache to fail
        mock_cache.get.side_effect = Exception("Redis connection failed")
        mock_cache.set.side_effect = Exception("Redis connection failed")
        mock_cache.connect = AsyncMock()
        mock_cache.disconnect = AsyncMock()
        mock_messaging.start = AsyncMock()
        mock_messaging.stop = AsyncMock()
        mock_messaging.send_operation_event = AsyncMock()
        mock_messaging.send_api_event = AsyncMock()

        settings.redis_enabled = True
        settings.kafka_enabled = True

        app = create_app()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/power",
                json={"base": 4, "exponent": 2}
            )

        # Service should still work despite cache failures
        assert response.status_code == 200
        result = response.json()
        assert result["result"] == 16

        # Messaging should still work
        mock_messaging.send_operation_event.assert_called_once()
        mock_messaging.send_api_event.assert_called_once()

    @pytest.mark.asyncio
    @patch('infra.cache.cache')
    @patch('infra.messaging.messaging')
    async def test_service_resilience_to_messaging_failures(self, mock_messaging, mock_cache):
        """Test service continues working when messaging operations fail."""
        # Setup messaging to fail
        mock_cache.get.return_value = None
        mock_cache.set = AsyncMock()
        mock_cache.connect = AsyncMock()
        mock_cache.disconnect = AsyncMock()
        mock_messaging.start = AsyncMock()
        mock_messaging.stop = AsyncMock()
        mock_messaging.send_operation_event.side_effect = Exception("Kafka connection failed")
        mock_messaging.send_api_event.side_effect = Exception("Kafka connection failed")

        settings.redis_enabled = True
        settings.kafka_enabled = True

        app = create_app()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/power",
                json={"base": 5, "exponent": 2}
            )

        # Service should still work despite messaging failures
        assert response.status_code == 200
        result = response.json()
        assert result["result"] == 25

        # Cache should still work
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
