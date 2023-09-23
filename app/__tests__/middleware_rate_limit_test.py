"""Test the rate-limiting middleware."""
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.__tests__.base import BaseTest
from app.middleware.rate_limiter import RateLimiter


class BaseRateLimitMiddlewareTest(BaseTest):
    """Parent class for rate-limiting middleware tests."""

    url = "/"

    def setUp(self) -> None:
        """
        Set up the test client.

        Create a dummy FastAPI app and add the rate-limiting middleware.
        Includes patching the rate-limiting config.
        """
        self.rate_limit_patch = patch(
            "app.middleware.rate_limiter.cfg.rate_limit", 5
        ).start()
        self.rate_limit_time_window_patch = patch(
            "app.middleware.rate_limiter.cfg.rate_limit_time_window", 10
        ).start()

        self.app = FastAPI()

        @self.app.get(self.url)
        def dummy_route():
            return {"message": "success"}

        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        """Tear down the test client."""
        patch.stopall()
        self.clear_rate_limiter()

    def clear_rate_limiter(self) -> None:
        """Clear the rate limiter."""
        pass

    def add_timestamp(self, timestamp: datetime) -> None:
        """
        Add a timestamp to the rate limiter.

        :param timestamp: Timestamp to add to the rate limiter.
        """
        pass

    def rate_limit(self) -> None:
        """
        Test the rate-limiting feature.

        First 5 requests should be allowed. The 6th request should be rate-limited.
        """
        response = None

        for _ in range(5):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 429)

    def rate_limit_reset(self) -> None:
        """
        Test that rate-limiting resets after time_window.

        Appends timestamp that is 12 seconds old to the request_timestamps list.
        This should be removed by the middleware.

        First 5 requests should be allowed.
        """
        self.add_timestamp(datetime.now() - timedelta(seconds=12))

        for _ in range(5):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)


class TestBasicRateLimitMiddleware(BaseRateLimitMiddlewareTest):
    """Test basic rate-limiting middleware."""

    def setUp(self) -> None:
        """Set up the test client."""
        super().setUp()
        self.rate_limiter = RateLimiter()
        self.app.middleware("http")(self.rate_limiter.rate_limit_middleware)

    def clear_rate_limiter(self) -> None:
        """Clear the rate limiter."""
        self.rate_limiter.request_timestamps.clear()

    def add_timestamp(self, timestamp: datetime) -> None:
        """Add a timestamp to the rate limiter."""
        self.rate_limiter.request_timestamps.append(timestamp)

    def test_rate_limit(self) -> None:
        """Test the rate-limiting feature."""
        super().rate_limit()

    def test_rate_limit_reset(self) -> None:
        """Test that rate-limiting resets after time_window."""
        super().rate_limit_reset()


class TestAdvancedRateLimitMiddleware(BaseRateLimitMiddlewareTest):
    """Test advanced rate-limiting middleware."""

    def setUp(self) -> None:
        """Set up the test client."""
        super().setUp()
        self.rate_limiter = RateLimiter()
        self.app.middleware("http")(self.rate_limiter.rate_limit_middleware_per_ip)

    def clear_rate_limiter(self) -> None:
        """Clear the rate limiter."""
        self.rate_limiter.request_history.clear()

    def add_timestamp(self, timestamp: datetime) -> None:
        """Add a timestamp to the rate limiter."""
        test_url = "127.0.0.1"
        self.rate_limiter.request_history[test_url] = timestamp

    def test_advanced_rate_limit(self) -> None:
        """Test the rate-limiting feature."""
        super().rate_limit()

    def test_advanced_rate_limit_reset(self) -> None:
        """Test that rate-limiting resets after time_window."""
        super().rate_limit_reset()


if __name__ == "__main__":
    unittest.main()
