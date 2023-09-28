"""
JWT Token Handlers Module.

This module contains the JWTHandler class that provides functionalities
for fetching and refreshing JWT tokens. Using Singleton pattern, the class
ensures that only one JWT handler instance exists across the application.

Components:
- JWTHandler: Class responsible for handling JWT tokens.

Key Considerations:
- Uses FastAPI for HTTP exceptions.
- Utilizes asynchronous programming for non-blocking operations.

Dependencies:
- fetch_new_jwt_token from app.utils.jwt_utils for fetching new tokens.
- FastAPI's HTTPException for error handling.
- Python's standard logging for logging information.
- asyncio.Lock for lock mechanism to handle concurrent requests.

"""
import base64
import json
import logging
from asyncio import Lock
from datetime import datetime, timedelta

from fastapi import HTTPException

from app.utils.jwt_utils import fetch_new_jwt_token

logger = logging.getLogger(__name__)


class JWTHandler:
    """
    Class responsible for fetching and refreshing JWT tokens.

    Provides:
    - Method to fetch new JWT token with `get_token`
    - Method to fetch the expiration time of a JWT token with `_get_expire_time`

    Utilizes FastAPI for error handling and logging for information tracking.
    """

    def __init__(self) -> None:
        """JWT Token handler constructor."""
        self.token = None
        self.expire_time = None
        self.lock = Lock()

    async def get_token(self) -> str:
        """
        Get a valid JWT token.

        :return: Valid JWT token.
        """
        async with self.lock:
            if self.token is None:
                self.token = await fetch_new_jwt_token()
                self.expire_time = self._get_expire_time(self.token)
                logger.info("JWT token fetched")
                logger.info("JWT token expires at: %s", self.expire_time.isoformat())

            if datetime.utcnow() >= self.expire_time:
                self.token = await fetch_new_jwt_token()
                self.expire_time = self._get_expire_time(self.token) - timedelta(
                    seconds=1
                )
                logger.info("JWT token refreshed")
                logger.info("JWT token expires at: %s", self.expire_time.isoformat())

        return self.token

    def _get_expire_time(self, token: str) -> datetime:
        """
        Get the expiration time of a JWT token.

        :param token: JWT token.

        :return: Expiration time of the JWT token as a datetime object.
        """
        try:
            token_parts = token.split(".")
            if len(token_parts) != 3:
                raise HTTPException(status_code=500, detail="Invalid token format.")

            payload = json.loads(
                base64.urlsafe_b64decode(
                    token_parts[1] + "=" * (4 - len(token_parts[1]) % 4)
                ).decode("utf-8")
            )
        except (json.JSONDecodeError, IndexError, UnicodeDecodeError) as exc:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(exc)}"
            ) from exc

        expiration_timestamp = payload.get("exp", 0)
        expiration_datetime = datetime.fromtimestamp(expiration_timestamp)

        return expiration_datetime


jwt_handler = JWTHandler()


async def get_current_token(handler: JWTHandler = jwt_handler) -> str:
    """
    Get the current JWT token.

    :param handler: JWT handler for testing purposes.

    :return: Current JWT token.
    """
    return await handler.get_token()
