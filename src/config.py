"""Configuration management using Pydantic Settings."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    database_url: str = Field(
        default="sqlite:///./math_service.db",
        description="Database connection URL",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )

    # API
    api_title: str = Field(default="Math Service API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_key_enabled: bool = Field(
        default=False, description="Enable API key authentication"
    )
    api_key: str = Field(
        default="your-secret-api-key", description="API key for authentication"
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Computation limits
    max_fibonacci_n: int = Field(
        default=10000, description="Maximum value for Fibonacci computation"
    )
    max_factorial_n: int = Field(
        default=5000, description="Maximum value for factorial computation"
    )
    max_power_base: int = Field(
        default=1000, description="Maximum base value for power computation"
    )
    max_power_exponent: int = Field(
        default=1000,
        description="Maximum exponent value for power computation",
    )

    # Redis Configuration
    redis_enabled: bool = Field(
        default=True, description="Enable Redis caching"
    )
    redis_url: str = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )
    redis_password: str = Field(
        default="", description="Redis password"
    )
    redis_db: int = Field(
        default=0, description="Redis database number"
    )
    redis_ttl: int = Field(
        default=3600, description="Cache TTL in seconds"
    )

    # Kafka Configuration
    kafka_enabled: bool = Field(
        default=True, description="Enable Kafka messaging"
    )
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092", description="Kafka bootstrap servers"
    )
    kafka_topic: str = Field(
        default="math-operations", description="Kafka topic for events"
    )
    kafka_group_id: str = Field(
        default="math-service", description="Kafka consumer group ID"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
