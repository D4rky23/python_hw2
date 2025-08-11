"""Dependency injection and API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from infra.db import get_db_session
from repositories.sqlite_repo import SqliteRepository
from services.factorial import FactorialService
from services.fibonacci import FibonacciService
from services.power import PowerService

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


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
