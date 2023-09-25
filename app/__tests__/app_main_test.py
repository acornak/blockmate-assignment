"""Test the main module."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function")
def client() -> TestClient:
    """
    Get the test client.

    :return: The test client.
    """
    return TestClient(app)


def test_not_found(client) -> None:
    """Test that the / route returns a 404."""
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_check_route_exists() -> None:
    """Test that the /check route exists with the correct methods."""
    expected_path = "/check"
    expected_methods = {"GET"}

    for route in app.routes:
        if route.path == expected_path:
            assert set(route.methods) == expected_methods
            return

    pytest.fail(
        f"The route {expected_path} with methods {expected_methods} was not found."
    )
