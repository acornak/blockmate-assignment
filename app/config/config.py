"""Centralized configuration for the application."""
import os

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration."""

    blockmate_api_url: str
    project_token: str
    jwt_url: str
    rate_limit: str

    class Config:
        """Configuration for the AppConfig class."""

        environment = os.getenv("ENVIRONMENT", "dev")
        env_file = f".env.{environment}"
