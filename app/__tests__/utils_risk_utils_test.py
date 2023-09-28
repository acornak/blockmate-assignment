"""
Test Risk Details Utility Functions.

This module contains tests for the risk details utility functions in the application.
The tests cover various scenarios such as successful and unsuccessful fetch
of risk details and deduplication of risk categories.

Components:
- test_fetch_risk_details_success: Tests the successful fetch of the risk details.
- test_fetch_risk_details_fail: Tests the failure to fetch the risk details due to authentication.
- test_fetch_risk_details_httpx_exception: Tests the failure to fetch
  the risk details due to an HTTPX Exception.
- test_deduplicate_categories: Tests the deduplication of risk categories.

Key Dependencies:
- pytest for test functionality.
- unittest.mock for mocking.
- fastapi for HTTP exceptions.
- httpx for making HTTP requests.
- RiskDetailsResponse, Details, OwnCategory from app.models.risk_model.
- deduplicate_categories, fetch_risk_details from app.utils.risk_utils.

Usage:
Run these tests to ensure that the risk details utility functions
work as expected under various conditions.
Each test validates a specific aspect of the function's behavior.

"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from httpx import RequestError, Response

from app.models.risk_model import Details, OwnCategory, RiskDetailsResponse
from app.utils.risk_utils import deduplicate_categories, fetch_risk_details


@pytest.fixture(scope="function")
def patched_config() -> None:
    """
    Patch the config.

    :return: None.
    """
    with patch("app.config.config.cfg.blockmate_api_url", new="http://test.url"):
        yield


@pytest.mark.asyncio
@pytest.mark.usefixtures("patched_config")
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_risk_details_success(mock_get: AsyncMock) -> None:
    """
    Test the successful fetch of the risk details.

    :param mock_get: Mocked HTTP GET request.
    """
    fake_resp = {
        "case_id": "703c0074-698a-4f2a-88a3-5a48a08047b2",
        "request_datetime": "2023-09-24T15:47:02Z",
        "response_datetime": "2023-09-24T15:47:02Z",
        "chain": "eth",
        "address": "0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
        "name": "Binance 6",
        "category_name": "Exchange",
        "risk": 5,
        "details": {
            "own_categories": [
                {
                    "address": "0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
                    "name": "Binance 6",
                    "category_name": "Exchange",
                    "risk": 5,
                }
            ],
            "source_of_funds_categories": [],
        },
    }

    response_model = RiskDetailsResponse.model_validate(fake_resp)

    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"
    jwt_token = "some_token"

    headers = {"accept": "application/json", "authorization": f"Bearer {jwt_token}"}
    url = f"http://test.url?address={test_address}&chain=eth"

    mock_get.return_value = Response(200, json=fake_resp)

    result = await fetch_risk_details(test_address, jwt_token)
    assert result == response_model

    mock_get.assert_called_once_with(url, headers=headers)


@pytest.mark.asyncio
@pytest.mark.usefixtures("patched_config")
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_risk_details_fail(mock_get: AsyncMock) -> None:
    """
    Test the failure to fetch the risk details.

    :param mock_get: Mocked HTTP GET request.
    """
    fake_resp = {"error": "unable to authenticate"}
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"
    jwt_token = "some_token"

    headers = {"accept": "application/json", "authorization": f"Bearer {jwt_token}"}
    url = f"http://test.url?address={test_address}&chain=eth"

    mock_get.return_value = Response(401, json=fake_resp)

    with pytest.raises(HTTPException) as excinfo:
        await fetch_risk_details(test_address, jwt_token)

    assert excinfo.value.status_code == 502
    assert excinfo.value.detail == f"Unable to fetch risk details: {fake_resp}"

    mock_get.assert_called_once_with(url, headers=headers)


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_risk_details_httpx_exception(mock_get: AsyncMock) -> None:
    """
    Test the failure to fetch the risk details due to the HTTPX Exception.

    :param mock_get: Mocked HTTP GET request.
    """
    test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"
    jwt_token = "some_token"

    mock_get.side_effect = RequestError("Dummy request error")

    with pytest.raises(HTTPException) as excinfo:
        await fetch_risk_details(test_address, jwt_token)

    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Unable to fetch risk details: Internal server error"


@pytest.mark.parametrize(
    "input_risk_details, expected_categories",
    [
        (
            RiskDetailsResponse(
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
                            address="addr1",
                            name="Binance 6",
                            category_name="Exchange",
                            risk=5,
                        )
                    ],
                    source_of_funds_categories=[],
                ),
            ),
            ["Exchange"],
        ),
        (
            RiskDetailsResponse(
                case_id="2",
                request_datetime="time3",
                response_datetime="time4",
                chain="eth",
                address="addr2",
                name="Kraken",
                category_name="Exchange",
                risk=6,
                details=Details(
                    own_categories=[
                        OwnCategory(
                            address="addr2",
                            name="Kraken",
                            category_name="Exchange",
                            risk=6,
                        ),
                        OwnCategory(
                            address="addr2",
                            name="Kraken",
                            category_name="High Risk",
                            risk=6,
                        ),
                    ],
                    source_of_funds_categories=[],
                ),
            ),
            ["Exchange", "High Risk"],
        ),
        (
            RiskDetailsResponse(
                case_id="3",
                request_datetime="time5",
                response_datetime="time6",
                chain="eth",
                address="addr3",
                name="Coinbase",
                category_name="Exchange",
                risk=7,
                details=Details(
                    own_categories=[
                        OwnCategory(
                            address="addr3",
                            name="Coinbase",
                            category_name="Exchange",
                            risk=7,
                        )
                    ],
                    source_of_funds_categories=[
                        OwnCategory(
                            address="addr3",
                            name="Unknown",
                            category_name="Unknown",
                            risk=0,
                        )
                    ],
                ),
            ),
            ["Exchange", "Unknown"],
        ),
        (
            RiskDetailsResponse(
                case_id="4",
                request_datetime="2023-09-24T15:47:02Z",
                response_datetime="2023-09-24T15:47:02Z",
                chain="eth",
                address="0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
                name="Binance 6",
                category_name="Exchange",
                risk=5,
                details=Details(
                    own_categories=[
                        OwnCategory(
                            address="0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
                            name="Binance 6",
                            category_name="Exchange",
                            risk=5,
                        ),
                        OwnCategory(
                            address="0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
                            name="Binance 7",
                            category_name="Wallet",
                            risk=5,
                        ),
                    ],
                    source_of_funds_categories=[
                        OwnCategory(
                            address="0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
                            name="Binance 8",
                            category_name="Mining",
                            risk=5,
                        )
                    ],
                ),
            ),
            ["Exchange", "Wallet", "Mining"],
        ),
    ],
)
def test_deduplicate_categories(
    input_risk_details: RiskDetailsResponse, expected_categories: list[str]
) -> None:
    """
    Test the deduplication of categories.

    :param input_risk_details: Risk details response from Blockmate API.
    :param expected_categories: Expected deduplicated categories.
    """
    output_categories = deduplicate_categories(input_risk_details)
    assert set(output_categories) == set(expected_categories)
