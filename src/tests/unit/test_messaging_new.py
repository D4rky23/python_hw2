"""Tests for Kafka messaging functionality."""

import pytest
from unittest.mock import AsyncMock

from src.infra.messaging import KafkaProducer


class TestKafkaProducer:
    """Test Kafka producer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.producer = KafkaProducer()

    @pytest.mark.asyncio
    async def test_producer_operations_without_kafka(self):
        """Test producer operations when Kafka is not available."""
        # When Kafka is not available, operations should gracefully fail
        result1 = await self.producer.send_operation_event(
            operation_type="power",
            parameters={"base": 2, "exponent": 3},
            result=8,
            duration_ms=1.0,
        )

        result2 = await self.producer.send_api_event(
            method="POST",
            endpoint="/api/v1/power",
            status_code=200,
            duration_ms=50.0,
        )

        # Should return False when Kafka is not available
        assert result1 is False
        assert result2 is False

        # Should not raise errors
        await self.producer.start()
        await self.producer.stop()

    @pytest.mark.asyncio
    async def test_operation_event_parameters(self):
        """Test operation event with various parameters."""
        # Mock the producer
        mock_producer = AsyncMock()
        self.producer._producer = mock_producer

        # Test successful operation
        await self.producer.send_operation_event(
            operation_type="fibonacci",
            parameters={"n": 10},
            result=55,
            duration_ms=2.0,
        )

        # Verify the method was called
        mock_producer.send_and_wait.assert_called_once()
        call_args = mock_producer.send_and_wait.call_args
        event_data = call_args[1]["value"]

        assert event_data["operation_type"] == "fibonacci"
        assert event_data["parameters"] == {"n": 10}
        assert event_data["result"] == "55"
        assert event_data["success"] is True

    @pytest.mark.asyncio
    async def test_operation_event_with_error(self):
        """Test operation event with error."""
        # Mock the producer
        mock_producer = AsyncMock()
        self.producer._producer = mock_producer

        # Test operation with error
        await self.producer.send_operation_event(
            operation_type="factorial",
            parameters={"n": 1000},
            result=None,
            duration_ms=1.0,
            success=False,
            error="Number too large",
        )

        # Verify the method was called
        mock_producer.send_and_wait.assert_called_once()
        call_args = mock_producer.send_and_wait.call_args
        event_data = call_args[1]["value"]

        assert event_data["operation_type"] == "factorial"
        assert event_data["success"] is False
        assert event_data["error"] == "Number too large"

    @pytest.mark.asyncio
    async def test_api_event_parameters(self):
        """Test API event with various parameters."""
        # Mock the producer
        mock_producer = AsyncMock()
        self.producer._producer = mock_producer

        # Test API event
        await self.producer.send_api_event(
            method="GET", endpoint="/health", status_code=200, duration_ms=5.0
        )

        # Verify the method was called
        mock_producer.send_and_wait.assert_called_once()
        call_args = mock_producer.send_and_wait.call_args
        event_data = call_args[1]["value"]

        assert event_data["method"] == "GET"
        assert event_data["endpoint"] == "/health"
        assert event_data["status_code"] == 200
        assert event_data["duration_ms"] == 5.0

    @pytest.mark.asyncio
    async def test_producer_error_handling(self):
        """Test producer error handling."""
        # Mock producer that fails
        mock_producer = AsyncMock()
        mock_producer.send_and_wait.side_effect = Exception("Kafka error")
        self.producer._producer = mock_producer

        # Should return False on error
        result = await self.producer.send_operation_event(
            operation_type="power",
            parameters={"base": 2, "exponent": 3},
            result=8,
            duration_ms=1.0,
        )

        assert result is False
