"""
Centralized configuration for the application.

This module holds the AppConfig class responsible for centralizing
the application's configuration settings. It utilizes pydantic for validation
and type checking, and python-dotenv for environment variable management.

Components:
- AppConfig: Pydantic class for app-wide configuration settings.

Key Variables:
- blockmate_api_url: URL for BlockMate API
- project_token: Project token for the BlockMate API
- jwt_url: URL for JWT service
- rate_limit_time_window: Time window for rate limiting, in seconds
- rate_limit: Number of requests allowed per time window

Dependencies:
- os for environment variables
- dotenv for .env file parsing
- pydantic for type checking and validation

"""
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

environment = os.getenv("ENVIRONMENT", "dev")
load_dotenv(f".env.{environment}")


class AppConfig(BaseSettings):
    """
    Centralized configuration for the application using Pydantic.

    This class holds variables that are critical for the application setup
    and are loaded from .env files.
    It uses pydantic for type checking and validation.

    Variables:
    - blockmate_api_url: URL for the BlockMate API
    - project_token: API token for BlockMate
    - jwt_url: URL for the JWT service
    - rate_limit_time_window: Time window for rate limiting in seconds
    - rate_limit: Number of allowed requests within the rate limit time window
    """

    blockmate_api_url: str
    project_token: str
    jwt_url: str
    rate_limit_time_window: int
    rate_limit: int


cfg = AppConfig()
