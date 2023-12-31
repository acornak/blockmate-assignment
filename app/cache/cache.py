"""
Least Recently Used (LRU) Cache Module.

This module provides an asynchronous LRU cache implementation using an OrderedDict.
It follows the Singleton design pattern,
ensuring that only one cache instance exists across the application.

Components:
- LRUCache: Class implementing the LRU cache.

Key Attributes:
- _instance: Singleton instance of the LRU cache
- _lock: Class-level lock for singleton instance access
- cache: The actual cache implemented as an OrderedDict
- capacity: Maximum number of elements in the cache
- purge_interval: Time interval for automatic cache purging in seconds
- _instance_lock: Instance-level lock for thread safety

Methods:
- get_instance: Creates or retrieves the singleton instance of the cache.
- delete_instance: Deletes the singleton instance.
- get: Retrieves an item from the cache.
- set: Inserts or updates an item in the cache.
- clear_cache: Manually clears the cache.
- periodic_purge: Periodically purges the cache based on the set interval.
- stop_purge: Stops the purge process.

Dependencies:
- logging for logging actions and errors
- asyncio for asynchronous programming
- OrderedDict from collections for cache implementation
- CheckEndpointResponse from app.models.check_model for type hinting
"""
import logging
from asyncio import Lock, create_task, sleep
from collections import OrderedDict
from typing import Optional

from app.models.check_model import CheckEndpointResponse

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU Cache Implementation.

    This class manages an LRU cache with a specified maximum capacity and optional purge interval.
    It is designed as a Singleton to ensure only one cache instance across the application.

    Attributes:
    - cache: Actual cache implemented as an OrderedDict
    - capacity: Maximum number of elements that can be stored in the cache
    - purge_interval: Time interval for automatic cache purging, in seconds
    - _instance_lock: Lock for ensuring thread-safe access to instance attributes
    - _stop_purge: Flag to stop the periodic purge process
    """

    _instance: Optional["LRUCache"] = None
    _lock: Lock = Lock()
    cache: OrderedDict[str, CheckEndpointResponse]
    capacity: int
    purge_interval: int
    _instance_lock: Lock

    def __init__(self, capacity: int, purge_interval: int) -> None:
        """Initialize the cache with a capacity and purge interval."""
        self.cache = OrderedDict()
        self.capacity = capacity
        self.purge_interval = purge_interval
        self._instance_lock = Lock()
        self._stop_purge = False

        if self.purge_interval is not None:
            create_task(self.periodic_purge())

    @classmethod
    async def get_instance(
        cls, capacity: int = 100, purge_interval: int = None
    ) -> "LRUCache":
        """
        Get the singleton instance of the cache.

        More explicit than using the __new__ method.
        """
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(capacity, purge_interval)
                logger.info("Created new cache instance")
        return cls._instance

    @classmethod
    async def delete_instance(cls) -> None:
        """Delete the singleton instance."""
        async with cls._lock:
            cls._instance = None

    async def get(self, key: str) -> Optional[CheckEndpointResponse]:
        """
        Get the value of a key in the cache.

        :param key: The key to retrieve.

        :return: The value of the key if it exists, else None.
        """
        async with self._instance_lock:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            logger.info("Cache hit for key: %s", key)
            return self.cache[key]

    async def set(self, key: str, value: CheckEndpointResponse) -> None:
        """
        Set the value of a key in the cache.

        :param key: The key to set.
        :param value: The value to set.
        """
        async with self._instance_lock:
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    async def clear_cache(self) -> None:
        """Clear the cache manually."""
        async with self._instance_lock:
            self.cache.clear()

    async def periodic_purge(self) -> None:
        """Periodically purge the oldest items in the cache."""
        while not self._stop_purge:
            await sleep(self.purge_interval)
            async with self._instance_lock:
                self.cache.clear()
                logger.info("Cache purged")

    def stop_purge(self) -> None:
        """Stop the purge process."""
        self._stop_purge = True
