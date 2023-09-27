"""Check route."""
import logging
from time import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.cache.cache import LRUCache
from app.jwt.jwt import get_current_token
from app.models.check_model import CheckEndpointResponse
from app.utils.risk_utils import deduplicate_categories, fetch_risk_details

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/check", response_model=CheckEndpointResponse, tags=["check"])
async def check_ethereum_address(
    address: str,
) -> CheckEndpointResponse:
    """
    Handle GET requests to the /check endpoint.

    :param address: Ethereum address to check passed as query param.

    :return: Deduplicated categories from blockmate.io response.
    """
    # some metrics
    start_time = time()

    try:
        jwt_token = await get_current_token()
    except HTTPException as exc:
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

    cache = await LRUCache.get_instance()
    cached_result = await cache.get(address)

    if cached_result:
        end_time = time()
        logger.info(
            "/check endpoint response took %.2f milliseconds (cached)",
            (end_time - start_time) * 1000,
        )
        return cached_result

    try:
        response = await fetch_risk_details(address, jwt_token)
        logger.info("Risk details response: %s", response)
    except HTTPException as exc:
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

    categories = deduplicate_categories(response)

    result = CheckEndpointResponse(category_names=categories)

    await cache.set(address, result)

    end_time = time()
    logger.info(
        "/check endpoint response took %.2f milliseconds",
        (end_time - start_time) * 1000,
    )

    return result
