"""Main module for the FastAPI application."""
import logging
import os

from fastapi import FastAPI

from app.cache.cache import get_cache
from app.middleware.rate_limiter import RateLimiter
from app.routes import check

# setup logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(levelname)s:     %(message)s",
)
logger = logging.getLogger(__name__)


# create the FastAPI app
app = FastAPI()

# rate limit middleware
rate_limiter = RateLimiter()
app.middleware("http")(rate_limiter.rate_limit_middleware)

# include the router from the check_route module.
app.include_router(check.router, tags=["check"])


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Stop the cache purge timer on shutdown."""
    cache = get_cache()
    cache.stop_purge_timer()
