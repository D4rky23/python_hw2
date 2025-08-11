"""API v1 endpoints."""

from fastapi import APIRouter

from .factorial import router as factorial_router
from .fibonacci import router as fibonacci_router
from .power import router as power_router

# Create v1 router
v1_router = APIRouter(prefix="/api")

# Include operation routers
v1_router.include_router(power_router)
v1_router.include_router(fibonacci_router)
v1_router.include_router(factorial_router)
