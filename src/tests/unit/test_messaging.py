"""Tests for Kafka messaging functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from infra.messaging import KafkaProducer


class TestKafkaProducer:
    """Test Kafka producer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.producer = KafkaProducer()

    @pytest.mark.asyncio
    async def test_producer_operations_without_kafka(self):
        """Test producer operations when Kafka is not available."""
        # When Kafka is not available, operations should gracefully fail
        await self.producer.send_operation_event(
            operation_type="power",
            parameters={"base": 2, "exponent": 3},
            result=8,
            duration_ms=1.0,
        )

        await self.producer.send_api_event(
            method="POST",
            endpoint="/api/v1/power",
            status_code=200,
            duration_ms=50.0,
        )

        # Should not raise errors
        await self.producer.start()
        await self.producer.stop()

    @pytest.mark.asyncio
    @patch("infra.messaging.messaging._producer")
    async def test_producer_operations_with_kafka(self, mock_producer):
        """Test producer operations when Kafka is available."""
        # Mock Kafka producer
        mock_producer.send_and_wait = AsyncMock()

        # Set the mock producer
        self.producer._producer = mock_producer

        # Test operation event
        await self.producer.send_operation_event(
            operation_type="power",
            parameters={"base": 2, "exponent": 3},
            result=8,
            duration_ms=1.0,
        )

        # Verify message was sent
        assert mock_producer.send_and_wait.call_count >= 1
        call_args = mock_producer.send_and_wait.call_args
        assert call_args[0][0] == "math-operations"  # topic

        # Parse the message value
        message_value = call_args[1]["value"]
        assert message_value["operation_type"] == "power"
        assert message_value["parameters"] == {"base": 2, "exponent": 3}
        assert message_value["result"] == "8"

        # Test API event
        await self.producer.send_api_event(
            method="POST",
            endpoint="/api/v1/power",
            status_code=200,
            duration_ms=50.0,
        )

        # Verify API message was sent
        assert mock_producer.send_and_wait.call_count >= 2

    @pytest.mark.asyncio
    @patch("aiokafka.AIOKafkaProducer")
    async def test_producer_error_handling(self, mock_producer_class):
        """Test producer error handling."""
        # Mock Kafka producer that fails
        mock_producer = AsyncMock()
        mock_producer.send.side_effect = Exception("Kafka error")
        mock_producer_class.return_value = mock_producer

        await self.producer.start()

        # Send operation event should not raise error
        result = await self.producer.send_operation_event(
            operation_type="power",
            parameters={"base": 2, "exponent": 3},
            error="Calculation failed",
            duration_ms=1.0,
        )

        # Should return False indicating failure
        assert result is False

    @pytest.mark.asyncio
    @patch("aiokafka.AIOKafkaProducer")
    async def test_producer_message_format(self, mock_producer_class):
        """Test message format and serialization."""
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer

        await self.producer.start()

        # Test operation event with all fields
        await self.producer.send_operation_event(
            operation="fibonacci",
            parameters={"n": 10},
            result=55,
            duration=0.002,
        )

        # Verify message structure
        call_args = mock_producer.send.call_args
        message_value = call_args[1]["value"]
        message_data = json.loads(message_value)

        expected_fields = {
            "event_type",
            "operation",
            "parameters",
            "result",
            "duration",
            "timestamp",
        }
        assert set(message_data.keys()) == expected_fields
        assert message_data["event_type"] == "operation"
        assert message_data["operation"] == "fibonacci"

    @pytest.mark.asyncio
    @patch("aiokafka.AIOKafkaProducer")
    async def test_api_event_format(self, mock_producer_class):
        """Test API event message format."""
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer

        await self.producer.start()

        # Test API event
        await self.producer.send_api_event(
            method="GET", endpoint="/health", status_code=200, duration=0.001
        )

        # Verify API message structure
        call_args = mock_producer.send.call_args
        message_value = call_args[1]["value"]
        message_data = json.loads(message_value)

        expected_fields = {
            "event_type",
            "method",
            "endpoint",
            "status_code",
            "duration",
            "timestamp",
        }
        assert set(message_data.keys()) == expected_fields
        assert message_data["event_type"] == "api"
        assert message_data["method"] == "GET"
        assert message_data["endpoint"] == "/health"
