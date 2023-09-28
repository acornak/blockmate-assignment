"""
Rate Limiter Middleware Module.

This module contains the RateLimiter class that provides middleware
to limit the rate of incoming requests.

Components:
- RateLimiter: Class responsible for rate-limiting incoming API requests.

Key Considerations:
- Uses FastAPI for handling requests and responses.
- Provides both global and per-IP rate limiting.

Dependencies:
- fastapi.Request and fastapi.Response for handling HTTP objects.
- asyncio.Lock for lock mechanism to handle concurrent requests.

"""
from asyncio import Lock
from datetime import datetime, timedelta
from typing import Callable, Coroutine

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.config.config import cfg


class RateLimiter:
    """
    Middleware class for rate-limiting incoming API requests.

    Provides:
    - Global rate limiting with `rate_limit_middleware`
    - Per-IP rate limiting with `rate_limit_middleware_per_ip`

    Utilizes FastAPI middleware functionality.
    """

    def __init__(self) -> None:
        """Rate limiter constructor."""
        self.request_timestamps: list[datetime] = []
        self.request_history: list[Request] = []
        self.time_window: timedelta = timedelta(seconds=cfg.rate_limit_time_window)
        self.requests_limit: int = cfg.rate_limit
        self.request_history: dict[str, list[datetime]] = {}
        self.lock = Lock()

    async def rate_limit_middleware(
        self,
        request: Request,
        call_next: Callable[[Request], Coroutine[None, None, Response]],
    ) -> Response:
        """
        Middleware for global rate limiting.

        :param request: Incoming API request.
        :param call_next: Next middleware in FastAPI's middleware chain.

        :return: API response or rate limit exceeded message.
        """
        now: datetime = datetime.now()

        async with self.lock:
            self.request_timestamps = [
                timestamp
                for timestamp in self.request_timestamps
                if now - timestamp <= self.time_window
            ]

            if len(self.request_timestamps) >= self.requests_limit:
                return JSONResponse(
                    content={"detail": "Rate limit exceeded"}, status_code=429
                )

            self.request_timestamps.append(now)

        response: Response = await call_next(request)
        return response

    async def rate_limit_middleware_per_ip(
        self,
        request: Request,
        call_next: Callable[[Request], Coroutine[None, None, Response]],
    ) -> Response:
        """
        More advanced rate limit middleware to limit incoming requests per IP.

        In addition to the rate limit middleware, this middleware also keeps track of
        the requests per IP. IP can be replaced with any other identifier, such as
        user ID, API key, etc. Useful for rate limiting per user.

        :param request: Incoming API request.
        :param call_next: Next middleware in FastAPI's middleware chain.

        :return: API response or rate limit exceeded message.
        """
        now = datetime.now()

        async with self.lock:
            client_ip = request.client.host

            if client_ip in self.request_history:
                self.request_history[client_ip] = [
                    timestamp
                    for timestamp in self.request_history[client_ip]
                    if now - timestamp <= self.time_window
                ]

            if len(self.request_history.get(client_ip, [])) >= self.requests_limit:
                return JSONResponse(
                    content={"detail": "Rate limit exceeded"}, status_code=429
                )

            if client_ip not in self.request_history:
                self.request_history[client_ip] = []

            self.request_history[client_ip].append(now)

        response: Response = await call_next(request)
        return response
