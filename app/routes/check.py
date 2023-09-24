"""Check route."""
import logging

from fastapi import APIRouter

from app.cache.cache import get_cache
from app.config.config import cfg
from app.jwt.jwt import get_current_token

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/check")
async def check_ethereum_address(
    address: str,
    # jwt_token: str = Depends(get_current_token),
) -> dict[str, str]:
    """
    Handle GET requests to the /check endpoint.

    :param address: Ethereum address to check passed as query param.
    :param jwt_token: JWT token from the Depends.

    :return: JSON response with the Ethereum address, blockmate_token and rate_limiter.
    """
    logging.info("Check endpoint hit")
    jwt_token = await get_current_token()
    logging.info(f"JWT token: {jwt_token}")

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
