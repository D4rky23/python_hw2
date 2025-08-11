"""Kafka messaging implementation."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from config import settings
from .logging import get_logger

logger = get_logger(__name__)


class KafkaProducer:
    """Kafka message producer."""

    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """Start Kafka producer."""
        if not settings.kafka_enabled:
            logger.info("Kafka messaging disabled")
            return

        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            logger.info(
                "Kafka producer started",
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_topic,
            )
        except Exception as e:
            logger.error("Failed to start Kafka producer", error=str(e))
            self._producer = None

    async def stop(self) -> None:
        """Stop Kafka producer."""
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped")

    async def send_operation_event(
        self,
        operation_type: str,
        parameters: Dict[str, Any],
        result: Any,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
    ) -> bool:
        """Send math operation event to Kafka."""
        if not self._producer:
            return False

        try:
            event = {
                "event_type": "math_operation",
                "operation_type": operation_type,
                "parameters": parameters,
                "result": str(result) if result is not None else None,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Use operation type as key for partitioning
            key = f"{operation_type}"

            await self._producer.send_and_wait(
                settings.kafka_topic, value=event, key=key
            )

            logger.debug(
                "Operation event sent to Kafka",
                operation_type=operation_type,
                success=success,
            )
            return True

        except KafkaError as e:
            logger.warning(
                "Failed to send Kafka message",
                operation_type=operation_type,
                error=str(e),
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error sending Kafka message",
                operation_type=operation_type,
                error=str(e),
            )
            return False

    async def send_api_event(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Send API request event to Kafka."""
        if not self._producer:
            return False

        try:
            event = {
                "event_type": "api_request",
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "user_agent": user_agent,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Use endpoint as key for partitioning
            key = f"{method}:{endpoint}"

            await self._producer.send_and_wait(
                settings.kafka_topic, value=event, key=key
            )

            logger.debug(
                "API event sent to Kafka",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            )
            return True

        except Exception as e:
            logger.warning(
                "Failed to send API event to Kafka",
                method=method,
                endpoint=endpoint,
                error=str(e),
            )
            return False


# Global producer instance
kafka_producer = KafkaProducer()


# Convenience functions for backward compatibility
async def send_operation_event(
    operation_type: str,
    parameters: Dict[str, Any],
    result: Any,
    duration_ms: float,
    success: bool = True,
    error: Optional[str] = None,
) -> bool:
    """Send math operation event to Kafka."""
    return await kafka_producer.send_operation_event(
        operation_type=operation_type,
        parameters=parameters,
        result=result,
        duration_ms=duration_ms,
        success=success,
        error=error,
    )


async def send_api_event(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    user_agent: Optional[str] = None,
) -> bool:
    """Send API request event to Kafka."""
    return await kafka_producer.send_api_event(
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
        user_agent=user_agent,
    )
