"""Utility functions for handling risk details requests."""
import logging
import urllib.parse

import httpx
from fastapi import HTTPException

from app.config.config import cfg
from app.models.risk_model import RiskDetailsResponse

logger = logging.getLogger(__name__)


async def fetch_risk_details(address: str, jwt_token: str) -> str:
    """
    Fetch a new JWT token from the auth service.

    :param address: Ethereum address to check passed as query param.
    :param jwt_token: Generated JWT token.

    :return: Response from blockmate.io risk details endpoint.
    """
    headers = {"accept": "application/json", "authorization": f"Bearer {jwt_token}"}
    url = f"{cfg.blockmate_api_url}?address={urllib.parse.quote(address)}&chain=eth"

    """
    Response from Blockmate API: {
        'case_id': '703c0074-698a-4f2a-88a3-5a48a08047b2',
        'request_datetime': '2023-09-24T15:47:02Z',
        'response_datetime': '2023-09-24T15:47:02Z',
        'chain': 'eth',
        'address': '0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67',
        'name': 'Binance 6',
        'category_name':'Exchange',
        'risk': 5,
        'details': {
            'own_categories': [
                {
                    'address': '0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67',
                    'name': 'Binance 6',
                    'category_name': 'Exchange',
                    'risk': 5
                }
            ],
            'source_of_funds_categories': []
        }
    }
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return RiskDetailsResponse.model_validate_json(response.text)

            logger.error("Unable to fetch risk details: %s", response.json())
            raise HTTPException(
                status_code=502,
                detail=f"Unable to fetch risk details: {response.json()}",
            )
    except httpx.RequestError as exc:
        logger.error("Request error: %s", str(exc))
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch risk details: Internal server error",
        ) from exc


def deduplicate_categories(risk_details: RiskDetailsResponse) -> list[str]:
    """
    Deduplicate categories.

    :param risk_details: Risk details response from Blockmate API.

    :return: List of categories.
    """
    categories: set[str] = set()

    categories.add(risk_details.category_name)

    for own_category in risk_details.details.own_categories:
        categories.add(own_category.category_name)

    for source_category in risk_details.details.source_of_funds_categories:
        categories.add(source_category.category_name)

    return list(categories)
