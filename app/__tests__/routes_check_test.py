"""Test the check route."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.__tests__.base import BaseTest
from app.cache.cache import get_cache
from app.main import app


class TestCheckEndpoint(BaseTest):
    """Test the check endpoint."""

    def setUp(self):
        """Set up the test client."""
        self.client = TestClient(app)

        self.mocked_token = "mocked_token"
        self.project_token_patch = patch(
            "app.routes.check.cfg.project_token", self.mocked_token
        ).start()

        self.rate_limit_patch = patch("app.routes.check.cfg.rate_limit", 100).start()
        self.rate_limit_time_window_patch = patch(
            "app.routes.check.cfg.rate_limit_time_window", 60
        ).start()

        self.cache_instance = get_cache()

    def tearDown(self):
        """Tear down the test client."""
        patch.stopall()

    def test_check_ethereum_address_success(self):
        """Test the check endpoint success."""
        test_address = "0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"

        response = self.client.get(f"/check?address={test_address}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(
            data,
            {
                "ethereum_address": test_address,
                "blockmate_token": self.mocked_token,
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
