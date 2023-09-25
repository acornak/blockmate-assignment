"""Least recently used cache."""
import logging
from asyncio import Lock
from collections import OrderedDict

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU Cache implementation using OrderedDict."""

    _instance = None
    _lock = Lock()

    def __init__(self, capacity: int, purge_interval: int) -> None:
        """Initialize the cache with a capacity and purge interval."""
        self.cache = OrderedDict()
        self.capacity = capacity
        self.purge_interval = purge_interval
        self._instance_lock = Lock()

    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the cache."""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(100, 60)
        return cls._instance

    async def get(self, key: str) -> dict[str, str]:
        """Get the value of a key in the cache."""
        async with self._instance_lock:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            return self.cache[key]

    async def set(self, key: str, value: dict[str, str]) -> None:
        """Set the value of a key in the cache."""
        async with self._instance_lock:
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    async def clear_cache(self) -> None:
        """Clear the cache."""
        async with self._instance_lock:
            self.cache.clear()
