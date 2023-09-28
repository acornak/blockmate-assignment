"""
Utility functions for handling risk details requests.

This module contains utility functions focused on dealing with risk details.

1. Risk Details Fetching: Retrieves the risk details of
   a specific Ethereum address from the Blockmate API.
2. Category Deduplication: Deduplicates categories received from
   Blockmate API to present a simplified list.

Key Considerations:
- Uses httpx for asynchronous HTTP requests.
- Exceptions are logged and propagated as HTTPException,
  indicating the HTTP status and detail for debugging.

Dependencies:
- httpx for the HTTP client.
- fastapi.HTTPException for exception handling.
- app.config for application configuration parameters.
- app.models for request and response models.
- logging for logging purposes.

"""
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
