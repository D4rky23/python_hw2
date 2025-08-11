"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.core import CollectorRegistry


# Create custom registry to avoid conflicts
registry = CollectorRegistry()

# Request metrics
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    registry=registry,
)

# Operation metrics
operation_count = Counter(
    "math_operations_total",
    "Total math operations",
    ["operation_type", "status"],
    registry=registry,
)

operation_duration = Histogram(
    "math_operation_duration_seconds",
    "Math operation duration in seconds",
    ["operation_type"],
    registry=registry,
)

# Database metrics
db_operation_count = Counter(
    "db_operations_total",
    "Total database operations",
    ["operation_type", "status"],
    registry=registry,
)


def get_metrics() -> str:
    """Get metrics in Prometheus format."""
    return generate_latest(registry).decode("utf-8")
