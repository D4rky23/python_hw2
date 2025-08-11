"""Repository interfaces (ports) for the application."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models import MathOperation


class MathOperationRepository(ABC):
    """Abstract repository for storing math operations."""

    @abstractmethod
    async def save_operation(self, operation: MathOperation) -> None:
        """Save a math operation to storage."""
        pass

    @abstractmethod
    async def get_operations(
        self, operation_type: Optional[str] = None, limit: int = 100
    ) -> List[MathOperation]:
        """Retrieve math operations from storage."""
        pass

    @abstractmethod
    async def get_operation_count(
        self, operation_type: Optional[str] = None
    ) -> int:
        """Get count of operations."""
        pass
