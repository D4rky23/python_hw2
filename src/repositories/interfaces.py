"""Repository interfaces (ports) for the application."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models import MathOperation, User, UserCreate


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


class UserRepository(ABC):
    """Abstract repository for user management."""

    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        pass

    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users."""
        pass
