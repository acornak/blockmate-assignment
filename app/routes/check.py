"""Check route."""
from fastapi import APIRouter

from app.config.config import AppConfig

router = APIRouter()

cfg = AppConfig()


@router.get("/check")
async def check_ethereum_address(
    address: str,
) -> dict[str, str]:
    """
    Handle GET requests to the /check endpoint.

    :param address: Ethereum address to check passed as query param.

    :return: JSON response with the Ethereum address, blockmate_token and rate_limiter.
    """
    return {
        "ethereum_address": address,
        "blockmate_token": cfg.project_token,
        "rate_limiter": cfg.rate_limit,
    }
