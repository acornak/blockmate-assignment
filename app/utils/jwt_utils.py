"""
Utility functions for JWT.

This module contains utility functions for managing JSON Web Tokens (JWT) in the application.
The following features are covered:

1. Token Retrieval: Fetches a new JWT token from the Blockmate authentication service.

Key Considerations:
- The Blockmate API key is fetched from the application's environment configuration.
- httpx.AsyncClient is used for making asynchronous HTTP requests.

Dependencies:
- httpx for making the HTTP calls.
- app.config for application configuration parameters.

"""
import httpx
from fastapi import HTTPException

from app.config.config import cfg


async def fetch_new_jwt_token() -> str:
    """Fetch a new JWT token from the auth service."""
    headers = {"accept": "application/json", "X-API-KEY": cfg.project_token}

    async with httpx.AsyncClient() as client:
        response = await client.get(cfg.jwt_url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get("token")
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch JWT token: {response.json()}",
        )
