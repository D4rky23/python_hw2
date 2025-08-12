"""Authentication service for user management."""

from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status

from domain.models import User, UserCreate, UserLogin, Token
from repositories.interfaces import UserRepository
from infra.auth import verify_password, create_access_token
from config import settings


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize with user repository."""
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if username already exists
        existing_user = await self.user_repository.get_user_by_username(
            user_data.username
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check if email already exists
        existing_email = await self.user_repository.get_user_by_email(
            user_data.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        user = await self.user_repository.create_user(user_data)
        return user

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with username and password."""
        user = await self.user_repository.get_user_by_username(
            login_data.username
        )

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(login_data.password, user.hashed_password):
            return None

        return user

    async def login_user(self, login_data: UserLogin) -> Token:
        """Login user and return JWT token."""
        user = await self.authenticate_user(login_data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role.value,
            },
            expires_delta=access_token_expires,
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60,  # Convert to seconds
        )

    async def get_current_user(self, username: str) -> Optional[User]:
        """Get current user by username."""
        user = await self.user_repository.get_user_by_username(username)
        if user and user.is_active:
            return user
        return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        user = await self.user_repository.get_user_by_id(user_id)
        if user and user.is_active:
            return user
        return None
