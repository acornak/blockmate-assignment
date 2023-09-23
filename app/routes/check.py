"""Check route."""
import logging

from fastapi import APIRouter

from app.cache.cache import get_cache
from app.config.config import cfg

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
    cache = get_cache()
    cached_result = cache.get(address)

    if cached_result:
        logger.info("Cache hit")
        return cached_result

    result = {
        "ethereum_address": address,
        "blockmate_token": cfg.project_token,
    }

    cache.set(address, result)

    return result
