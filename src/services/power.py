"""Power calculation service."""

import time
from datetime import datetime, timezone
from typing import Any, Dict

from domain.models import MathOperation, PowerRequest, PowerResult
from repositories.interfaces import MathOperationRepository
from config import settings
from infra.logging import get_logger
from infra.metrics import operation_count, operation_duration
from infra import cache, cache_key_for_operation
from infra.messaging import send_operation_event

logger = get_logger(__name__)


class PowerService:
    """Service for power calculations."""

    def __init__(self, repository: MathOperationRepository) -> None:
        """Initialize with repository dependency."""
        self.repository = repository

    async def calculate_power(self, request: PowerRequest) -> PowerResult:
        """Calculate base^exponent with caching, logging and persistence."""
        start_time = time.time()

        # Generate cache key
        cache_key = cache_key_for_operation(
            "power", base=request.base, exponent=request.exponent
        )

        try:
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.info(
                    "Power calculation cache hit",
                    base=request.base,
                    exponent=request.exponent,
                    result=cached_result,
                )
                return PowerResult(
                    base=request.base,
                    exponent=request.exponent,
                    result=cached_result,
                )

            # Validate input limits
            if request.base > settings.max_power_base:
                raise ValueError(f"Base must be <= {settings.max_power_base}")
            if request.exponent > settings.max_power_exponent:
                raise ValueError(
                    f"Exponent must be <= {settings.max_power_exponent}"
                )

            # Additional overflow protection
            # Prevent calculations that would create extremely large numbers
            # Check more specific cases first
            if request.base > 100 and request.exponent > 20:
                raise ValueError(
                    "Calculation would result in overflow: large base with large exponent"
                )
            if request.base > 10 and request.exponent > 100:
                raise ValueError(
                    "Calculation would result in overflow: base > 10 with exponent > 100"
                )
            if request.exponent > 50:
                raise ValueError(
                    f"Exponent too large: {request.exponent}. Maximum safe exponent is 50"
                )

            # Estimate result size to prevent memory issues
            import math

            try:
                # Use logarithms to estimate the size of the result
                if request.base > 1 and request.exponent > 0:
                    log_result = request.exponent * math.log10(request.base)
                    if log_result > 1000:  # Result would have > 1000 digits
                        raise ValueError(
                            f"Result would be too large (estimated {int(log_result)} digits)"
                        )
            except (ValueError, OverflowError):
                raise ValueError("Calculation parameters would cause overflow")

            # Calculate result with overflow protection
            try:
                result = request.base**request.exponent
            except (OverflowError, MemoryError):
                raise ValueError(
                    f"Calculation {request.base}^{request.exponent} causes overflow or memory error"
                )

            # Cache the result
            await cache.set(cache_key, result, ttl=3600)  # Cache for 1 hour

            # Create result object
            power_result = PowerResult(
                base=request.base,
                exponent=request.exponent,
                result=result,
            )

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log the operation
            logger.info(
                "Power calculation completed",
                base=request.base,
                exponent=request.exponent,
                result=result,
                duration_ms=duration_ms,
            )

            # Send operation event to Kafka
            await send_operation_event(
                operation_type="power",
                parameters={
                    "base": request.base,
                    "exponent": request.exponent,
                },
                result=result,
                duration_ms=duration_ms,
            )

            # Create domain operation for persistence
            operation = MathOperation(
                operation_type="power",
                parameters={
                    "base": request.base,
                    "exponent": request.exponent,
                },
                result=result,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc),
            )

            # Save to repository
            await self.repository.save_operation(operation)

            # Update metrics
            operation_count.labels(
                operation_type="power", status="success"
            ).inc()
            operation_duration.labels(operation_type="power").observe(
                duration_ms / 1000
            )

            return power_result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Send error event to Kafka
            await send_operation_event(
                operation_type="power",
                parameters={
                    "base": request.base,
                    "exponent": request.exponent,
                },
                result=None,
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            )

            logger.error(
                "Power calculation failed",
                base=request.base,
                exponent=request.exponent,
                error=str(e),
                duration_ms=duration_ms,
            )

            operation_count.labels(
                operation_type="power", status="error"
            ).inc()
            raise
