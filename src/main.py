"""FastAPI application factory and main entry point."""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from api.v1 import v1_router
from config import settings
from infra import (
    configure_logging,
    create_tables,
    get_logger,
    get_metrics,
    request_count,
    request_duration,
)


# Configure logging early
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Math Service API")
    await create_tables()
    logger.info("Database tables created")

    yield

    # Shutdown
    logger.info("Shutting down Math Service API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="A production-ready microservice for mathematical operations",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8080",
        ],  # Configure for specific frontend URLs
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    )

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests with timing."""
        import time

        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        logger.info(
            "HTTP request processed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration_seconds=duration,
        )

        # Update metrics
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).inc()

        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)

        return response

    # Include API routers
    app.include_router(v1_router)

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "math-service"}

    # Metrics endpoint
    @app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
    async def metrics() -> str:
        """Prometheus metrics endpoint."""
        return get_metrics()

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
