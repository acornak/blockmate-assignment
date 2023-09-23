"""Test the cache module."""
import unittest
from unittest.mock import patch

from app.__tests__.base import BaseTest
from app.cache.cache import LRUCache


class TestLRUCache(BaseTest):
    """Test the LRU cache."""

    def setUp(self) -> None:
        """Set up the LRU cache."""
        self.cache = LRUCache(100, 60)

    def tearDown(self) -> None:
        """Tear down the LRU cache."""
        self.cache.stop_purge_timer()

    def test_get_miss(self) -> None:
        """Test a cache miss."""
        result = self.cache.get("missing_key")
        self.assertIsNone(result)

    def test_get_hit(self) -> None:
        """Test a cache hit."""
        self.cache.set("existing_key", {"value": "test"})
        result = self.cache.get("existing_key")
        self.assertEqual(result, {"value": "test"})

    def test_set(self) -> None:
        """Test setting a value in the cache."""
        self.cache.set("new_key", {"value": "new_value"})
        result = self.cache.get("new_key")
        self.assertEqual(result, {"value": "new_value"})

    def test_cache_overflow(self) -> None:
        """Test that the cache overflows."""
        for i in range(101):
            self.cache.set(str(i), {"value": "new_value"})

        self.assertIsNone(self.cache.get("0"))

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        self.cache.set("key", {"value": "value"})
        self.cache.cache.clear()
        self.assertIsNone(self.cache.get("key"))

    def test_stop_purge_timer(self) -> None:
        """Test stopping the purge timer."""
        with patch.object(LRUCache, "stop_purge_timer") as mock_stop_purge_timer:
            self.cache.stop_purge_timer()

        mock_stop_purge_timer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
