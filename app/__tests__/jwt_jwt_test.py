"""Test the JWT class."""
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.jwt.jwt import JWTHandler, get_current_token


class TestJWTHandler(unittest.TestCase):
    """Test the JWTHandler class."""

    def setUp(self):
        """Set up the JWTHandler."""
        self.jwt_handler = JWTHandler()

    def tearDown(self):
        """Tear down the JWTHandler."""
        patch.stopall()

    @patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
    async def test_get_current_token(self, mock_fetch_new_jwt_token):
        """Test the get_current_token method without token."""
        mock_fetch_new_jwt_token.return_value = self.test_token

        current_token = await get_current_token(self.jwt_handler)

        self.assertEqual(current_token, mock_fetch_new_jwt_token.return_value)
        mock_fetch_new_jwt_token.assert_called()

    @patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
    async def test_valid_token(self, mock_fetch_new_jwt_token):
        """Test the get_current_token method with a valid token."""
        mock_fetch_new_jwt_token.return_value = self.test_token

        self.jwt_handler.expire_time = datetime.utcnow() + timedelta(seconds=60)
        self.jwt_handler.token = self.test_token

        current_token = await get_current_token(self.jwt_handler)

        self.assertEqual(current_token, mock_fetch_new_jwt_token.return_value)
        mock_fetch_new_jwt_token.assert_not_called()

    @patch("app.jwt.jwt.fetch_new_jwt_token", new_callable=AsyncMock)
    async def test_expired_token(self, mock_fetch_new_jwt_token):
        """Test the get_current_token method with an expired token."""
        mock_fetch_new_jwt_token.return_value = self.test_token

        self.jwt_handler.expire_time = datetime.utcnow() - timedelta(seconds=10)
        self.jwt_handler.token = self.test_token

        current_token = await get_current_token(self.jwt_handler)

        self.assertEqual(current_token, mock_fetch_new_jwt_token.return_value)
        mock_fetch_new_jwt_token.assert_called()


if __name__ == "__main__":
    unittest.main()
