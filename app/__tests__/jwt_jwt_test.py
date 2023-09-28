"""
Test JWT Class.

This module contains tests for the JWT (JSON Web Token) handler in the application.
These tests focus on scenarios such as token retrieval, token caching, and error conditions.

Components:
- handler: Fixture to get a JWTHandler object for each test.
- token: Fixture to get a mock JWT token for each test.
- test_get_current_token: Test if a new token can be retrieved.
- test_get_token_uses_existing: Test if existing tokens are reused.
- test_get_token_refreshes_expired: Test if expired tokens are refreshed.
- test_get_expire_time_invalid_token_format: Test invalid token format.
- test_get_expire_time_invalid_token_payload_json_decode_error: Test invalid token payload.

Key Dependencies:
- pytest for test functionality.
- unittest.mock for mocking.
- datetime for date and time manipulations.
- JWTHandler from app.jwt.jwt for JWT operations.
- get_current_token from app.jwt.jwt for getting the current token.

Usage:
Run these tests to ensure that JWT handling logic in the application is correct.
Each test aims to validate a specific behavior of the JWT operations.

"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.__tests__.utils import generate_token
from app.jwt.jwt import JWTHandler, get_current_token


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
async def test_get_current_token(
    mock_fetch_new_jwt_token: AsyncMock, handler: JWTHandler, token: str
) -> None:
    """Test the get_current_token method without token."""
    mock_fetch_new_jwt_token.return_value = token
    obtained_token = await handler.get_token()

    assert obtained_token == token
    mock_fetch_new_jwt_token.assert_called_once()


@pytest.mark.asyncio
@patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
async def test_get_token_uses_existing(
    mock_fetch_new_jwt_token: AsyncMock, handler: JWTHandler, token: str
) -> None:
    """Test the get_token method with existing token."""
    handler.token = token
    handler.expire_time = datetime.utcnow() + timedelta(minutes=10)

    obtained_token = await handler.get_token()

    assert obtained_token == token
    mock_fetch_new_jwt_token.assert_not_called()


@pytest.mark.asyncio
@patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
async def test_get_token_refreshes_expired(
    mock_fetch_new_jwt_token: AsyncMock, handler: JWTHandler, token: str
) -> None:
    """Test the get_token method with expired token."""
    mock_fetch_new_jwt_token.return_value = token
    handler.token = "expired_token"
    handler.expire_time = datetime.utcnow() - timedelta(minutes=10)

    obtained_token = await handler.get_token()

    assert obtained_token == token
    mock_fetch_new_jwt_token.assert_called_once()


def test_get_expire_time_invalid_token_format(handler: JWTHandler) -> None:
    """Test if an exception is raised when the token format is invalid."""
    with pytest.raises(HTTPException) as excinfo:
        handler._get_expire_time("invalid.token")
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Invalid token format"


def test_get_expire_time_invalid_token_payload_json_decode_error(
    handler: JWTHandler,
) -> None:
    """Test if an exception is raised when JSON decoding fails."""
    with pytest.raises(HTTPException) as excinfo:
        handler._get_expire_time("header.8a.signature")
    assert excinfo.value.status_code == 500
    assert "Internal server error" in excinfo.value.detail


@pytest.mark.asyncio
@patch.object(JWTHandler, "get_token", new_callable=AsyncMock)
async def test_get_current_token_success(mock_get_token: AsyncMock) -> None:
    """Test successful retrieval of a JWT token."""
    mock_token = "mock_token_here"
    mock_get_token.return_value = mock_token

    result = await get_current_token()
    assert result == mock_token
    mock_get_token.assert_called_once()
