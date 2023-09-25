"""Test the cache module."""
import pytest

from app.cache.cache import LRUCache


@pytest.mark.asyncio
async def test_get_miss() -> None:
    """Test that a cache miss returns None."""
    cache = await LRUCache.get_instance()
    result = await cache.get("missing_key")
    assert result is None


@pytest.mark.asyncio
async def test_get_hit() -> None:
    """Test that a cache hit returns the correct value."""
    cache = await LRUCache.get_instance()
    await cache.set("existing_key", {"value": "test"})
    result = await cache.get("existing_key")
    assert result == {"value": "test"}


@pytest.mark.asyncio
async def test_set() -> None:
    """Test that a key-value pair is set correctly."""
    cache = await LRUCache.get_instance()
    await cache.set("new_key", {"value": "new_value"})
    result = await cache.get("new_key")
    assert result == {"value": "new_value"}


@pytest.mark.asyncio
async def test_cache_overflow() -> None:
    """Test that the cache overflows correctly."""
    cache = await LRUCache.get_instance()
    for i in range(101):
        await cache.set(str(i), {"value": "new_value"})
    assert await cache.get("0") is None


@pytest.mark.asyncio
async def test_clear_cache() -> None:
    """Test that the cache is cleared correctly."""
    cache = await LRUCache.get_instance()
    await cache.set("key", {"value": "value"})
    await cache.clear_cache()
    assert await cache.get("key") is None
