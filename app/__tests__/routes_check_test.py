"""Test the check route."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.__tests__.utils import generate_token
from app.config.config import cfg
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Get the test client.

    :return: The test client.
    """
    return TestClient(app)


@pytest.mark.asyncio
async def test_check_ethereum_address_success(client) -> None:
    """Test the successful check of an Ethereum address."""
    with patch("app.routes.check.cfg.rate_limit", 100), patch(
        "app.routes.check.cfg.rate_limit_time_window", 60
    ):
        token = generate_token(datetime.utcnow() + timedelta(hours=1))
        test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"

        with patch(
            "app.routes.check.fetch_risk_details", new_callable=AsyncMock
        ) as mock_fetch_risk_details, patch(
            "app.routes.check.get_current_token", new_callable=AsyncMock
        ) as mock_get_current_token:
            mock_get_current_token.return_value = token
            mock_fetch_risk_details.return_value = {"some": "value"}

            response = client.get(f"/check?address={test_address}")

            assert response.status_code == 200
            assert response.json() == {
                "ethereum_address": test_address,
                "blockmate_token": cfg.project_token,
            }
            mock_fetch_risk_details.assert_called_once_with(test_address, token)


def test_check_ethereum_address_failed(client) -> None:
    """Test the failed check of an Ethereum address."""
    with patch("app.routes.check.cfg.rate_limit", 100), patch(
        "app.routes.check.cfg.rate_limit_time_window", 60
    ):
        response = client.get("/check")
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        assert data["detail"][0]["type"] == "missing"
        assert data["detail"][0]["loc"] == ["query", "address"]
        assert data["detail"][0]["msg"] == "Field required"
