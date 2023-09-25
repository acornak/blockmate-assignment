"""Check route."""
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.cache.cache import LRUCache
from app.config.config import cfg
from app.jwt.jwt import get_current_token
from app.utils.risk_utils import fetch_risk_details

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/check")
async def check_ethereum_address(
    address: str,
) -> dict[str, str]:
    """
    Handle GET requests to the /check endpoint.

    :param address: Ethereum address to check passed as query param.

    :return: JSON response with the Ethereum address, blockmate_token and rate_limiter.
    """
    jwt_token = await get_current_token()

    cache = await LRUCache.get_instance()
    cached_result = await cache.get(address)

    if cached_result:
        return cached_result

    try:
        response = await fetch_risk_details(address, jwt_token)
        print(response)
    except HTTPException as exc:
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

    result = {
        "ethereum_address": address,
        "blockmate_token": cfg.project_token,
    }

    await cache.set(address, result)

    return result
