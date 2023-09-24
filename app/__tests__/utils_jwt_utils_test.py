"""Test the JWT utility functions."""
import unittest
from unittest.mock import patch

from httpx import Response

from app.utils.jwt_utils import fetch_new_jwt_token


class TestFetchNewJwtToken(unittest.IsolatedAsyncioTestCase):
    """Test the fetch_new_jwt_token function."""

    @patch("httpx.AsyncClient.get")
    async def test_fetch_new_jwt_token_success(self, mock_get) -> None:
        """Test the successful fetch of a new JWT token."""
        fake_token = "fake_token"

        response = Response(200, json={"token": fake_token})
        mock_get.return_value = response

        result = await fetch_new_jwt_token()
        self.assertEqual(result, fake_token)

    @patch("httpx.AsyncClient.get")
    async def test_fetch_new_jwt_token_failure(self, mock_get) -> None:
        """Test the failure to fetch a new JWT token."""
        response = Response(400, json={"error": "something went wrong"})
        mock_get.return_value = response

        result = await fetch_new_jwt_token()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
