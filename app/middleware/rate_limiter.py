"""Rate limiter middleware to limit incoming requests."""
from datetime import datetime, timedelta
from typing import Callable, Coroutine, List

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.config.config import cfg


class RateLimiter:
    """Rate limiter class to limit incoming requests."""

    def __init__(self) -> None:
        """Rate limiter constructor."""
        self.request_timestamps: List[datetime] = []
        self.request_history: List[Request] = []
        self.time_window: timedelta = timedelta(seconds=cfg.rate_limit_time_window)
        self.requests_limit: int = cfg.rate_limit
        self.request_history: dict[str, List[datetime]] = {}

    async def rate_limit_middleware(
        self,
        request: Request,
        call_next: Callable[[Request], Coroutine[None, None, Response]],
    ) -> Response:
        """
        Rate limit middleware to limit incoming requests.

        :param request: Incoming request.
        :param call_next: Next call in the middleware chain.

        :return: Response from the next call in the middleware chain.
        """
        now: datetime = datetime.now()

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

        :param request: Incoming request.
        :param call_next: Next call in the middleware chain.

        :return: Response from the next call in the middleware chain.
        """
        client_ip = request.client.host
        now = datetime.now()

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
