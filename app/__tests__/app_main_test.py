"""Test the main module."""
import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestMain(unittest.TestCase):
    """Test the main module."""

    def setUp(self):
        """Set up the test client."""
        self.client = TestClient(app)

    def test_not_found(self):
        """Test that the / route returns a 404."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Not Found"})

    def test_check_route_exists(self):
        """Test that the /check route exists with the correct methods."""
        expected_path = "/check"
        expected_methods = {"GET"}

        for route in app.routes:
            if route.path == expected_path:
                self.assertEqual(set(route.methods), expected_methods)
                return

        self.fail(
            f"The route {expected_path} with methods {expected_methods} was not found."
        )


if __name__ == "__main__":
    unittest.main()
