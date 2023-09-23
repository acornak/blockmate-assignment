"""Least recently used cache."""
import logging
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU Cache implementation using OrderedDict."""

    def __init__(self, capacity: int, purge_interval: int) -> None:
        """Initialize the cache with a capacity and purge interval."""
        self.cache = OrderedDict()
        self.capacity = capacity
        self.purge_interval = purge_interval
        self.timer = threading.Timer(self.purge_interval, self.clear_cache)
        self.timer.start()

    def get(self, key: str) -> dict[str, str]:
        """Get the value of a key in the cache."""
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key: str, value: dict[str, str]) -> None:
        """Set the value of a key in the cache."""
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        logging.info("Cache cleared")
        self.timer = threading.Timer(self.purge_interval, self.clear_cache)
        self.timer.start()

    def stop_purge_timer(self) -> None:
        """Stop the purge timer."""
        self.timer.cancel()


_cache_instance = None


def get_cache() -> LRUCache:
    """Lazy instantiation of the cache."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LRUCache(100, 10)
    return _cache_instance
