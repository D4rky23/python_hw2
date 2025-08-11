# Math Service

A production-ready microservice for mathematical operations built with FastAPI, following Clean Architecture and Domain-Driven Design principles.

## 🏗️ Architecture

This service implements Clean Architecture with the following layers:

- **API Layer** (FastAPI routers) - Entry point with validation and authentication
- **Application Layer** (Services) - Use cases and business logic orchestration
- **Domain Layer** (Entities/Value Objects) - Pure business rules
- **Infrastructure Layer** (Repositories/External) - Data persistence and external concerns

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run
docker compose up --build
```

## 📋 API Endpoints

- `POST /v1/power` - Calculate base^exponent
- `GET /v1/fibonacci/{n}` - Calculate nth Fibonacci number
- `POST /v1/factorial` - Calculate factorial of a number
- `/docs` - Interactive API documentation
- `/metrics` - Prometheus metrics

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## 📊 Features

- ✅ Clean Architecture with dependency injection
- ✅ Input validation with Pydantic
- ✅ SQLite persistence with SQLAlchemy
- ✅ Structured logging
- ✅ Prometheus metrics
- ✅ OpenAPI documentation
- ✅ Docker containerization
- ✅ Comprehensive testing

## 🔧 Configuration

Configuration is handled via environment variables:

- `DATABASE_URL` - SQLite database path (default: sqlite:///./math_service.db)
- `LOG_LEVEL` - Logging level (default: INFO)
- `API_KEY_ENABLED` - Enable API key authentication (default: False)

## 📈 Observability

- Structured logs in JSON format
- Prometheus metrics at `/metrics`
- Request/response logging with duration tracking
- Database operation metrics
