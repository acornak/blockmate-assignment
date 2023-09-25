"""Test the JWT class."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from app.__tests__.utils import generate_token
from app.jwt.jwt import JWTHandler


@pytest.fixture
def handler() -> JWTHandler:
    """
    Get the JWT handler.

    :return: The JWT handler.
    """
    return JWTHandler()


@pytest.fixture
def token() -> str:
    """
    Get a JWT token.

    :return: The JWT token.
    """
    return generate_token(datetime.utcnow() + timedelta(hours=1))


@pytest.mark.asyncio
@patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
async def test_get_current_token(mock_fetch_new_jwt_token, handler, token):
    """Test the get_current_token method without token."""
    mock_fetch_new_jwt_token.return_value = token
    obtained_token = await handler.get_token()

    assert obtained_token == token
    mock_fetch_new_jwt_token.assert_called_once()


@pytest.mark.asyncio
@patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
async def test_get_token_uses_existing(mock_fetch_new_jwt_token, handler, token):
    """Test the get_token method with existing token."""
    handler.token = token
    handler.expire_time = datetime.utcnow() + timedelta(minutes=10)

    obtained_token = await handler.get_token()

    assert obtained_token == token
    mock_fetch_new_jwt_token.assert_not_called()


@pytest.mark.asyncio
@patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
async def test_get_token_refreshes_expired(mock_fetch_new_jwt_token, handler, token):
    """Test the get_token method with expired token."""
    mock_fetch_new_jwt_token.return_value = token
    handler.token = "expired_token"
    handler.expire_time = datetime.utcnow() - timedelta(minutes=10)

    obtained_token = await handler.get_token()

    assert obtained_token == token
    mock_fetch_new_jwt_token.assert_called_once()
