"""Centralized configuration for the application."""
import os

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration.

    blockmate_api_url: URL for the BlockMate API.
    project_token: Token for the BlockMate API.
    jwt_url: URL for the JWT service.
    rate_limit_time_window: Time window for the rate limiter in seconds.
    rate_limit: Number of requests allowed per time window for the rate limiter.
    """

    blockmate_api_url: str
    project_token: str
    jwt_url: str
    rate_limit_time_window: int
    rate_limit: int

    class Config:
        """Configuration for the AppConfig class."""

        environment = os.getenv("ENVIRONMENT", "dev")
        env_file = f".env.{environment}"


cfg = AppConfig()
