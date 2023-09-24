"""Utility functions for JWT."""
import httpx

from app.config.config import cfg


async def fetch_new_jwt_token() -> str:
    """Fetch a new JWT token from the auth service."""
    headers = {"accept": "application/json", "X-API-KEY": cfg.project_token}

    async with httpx.AsyncClient() as client:
        response = await client.get(cfg.jwt_url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get("token")
