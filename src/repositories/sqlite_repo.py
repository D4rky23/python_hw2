"""SQLite repository implementation."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from domain.models import MathOperation
from repositories.interfaces import MathOperationRepository


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class MathOperationModel(Base):
    """SQLAlchemy model for math operations."""

    __tablename__ = "math_operations"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String(50), nullable=False, index=True)
    parameters = Column(Text, nullable=False)  # JSON string
    result = Column(Text, nullable=False)  # String representation
    duration_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_domain(self) -> MathOperation:
        """Convert to domain model."""
        return MathOperation(
            operation_type=self.operation_type,
            parameters=json.loads(self.parameters),
            result=self.result,
            duration_ms=self.duration_ms,
            timestamp=self.timestamp,
        )

    @classmethod
    def from_domain(cls, operation: MathOperation) -> "MathOperationModel":
        """Create from domain model."""
        return cls(
            operation_type=operation.operation_type,
            parameters=json.dumps(operation.parameters),
            result=str(operation.result),
            duration_ms=operation.duration_ms,
            timestamp=operation.timestamp,
        )


class SqliteRepository(MathOperationRepository):
    """SQLite implementation of the math operation repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self.session = session

    async def save_operation(self, operation: MathOperation) -> None:
        """Save a math operation to SQLite."""
        model = MathOperationModel.from_domain(operation)
        self.session.add(model)
        await self.session.commit()

    async def get_operations(
        self, operation_type: Optional[str] = None, limit: int = 100
    ) -> List[MathOperation]:
        """Retrieve math operations from SQLite."""
        stmt = select(MathOperationModel)

        if operation_type:
            stmt = stmt.where(
                MathOperationModel.operation_type == operation_type
            )

        stmt = stmt.order_by(MathOperationModel.timestamp.desc()).limit(limit)

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [model.to_domain() for model in models]

    async def get_operation_count(
        self, operation_type: Optional[str] = None
    ) -> int:
        """Get count of operations."""
        stmt = select(func.count(MathOperationModel.id))

        if operation_type:
            stmt = stmt.where(
                MathOperationModel.operation_type == operation_type
            )

        result = await self.session.execute(stmt)
        return result.scalar() or 0
