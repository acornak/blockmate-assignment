"""Main module for the FastAPI application."""
import logging
import os

from fastapi import FastAPI

from app.cache.cache import LRUCache
from app.middleware.rate_limiter import RateLimiter
from app.routes import check

# setup logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(levelname)s:     %(message)s",
)
logger = logging.getLogger(__name__)


class AppState:
    """State of the FastAPI application."""

    def __init__(self) -> None:
        """Initialize the state."""
        self.cache_instance = None


# create the FastAPI app
app = FastAPI()


# create the cache instance
@app.on_event("startup")
async def startup_event() -> None:
    """Create the cache instance."""
    app.state.cache_instance = await LRUCache.get_instance(
        capacity=100, purge_interval=60
    )


# rate limit middleware
rate_limiter = RateLimiter()
app.middleware("http")(rate_limiter.rate_limit_middleware)

# include the router from the check_route module.
app.include_router(check.router, tags=["check"])


# shutdown the cache instance
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown the cache instance."""
    if app.state.cache_instance:
        logger.info("Shutting down the cache instance.")
        app.state.cache_instance.stop_purge()
        await app.state.cache_instance.delete_instance()
