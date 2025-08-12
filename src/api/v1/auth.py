"""Authentication API endpoints."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

from api.deps import get_auth_service, get_current_user
from domain.models import User, UserCreate, UserLogin, Token, UserRole
from services.auth import AuthService

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


class UserCreateRequest(BaseModel):
    """Request model for user registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username",
        example="johndoe",
    )
    email: EmailStr = Field(
        ..., description="Email address", example="john@example.com"
    )
    password: str = Field(
        ..., min_length=6, description="Password", example="securepassword"
    )
    full_name: str = Field(
        None, max_length=100, description="Full name", example="John Doe"
    )
    role: UserRole = Field(UserRole.USER, description="User role")


class UserLoginRequest(BaseModel):
    """Request model for user login."""

    username: str = Field(..., description="Username", example="johndoe")
    password: str = Field(
        ..., description="Password", example="securepassword"
    )


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Is user active")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(
        None, description="Last update timestamp"
    )

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        """Create from domain user."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=(
                user.updated_at.isoformat() if user.updated_at else None
            ),
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account",
)
async def register_user(
    request: UserCreateRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Register a new user."""
    user_data = UserCreate(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
    )

    user = await auth_service.register_user(user_data)
    return UserResponse.from_domain(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and return access token",
)
async def login_user(
    request: UserLoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login user and return JWT token."""
    login_data = UserLogin(
        username=request.username, password=request.password
    )
    return await auth_service.login_user(login_data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information",
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user information."""
    return UserResponse.from_domain(current_user)


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List users",
    description="List all users (admin only)",
)
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    skip: int = 0,
    limit: int = 100,
) -> List[UserResponse]:
    """List users (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    users = await auth_service.user_repository.list_users(
        skip=skip, limit=limit
    )
    return [UserResponse.from_domain(user) for user in users]
