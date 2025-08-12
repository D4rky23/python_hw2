# Math Service

A production-ready microservice for mathematical operations built with FastAPI, featuring JWT authentication, following Clean Architecture and Domain-Driven Design principles.

## Architecture

This service implements Clean Architecture with the following layers:

- **API Layer** (FastAPI routers) - Entry point with validation and JWT authentication
- **Application Layer** (Services) - Use cases and business logic orchestration
- **Domain Layer** (Entities/Value Objects) - Pure business rules
- **Infrastructure Layer** (Repositories/External) - Data persistence and external concerns

## Authentication

The service implements JWT-based authentication with username/password login:

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user information
- `GET /api/v1/auth/users` - List all users (admin only)

### Default Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

### Using Authentication
1. Login to get JWT token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

2. Use token in subsequent requests:
```bash
curl -X POST http://localhost:8000/api/v1/factorial/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"n":5}'
```

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create admin user
python scripts/create_admin.py

# Run the service
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run
docker compose up --build
```

## API Endpoints

### Mathematical Operations (JWT Required)
- `POST /api/v1/power/` - Calculate base^exponent
- `GET /api/v1/fibonacci/{n}` - Calculate nth Fibonacci number
- `POST /api/v1/factorial/` - Calculate factorial of a number

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/users` - List users (admin only)

### Public Endpoints
- `/health` - Health check
- `/docs` - Interactive API documentation
- `/metrics` - Prometheus metrics

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# End-to-end testing with Playwright
# The service includes comprehensive Playwright tests for all endpoints
# All endpoints have been tested and verified working:
# Health endpoint: {"status": "healthy", "service": "math-service"}
# Factorial endpoint: {"n": 5, "result": 120}
# Power endpoint: {"base": 4, "exponent": 2, "result": 16}
# Fibonacci endpoint: {"n": 8, "result": 21}
# Authentication endpoints: Login, register, user management
# Metrics endpoint: Prometheus metrics with full statistics
```

## Features

- Clean Architecture with dependency injection
- JWT Authentication with username/password
- User management with role-based access control
- Input validation with Pydantic
- SQLite persistence with SQLAlchemy
- Structured logging
- Prometheus metrics
- OpenAPI documentation
- Docker containerization with Kafka messaging
- Comprehensive testing (Unit, Integration, E2E with Playwright)
- Redis caching layer
- Event-driven architecture with Kafka
- Production-ready monitoring and observability

## Configuration

Configuration is handled via environment variables:

- `DATABASE_URL` - SQLite database path (default: sqlite:///./src/math_service.db)
- `LOG_LEVEL` - Logging level (default: INFO)
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `JWT_ALGORITHM` - Algorithm for JWT signing (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration (default: 30)

## Development Tools

The project includes useful development utilities:

- `scripts/create_admin.py` - Create admin user for authentication
- `scripts/debug.py` - Database connectivity and environment debugging tool
- `scripts/quick_test.py` - Quick API endpoint testing utility
- `scripts/setup_auth.py` - Authentication system setup

## Observability

- Structured logs in JSON format
- Prometheus metrics at `/metrics`
- Request/response logging with duration tracking
- Database operation metrics

## Docker Troubleshooting

If you encounter the "ModuleNotFoundError: No module named 'api'" error when running the Docker container, this is due to Python import path issues. Here's how to fix it:

### Solution 1: Use docker-compose (Recommended)
The docker-compose.yml file has been properly configured with all dependencies:

```bash
docker-compose up --build
```

This starts the full stack:
- Math Service API (port 8000)
- Redis cache (port 6379)
- Kafka message broker (port 9092)
- Zookeeper (port 2181)

### Solution 2: Manual Fix
If you want to fix the original Dockerfile, ensure these environment variables are set:

```dockerfile
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
```

And the CMD should be:
```dockerfile
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database Location Notes
- **Development**: Database stored in `src/math_service.db`  
- **Docker**: Database stored in `data/math_service.db` (volume mounted)
- **Configuration**: Paths are relative to project root

### Verification
Once the container is running, test the endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test authenticated endpoint
curl -X POST http://localhost:8000/api/v1/factorial/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"n":5}'

# API documentation  
curl http://localhost:8000/docs

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Security

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Role-based access control (USER/ADMIN)
- Protected mathematical endpoints
- Public health and documentation endpoints

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `hashed_password` - Bcrypt hashed password
- `full_name` - Optional full name
- `role` - User role (USER/ADMIN)
- `is_active` - Account status
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp

### Math Operations Table
- `id` - Primary key
- `operation_type` - Type of mathematical operation
- `parameters` - JSON parameters
- `result` - Operation result
- `duration_ms` - Execution time
- `timestamp` - Operation timestamp
