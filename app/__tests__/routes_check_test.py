"""Test the check route."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestCheckEndpoint(unittest.TestCase):
    """Test the check endpoint."""

    def setUp(self):
        """Set up the test client."""
        self.client = TestClient(app)
        self.mocked_token = "mocked_token"
        self.mocked_rate_limit = "mocked_rate_limit"
        self.project_token_patch = patch(
            "app.routes.check.cfg.project_token", self.mocked_token
        ).start()
        self.rate_limit_patch = patch(
            "app.routes.check.cfg.rate_limit", self.mocked_rate_limit
        ).start()

    def tearDown(self):
        """Tear down the test client."""
        patch.stopall()

    def test_check_ethereum_address_success(self):
        """Test the check endpoint."""
        test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"

        response = self.client.get(f"/check?address={test_address}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(
            data,
            {
                "ethereum_address": test_address,
                "blockmate_token": self.mocked_token,
                "rate_limiter": self.mocked_rate_limit,
            },
        )

    def test_check_ethereum_address_failed(self):
        """Test the check endpoint with incorrect params."""
        response = self.client.get("/check")

        self.assertEqual(response.status_code, 422)

        data = response.json()

        self.assertIn("detail", data)

        self.assertEqual(data["detail"][0]["type"], "missing")
        self.assertEqual(data["detail"][0]["loc"], ["query", "address"])
        self.assertEqual(data["detail"][0]["msg"], "Field required")


if __name__ == "__main__":
    unittest.main()
