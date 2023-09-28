"""
Test Check Route.

This module contains tests for the `/check` route in the application.
The tests cover various scenarios, such as a successful check of an Ethereum address, cache hit,
missing address, and different types of exceptions.

Components:
- client: Fixture to get the FastAPI test client.
- patched_config: Fixture to patch the configuration values.
- test_check_ethereum_address_success: Tests a successful check of an Ethereum address.
- test_check_ethereum_address_cached: Tests the behavior when the
  Ethereum address data is already cached.
- test_check_ethereum_address_failed: Tests the behavior when required address field is missing.
- test_check_ethereum_address_http_exception: Tests the HTTPException
  scenario for fetch_risk_details.
- test_check_ethereum_address_token_exception: Tests the HTTPException
  scenario for get_current_token.

Key Dependencies:
- pytest for test functionality.
- unittest.mock for mocking.
- datetime for date and time manipulations.
- FastAPI for the web application.
- TestClient from fastapi.testclient for API testing.

Usage:
Run these tests to ensure that the `/check` route works as expected under various conditions.
Each test validates a specific aspect of the route's behavior.

"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.__tests__.utils import generate_token
from app.main import app
from app.models.check_model import CheckEndpointResponse
from app.models.risk_model import Details, OwnCategory, RiskDetailsResponse


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Get the test client.

    :return: The test client.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def patched_config() -> None:
    """Patch the config for rate limiting."""
    with patch("app.middleware.rate_limiter.cfg.rate_limit", 100), patch(
        "app.middleware.rate_limiter.cfg.rate_limit_time_window", 60
    ):
        yield


@pytest.mark.asyncio
@pytest.mark.usefixtures("patched_config")
@patch("app.routes.check.fetch_risk_details", new_callable=AsyncMock)
@patch("app.routes.check.get_current_token", new_callable=AsyncMock)
async def test_check_ethereum_address_success(
    mock_get_current_token: AsyncMock,
    mock_fetch_risk_details: AsyncMock,
    client: TestClient,
) -> None:
    """Test the successful check of an Ethereum address."""
    token = generate_token(datetime.utcnow() + timedelta(hours=1))
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"

    mock_get_current_token.return_value = token
    mock_fetch_risk_details.return_value = RiskDetailsResponse(
        case_id="1",
        request_datetime="time1",
        response_datetime="time2",
        chain="eth",
        address="addr1",
        name="Binance 6",
        category_name="Exchange",
        risk=5,
        details=Details(
            own_categories=[
                OwnCategory(
                    address="addr1", name="Binance 6", category_name="Exchange", risk=5
                )
            ],
            source_of_funds_categories=[],
        ),
    )

    response = client.get(f"/check?address={test_address}")

    assert response.status_code == 200
    assert (
        response.json()
        == CheckEndpointResponse(category_names=["Exchange"]).model_dump()
    )
    mock_fetch_risk_details.assert_called_once_with(test_address, token)


@pytest.mark.asyncio
@pytest.mark.usefixtures("patched_config")
@patch("app.routes.check.fetch_risk_details", new_callable=AsyncMock)
@patch("app.routes.check.get_current_token", new_callable=AsyncMock)
async def test_check_ethereum_address_cached(
    mock_get_current_token: AsyncMock,
    mock_fetch_risk_details: AsyncMock,
    client: TestClient,
) -> None:
    """Test the successful check of an Ethereum address from cache."""
    token = generate_token(datetime.utcnow() + timedelta(hours=1))
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"

    mock_get_current_token.return_value = token

    response = client.get(f"/check?address={test_address}")

    assert response.status_code == 200
    assert (
        response.json()
        == CheckEndpointResponse(category_names=["Exchange"]).model_dump()
    )

    mock_fetch_risk_details.assert_not_called()


@pytest.mark.usefixtures("patched_config")
def test_check_ethereum_address_failed(client) -> None:
    """Test the failed check of an Ethereum address."""
    response = client.get("/check")
    assert response.status_code == 422

    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["query", "address"]
    assert data["detail"][0]["msg"] == "Field required"


@pytest.mark.asyncio
@pytest.mark.usefixtures("patched_config")
@patch("app.routes.check.fetch_risk_details", new_callable=AsyncMock)
@patch("app.routes.check.get_current_token", new_callable=AsyncMock)
async def test_check_ethereum_address_http_exception(
    mock_get_current_token: AsyncMock,
    mock_fetch_risk_details: AsyncMock,
    client: TestClient,
) -> None:
    """Test the HTTPException raised by fetch_risk_details."""
    token = generate_token(datetime.utcnow() + timedelta(hours=1))
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A65"

    mock_get_current_token.return_value = token
    mock_fetch_risk_details.side_effect = HTTPException(
        status_code=500, detail="Server Error"
    )

    response = client.get(f"/check?address={test_address}")

    assert response.status_code == 500
    assert response.json() == {"detail": "Server Error"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("patched_config")
@patch("app.routes.check.get_current_token", new_callable=AsyncMock)
async def test_check_ethereum_address_token_exception(
    mock_get_current_token: AsyncMock, client: TestClient
) -> None:
    """Test the HTTPException raised by get_current_token."""
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A65"

    mock_get_current_token.side_effect = HTTPException(
        status_code=500, detail="Invalid token format"
    )

    response = client.get(f"/check?address={test_address}")

    assert response.status_code == 500
    assert response.json() == {"detail": "Invalid token format"}
