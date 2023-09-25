"""Test the risk details utility functions."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from httpx import Response

from app.utils.risk_utils import fetch_risk_details


@pytest.mark.asyncio
async def test_fetch_risk_details_success() -> None:
    """Test the successful fetch of the risk details."""
    fake_resp = {"case_id": "some_id", "risk": 5}
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"
    jwt_token = "some_token"

    headers = {"accept": "application/json", "authorization": f"Bearer {jwt_token}"}
    url = f"http://test.url?address={test_address}&chain=eth"

    with patch("app.config.config.cfg.blockmate_api_url", new="http://test.url"), patch(
        "httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = Response(200, json=fake_resp)

        result = await fetch_risk_details(test_address, jwt_token)
        assert result == fake_resp

        mock_get.assert_called_once_with(url, headers=headers)


@pytest.mark.asyncio
async def test_fetch_risk_details_fail() -> None:
    """Test the failure to fetch the risk details."""
    fake_resp = {"error": "unable to authenticate"}
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"
    jwt_token = "some_token"

    headers = {"accept": "application/json", "authorization": f"Bearer {jwt_token}"}
    url = f"http://test.url?address={test_address}&chain=eth"

    with patch("app.config.config.cfg.blockmate_api_url", new="http://test.url"), patch(
        "httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = Response(401, json=fake_resp)

        with pytest.raises(HTTPException) as excinfo:
            await fetch_risk_details(test_address, jwt_token)

        assert excinfo.value.status_code == 502
        assert excinfo.value.detail == f"Unable to fetch risk details: {fake_resp}"

        mock_get.assert_called_once_with(url, headers=headers)
