"""
Test Cache Module.

This module contains tests that validate the behavior of the LRU (Least Recently Used) cache
implemented in the application. These tests include scenarios like cache miss, cache hit,
setting cache entries, cache overflow, and cache purging.

Components:
- test_get_miss: Validates that a cache miss returns None.
- test_get_hit: Validates that a cache hit returns the expected value.
- test_set: Validates that a new cache entry can be set.
- test_cache_overflow: Validates that the oldest cache entry is removed
  when the cache exceeds its capacity.
- test_clear_cache: Validates that the cache can be manually cleared.
- test_periodic_purge: Validates that the cache is periodically purged after a given interval.

Key Dependencies:
- pytest for test functionality.
- asyncio for asynchronous test execution.
- LRUCache from app.cache.cache for cache checks.
- CheckEndpointResponse from app.models.check_model for response model.

Usage:
Run these tests to ensure that the LRU cache is functioning as expected.
Each test aims to validate a specific feature or behavior of the cache.

"""
import asyncio

import pytest

from app.cache.cache import LRUCache
from app.models.check_model import CheckEndpointResponse


@pytest.mark.asyncio
async def test_get_miss() -> None:
    """Test that a cache miss returns None."""
    cache = await LRUCache.get_instance()
    result = await cache.get("missing_key")
    assert result is None

    await cache.delete_instance()


value = CheckEndpointResponse(category_names=["test"])


@pytest.mark.asyncio
async def test_get_hit() -> None:
    """Test that a cache hit returns the correct value."""
    cache = await LRUCache.get_instance()
    await cache.set("existing_key", value)
    result = await cache.get("existing_key")
    assert result == value

    await cache.delete_instance()


@pytest.mark.asyncio
async def test_set() -> None:
    """Test that a key-value pair is set correctly."""
    cache = await LRUCache.get_instance()
    await cache.set("new_key", value)
    result = await cache.get("new_key")
    assert result == value

    await cache.delete_instance()


@pytest.mark.asyncio
async def test_cache_overflow() -> None:
    """Test that the cache overflows correctly."""
    cache = await LRUCache.get_instance()
    for i in range(101):
        await cache.set(str(i), CheckEndpointResponse(category_names=[f"test {i}"]))
    assert await cache.get("0") is None

    await cache.delete_instance()


@pytest.mark.asyncio
async def test_clear_cache() -> None:
    """Test that the cache is cleared correctly."""
    cache = await LRUCache.get_instance()
    await cache.set("key", value)
    await cache.clear_cache()
    assert await cache.get("key") is None

    await cache.delete_instance()


@pytest.mark.asyncio
async def test_periodic_purge() -> None:
    """Test that the cache is purged periodically."""
    cache = await LRUCache.get_instance(purge_interval=1)
    cache.capacity = 4
    cache.purge_interval = 1

    await cache.set("a", CheckEndpointResponse(category_names=["A"]))
    await cache.set("b", CheckEndpointResponse(category_names=["B"]))
    await cache.set("c", CheckEndpointResponse(category_names=["C"]))
    await cache.set("d", CheckEndpointResponse(category_names=["D"]))

    await asyncio.sleep(1.2)
    cache.stop_purge()

    assert len(cache.cache) == 0
    assert await cache.get("a") is None
    assert await cache.get("b") is None
    assert await cache.get("c") is None
    assert await cache.get("d") is None

    cache.stop_purge()

    await cache.delete_instance()
