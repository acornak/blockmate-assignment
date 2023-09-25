"""Test the JWT utility functions."""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response

from app.utils.jwt_utils import fetch_new_jwt_token


@pytest.mark.asyncio
async def test_fetch_new_jwt_token_success() -> None:
    """Test the successful fetch of a new JWT token."""
    fake_token = "fake_token"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Response(200, json={"token": fake_token})

        result = await fetch_new_jwt_token()
        assert result == fake_token


@pytest.mark.asyncio
async def test_fetch_new_jwt_token_failure() -> None:
    """Test the failure to fetch a new JWT token."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Response(400, json={"error": "something went wrong"})

        result = await fetch_new_jwt_token()
        assert result is None
