"""Dependency injection and API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    APIKeyHeader,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from domain.models import User
from infra.db import get_db_session
from infra.auth import get_username_from_token
from repositories.sqlite_repo import SqliteRepository, SqliteUserRepository
from services.factorial import FactorialService
from services.fibonacci import FibonacciService
from services.power import PowerService
from services.auth import AuthService

# API Key security (legacy)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT Bearer token security
security = HTTPBearer(auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> None:
    """Verify API key if authentication is enabled."""
    if not settings.api_key_enabled:
        return

    if not api_key or api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


def get_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SqliteRepository:
    """Get repository instance."""
    return SqliteRepository(session)


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SqliteUserRepository:
    """Get user repository instance."""
    return SqliteUserRepository(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    user_repository: Annotated[
        SqliteUserRepository, Depends(get_user_repository)
    ] = None,
) -> User:
    """Get current user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = get_username_from_token(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(user_repository)
    user = await auth_service.get_current_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_auth_service(
    user_repository: Annotated[
        SqliteUserRepository, Depends(get_user_repository)
    ],
) -> AuthService:
    """Get authentication service instance."""
    return AuthService(user_repository)


def get_power_service(
    repository: Annotated[SqliteRepository, Depends(get_repository)],
) -> PowerService:
    """Get power service instance."""
    return PowerService(repository)


def get_fibonacci_service(
    repository: Annotated[SqliteRepository, Depends(get_repository)],
) -> FibonacciService:
    """Get Fibonacci service instance."""
    return FibonacciService(repository)


def get_factorial_service(
    repository: Annotated[SqliteRepository, Depends(get_repository)],
) -> FactorialService:
    """Get factorial service instance."""
    return FactorialService(repository)
