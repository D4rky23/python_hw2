"""Domain models and value objects."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class UserRole(str, Enum):
    """User roles enum."""

    USER = "user"
    ADMIN = "admin"


@dataclass(frozen=True)
class User:
    """User domain model."""

    id: Optional[int]
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


@dataclass(frozen=True)
class UserCreate:
    """User creation request."""

    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


@dataclass(frozen=True)
class UserLogin:
    """User login request."""

    username: str
    password: str


@dataclass(frozen=True)
class Token:
    """JWT Token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


@dataclass(frozen=True)
class MathOperation:
    """Value object representing a mathematical operation."""

    operation_type: str
    parameters: Dict[str, Any]
    result: Any
    duration_ms: float
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "operation_type": self.operation_type,
            "parameters": self.parameters,
            "result": str(
                self.result
            ),  # Convert to string for JSON serialization
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class PowerRequest:
    """Value object for power operation request."""

    base: int
    exponent: int

    def __post_init__(self) -> None:
        """Validate the power request."""
        if not isinstance(self.base, int) or not isinstance(
            self.exponent, int
        ):
            raise ValueError("Base and exponent must be integers")
        if self.exponent < 0:
            raise ValueError("Exponent must be non-negative")


@dataclass(frozen=True)
class PowerResult:
    """Value object for power operation result."""

    base: int
    exponent: int
    result: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "base": self.base,
            "exponent": self.exponent,
            "result": self.result,
        }


@dataclass(frozen=True)
class FibonacciRequest:
    """Request for Fibonacci calculation."""

    n: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {"n": self.n}


@dataclass(frozen=True)
class FibonacciResult:
    """Value object for Fibonacci operation result."""

    n: int
    result: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "n": self.n,
            "result": self.result,
        }


@dataclass(frozen=True)
class FactorialRequest:
    """Value object for factorial operation request."""

    n: int

    def __post_init__(self) -> None:
        """Validate the factorial request."""
        if not isinstance(self.n, int):
            raise ValueError("N must be an integer")
        if self.n < 0:
            raise ValueError("N must be non-negative")


@dataclass(frozen=True)
class FactorialResult:
    """Value object for factorial operation result."""

    n: int
    result: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "n": self.n,
            "result": self.result,
        }
