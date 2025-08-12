import asyncio
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), "src")
sys.path.insert(0, src_dir)

from repositories.sqlite_repo import SqliteUserRepository
from services.auth import AuthService
from domain.models import UserCreate, UserRole
from infra.db import AsyncSessionLocal


async def create_admin():
    session = AsyncSessionLocal()
    try:
        user_repo = SqliteUserRepository(session)
        auth_service = AuthService(user_repo)

        # Check if admin exists
        existing = await user_repo.get_user_by_username("admin")
        if existing:
            print("Admin user already exists!")
            return

        # Create admin
        admin_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",
            full_name="Admin User",
            role=UserRole.ADMIN,
        )

        user = await auth_service.register_user(admin_data)
        print(f"Admin created successfully: {user.username}")

    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(create_admin())
