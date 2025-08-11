#!/usr/bin/env python3
"""Setup script for the Math Service."""

import asyncio
import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    return result


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")
    run_command(f"{sys.executable} -m pip install -r requirements-dev.txt")


def setup_environment():
    """Set up environment files."""
    print("Setting up environment...")
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        env_example = Path(".env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
        else:
            env_content = """DATABASE_URL=sqlite:///./math_service.db
LOG_LEVEL=INFO
API_KEY_ENABLED=false
API_KEY=your-secret-api-key
HOST=0.0.0.0
PORT=8000
"""
            env_file.write_text(env_content)


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    run_command(f"{sys.executable} -m pytest src/tests/ -v")


def start_service():
    """Start the service."""
    print("Starting the Math Service...")
    print("Service will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Metrics at: http://localhost:8000/metrics")
    print("")
    print("Press Ctrl+C to stop the service")
    
    run_command(f"{sys.executable} -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")


def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Math Service Setup")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--all", action="store_true", help="Install, test, and start")
    
    args = parser.parse_args()
    
    if args.all or not any([args.install, args.test, args.start]):
        # Default behavior: do everything
        setup_environment()
        install_dependencies()
        run_tests()
        start_service()
    else:
        if args.install:
            setup_environment()
            install_dependencies()
        if args.test:
            run_tests()
        if args.start:
            start_service()


if __name__ == "__main__":
    main()
