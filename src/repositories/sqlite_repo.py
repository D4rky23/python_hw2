"""SQLite repository implementation."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
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

from domain.models import MathOperation, User, UserCreate, UserRole
from repositories.interfaces import MathOperationRepository, UserRepository
from infra.auth import get_password_hash


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
    timestamp = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

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


class UserModel(Base):
    """SQLAlchemy model for users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default=UserRole.USER.value)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(DateTime, nullable=True)

    def to_domain(self) -> User:
        """Convert to domain model."""
        return User(
            id=self.id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            role=UserRole(self.role),
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain_create(
        cls, user_data: UserCreate, hashed_password: str
    ) -> "UserModel":
        """Create from domain create model."""
        now = datetime.now(timezone.utc)
        return cls(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role.value,
            is_active=True,
            created_at=now,
        )


class SqliteRepository(MathOperationRepository):
    """SQLite implementation of the math operation repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self.session = session

    async def save_operation(self, operation: MathOperation) -> None:
        """Save a math operation to SQLite."""
        try:
            model = MathOperationModel.from_domain(operation)
            self.session.add(model)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

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


class SqliteUserRepository(UserRepository):
    """SQLite implementation of the user repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            # Hash password
            hashed_password = get_password_hash(user_data.password)

            # Create user model
            user_model = UserModel.from_domain_create(
                user_data, hashed_password
            )

            # Save to database
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)

            return user_model.to_domain()
        except Exception:
            await self.session.rollback()
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model:
            return user_model.to_domain()
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model:
            return user_model.to_domain()
        return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model:
            return user_model.to_domain()
        return None

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            # Update fields
            for key, value in kwargs.items():
                if hasattr(user_model, key):
                    setattr(user_model, key, value)

            user_model.updated_at = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(user_model)

            return user_model.to_domain()
        except Exception:
            await self.session.rollback()
            raise

    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return False

            await self.session.delete(user_model)
            await self.session.commit()

            return True
        except Exception:
            await self.session.rollback()
            raise

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users."""
        stmt = (
            select(UserModel)
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()

        return [user_model.to_domain() for user_model in user_models]
