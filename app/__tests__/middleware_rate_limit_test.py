"""Test the rate-limiting middleware."""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.rate_limiter import RateLimiter


@pytest.fixture(scope="function")
def app_setup() -> tuple:
    """
    Get the app and test client.

    :return: The app and test client.
    """
    app = FastAPI()
    client = TestClient(app)

    @app.get("/")
    def dummy_route():
        return {"message": "success"}

    return app, client


@pytest.fixture(scope="function")
def rate_limiter() -> RateLimiter:
    """
    Get the rate limiter.

    :return: The rate limiter.
    """
    return RateLimiter()


@pytest.fixture(scope="function")
def patched_config() -> None:
    """
    Patch the config.

    :return: None.
    """
    with patch("app.middleware.rate_limiter.cfg.rate_limit", 5), patch(
        "app.middleware.rate_limiter.cfg.rate_limit_time_window", 10
    ):
        yield


@pytest.mark.usefixtures("patched_config")
def test_rate_limit(app_setup, rate_limiter) -> None:
    """Test that rate-limiting works."""
    app, client = app_setup
    app.middleware("http")(rate_limiter.rate_limit_middleware)

    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200

    response = client.get("/")
    assert response.status_code == 429


@pytest.mark.usefixtures("patched_config")
def test_rate_limit_reset(app_setup, rate_limiter) -> None:
    """Test that rate-limiting resets after time_window."""
    app, client = app_setup
    app.middleware("http")(rate_limiter.rate_limit_middleware)

    rate_limiter.request_timestamps.append(datetime.now() - timedelta(seconds=12))

    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200


@pytest.mark.usefixtures("patched_config")
def test_advanced_rate_limit(app_setup, rate_limiter) -> None:
    """Test that rate-limiting works per IP."""
    app, client = app_setup
    app.middleware("http")(rate_limiter.rate_limit_middleware_per_ip)

    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200

    response = client.get("/")
    assert response.status_code == 429


@pytest.mark.usefixtures("patched_config")
def test_advanced_rate_limit_reset(app_setup, rate_limiter) -> None:
    """Test that rate-limiting resets after time_window."""
    app, client = app_setup
    app.middleware("http")(rate_limiter.rate_limit_middleware_per_ip)

    rate_limiter.request_history["127.0.0.1"] = datetime.now() - timedelta(seconds=12)

    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200
