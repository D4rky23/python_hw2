"""Fibonacci calculation service."""

import time
from datetime import datetime, timezone
from typing import Dict, List

from domain.models import FibonacciResult, MathOperation
from repositories.interfaces import MathOperationRepository
from config import settings
from infra.logging import get_logger
from infra.metrics import operation_count, operation_duration

logger = get_logger(__name__)


class FibonacciService:
    """Service for Fibonacci calculations."""

    def __init__(self, repository: MathOperationRepository) -> None:
        """Initialize with repository dependency."""
        self.repository = repository
        self._cache: Dict[int, int] = {0: 0, 1: 1}

    def _calculate_fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number using dynamic programming."""
        if n in self._cache:
            return self._cache[n]

        # Initialize for iterative calculation
        if n < 2:
            return n

        # Calculate iteratively to avoid recursion limits
        a, b = 0, 1
        for i in range(2, n + 1):
            a, b = b, a + b
            # Cache intermediate results for efficiency
            if i not in self._cache:
                self._cache[i] = b

        return b

    async def calculate_fibonacci(self, n: int) -> FibonacciResult:
        """Calculate nth Fibonacci number with logging and persistence."""
        start_time = time.time()

        try:
            # Validate input
            if not isinstance(n, int):
                raise ValueError("N must be an integer")
            if n < 0:
                raise ValueError("N must be non-negative")
            if n > settings.max_fibonacci_n:
                raise ValueError(f"N must be <= {settings.max_fibonacci_n}")

            # Calculate result
            result = self._calculate_fibonacci(n)

            # Create result object
            fib_result = FibonacciResult(n=n, result=result)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log the operation
            logger.info(
                "Fibonacci calculation completed",
                n=n,
                result=result,
                duration_ms=duration_ms,
            )

            # Create domain operation for persistence
            operation = MathOperation(
                operation_type="fibonacci",
                parameters={"n": n},
                result=result,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc),
            )

            # Save to repository
            await self.repository.save_operation(operation)

            # Update metrics
            operation_count.labels(
                operation_type="fibonacci", status="success"
            ).inc()
            operation_duration.labels(operation_type="fibonacci").observe(
                duration_ms / 1000
            )

            return fib_result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "Fibonacci calculation failed",
                n=n,
                error=str(e),
                duration_ms=duration_ms,
            )

            operation_count.labels(
                operation_type="fibonacci", status="error"
            ).inc()
            raise
