"""
Test JWT Utility Functions.

This module contains tests for the JWT utility functions in the application.
The tests cover various scenarios such as successful and unsuccessful fetch of a new JWT token.

Components:
- test_fetch_new_jwt_token_success: Tests the successful fetch of a new JWT token.
- test_fetch_new_jwt_token_failure: Tests the failure in fetching a new JWT token.

Key Dependencies:
- pytest for test functionality.
- unittest.mock for mocking.
- httpx for making HTTP requests.
- fetch_new_jwt_token from app.utils.jwt_utils as the utility function being tested.

Usage:
Run these tests to ensure that the JWT utility functions work as expected under various conditions.
Each test validates a specific aspect of the function's behavior.

"""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response

from app.utils.jwt_utils import fetch_new_jwt_token


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_new_jwt_token_success(mock_get: AsyncMock) -> None:
    """Test the successful fetch of a new JWT token."""
    fake_token = "fake_token"

    mock_get.return_value = Response(200, json={"token": fake_token})

    result = await fetch_new_jwt_token()
    assert result == fake_token


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_new_jwt_token_failure(mock_get: AsyncMock) -> None:
    """Test the failure to fetch a new JWT token."""
    mock_get.return_value = Response(400, json={"error": "something went wrong"})

    result = await fetch_new_jwt_token()
    assert result is None
