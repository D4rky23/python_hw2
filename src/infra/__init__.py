"""Infrastructure layer components."""

from .cache import RedisCache, cache, cache_key_for_operation
from .db import AsyncSessionLocal, create_tables, get_db_session
from .logging import configure_logging, get_logger
from .messaging import KafkaProducer, kafka_producer
from .metrics import (
    get_metrics,
    operation_count,
    operation_duration,
    request_count,
    request_duration,
)

__all__ = [
    "AsyncSessionLocal",
    "create_tables",
    "get_db_session",
    "configure_logging",
    "get_logger",
    "get_metrics",
    "operation_count",
    "operation_duration",
    "request_count",
    "request_duration",
    "RedisCache",
    "cache",
    "cache_key_for_operation",
    "KafkaProducer",
    "kafka_producer",
]
