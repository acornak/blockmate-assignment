"""JWT Token handlers."""
import base64
import json
import logging
from asyncio import Lock
from datetime import datetime

from fastapi import HTTPException

from app.utils.jwt_utils import fetch_new_jwt_token


class JWTHandler:
    """JWT Token handler."""

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
                logging.info("JWT token fetched")

            if datetime.utcnow() >= self.expire_time:
                self.token = await fetch_new_jwt_token()
                self.expire_time = self._get_expire_time(self.token)
                logging.info("JWT token refreshed")

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
                raise HTTPException(status_code=401, detail="Invalid token format")

            payload = json.loads(
                base64.urlsafe_b64decode(
                    token_parts[1] + "=" * (4 - len(token_parts[1]) % 4)
                ).decode("utf-8")
            )
        except (json.JSONDecodeError, IndexError) as exc:
            raise HTTPException(
                status_code=401, detail="Invalid token payload"
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
