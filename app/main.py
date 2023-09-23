"""Main module for the FastAPI application."""
from fastapi import FastAPI

from app.middleware.rate_limiter import RateLimiter
from app.routes import check

app = FastAPI()

# rate limit middleware
rate_limiter = RateLimiter()
app.middleware("http")(rate_limiter.rate_limit_middleware)

# include the router from the check_route module.
app.include_router(check.router, tags=["check"])
