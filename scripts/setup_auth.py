"""Script to setup authentication system."""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infra.db import create_tables, AsyncSessionLocal
from repositories.sqlite_repo import SqliteUserRepository
from services.auth import AuthService
from domain.models import UserCreate, UserRole


async def create_admin_user():
    """Create default admin user."""
    async with AsyncSessionLocal() as session:
        user_repo = SqliteUserRepository(session)
        auth_service = AuthService(user_repo)

        # Check if admin already exists
        existing_admin = await user_repo.get_user_by_username("admin")
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@mathservice.com",
            password="admin123",
            full_name="System Administrator",
            role=UserRole.ADMIN,
        )

        try:
            admin_user = await auth_service.register_user(admin_data)
            print(f"Admin user created successfully!")
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"Role: {admin_user.role.value}")
        except Exception as e:
            print(f"Error creating admin user: {e}")


async def main():
    """Main setup function."""
    print("Setting up authentication system...")

    # Create database tables
    print("Creating database tables...")
    await create_tables()
    print("Database tables created!")

    # Create admin user
    print("Creating admin user...")
    await create_admin_user()

    print("Authentication setup completed!")
    print("\nYou can now:")
    print("1. Register new users via POST /api/v1/auth/register")
    print("2. Login via POST /api/v1/auth/login")
    print("3. Access protected endpoints with JWT token")
    print("\nDefault admin credentials:")
    print("Username: admin")
    print("Password: admin123")


if __name__ == "__main__":
    asyncio.run(main())
