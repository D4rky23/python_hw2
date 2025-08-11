"""Factorial calculation service."""

import time
from datetime import datetime, timezone

from domain.models import FactorialRequest, FactorialResult, MathOperation
from repositories.interfaces import MathOperationRepository
from config import settings
from infra.logging import get_logger
from infra.metrics import operation_count, operation_duration

logger = get_logger(__name__)


class FactorialService:
    """Service for factorial calculations."""

    def __init__(self, repository: MathOperationRepository) -> None:
        """Initialize with repository dependency."""
        self.repository = repository

    def _calculate_factorial(self, n: int) -> int:
        """Calculate factorial using iterative approach."""
        if n <= 1:
            return 1

        # Check for potential overflow
        if n > 170:  # factorial(170) is close to sys.float_info.max
            raise ValueError("Number too large for factorial calculation")

        result = 1
        for i in range(2, n + 1):
            result *= i

        return result

    async def calculate_factorial(
        self, request: FactorialRequest
    ) -> FactorialResult:
        """Calculate factorial with logging and persistence."""
        start_time = time.time()

        try:
            # Validate input limits
            if request.n > settings.max_factorial_n:
                raise ValueError(f"N must be <= {settings.max_factorial_n}")

            # Calculate result
            result = self._calculate_factorial(request.n)

            # Create result object
            factorial_result = FactorialResult(n=request.n, result=result)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log the operation
            logger.info(
                "Factorial calculation completed",
                n=request.n,
                result=result,
                duration_ms=duration_ms,
            )

            # Create domain operation for persistence
            operation = MathOperation(
                operation_type="factorial",
                parameters={"n": request.n},
                result=result,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc),
            )

            # Save to repository
            await self.repository.save_operation(operation)

            # Update metrics
            operation_count.labels(
                operation_type="factorial", status="success"
            ).inc()
            operation_duration.labels(operation_type="factorial").observe(
                duration_ms / 1000
            )

            return factorial_result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "Factorial calculation failed",
                n=request.n,
                error=str(e),
                duration_ms=duration_ms,
            )

            operation_count.labels(
                operation_type="factorial", status="error"
            ).inc()
            raise
