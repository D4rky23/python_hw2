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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
