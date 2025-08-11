"""Power calculation service."""

import time
from datetime import datetime
from typing import Any, Dict

from domain.models import MathOperation, PowerRequest, PowerResult
from repositories.interfaces import MathOperationRepository
from config import settings
from infra.logging import get_logger
from infra.metrics import operation_count, operation_duration

logger = get_logger(__name__)


class PowerService:
    """Service for power calculations."""
    
    def __init__(self, repository: MathOperationRepository) -> None:
        """Initialize with repository dependency."""
        self.repository = repository
    
    async def calculate_power(self, request: PowerRequest) -> PowerResult:
        """Calculate base^exponent with logging and persistence."""
        start_time = time.time()
        
        try:
            # Validate input limits
            if request.base > settings.max_power_base:
                raise ValueError(f"Base must be <= {settings.max_power_base}")
            if request.exponent > settings.max_power_exponent:
                raise ValueError(f"Exponent must be <= {settings.max_power_exponent}")
            
            # Calculate result
            result = request.base ** request.exponent
            
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
            
            # Create domain operation for persistence
            operation = MathOperation(
                operation_type="power",
                parameters={"base": request.base, "exponent": request.exponent},
                result=result,
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
            )
            
            # Save to repository
            await self.repository.save_operation(operation)
            
            # Update metrics
            operation_count.labels(operation_type="power", status="success").inc()
            operation_duration.labels(operation_type="power").observe(duration_ms / 1000)
            
            return power_result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                "Power calculation failed",
                base=request.base,
                exponent=request.exponent,
                error=str(e),
                duration_ms=duration_ms,
            )
            
            operation_count.labels(operation_type="power", status="error").inc()
            raise
