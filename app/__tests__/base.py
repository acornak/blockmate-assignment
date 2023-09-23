"""Base test class for all tests."""
import logging
import unittest


class BaseTest(unittest.TestCase):
    """Base test class for all tests."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the base test class."""
        logging.getLogger().setLevel(logging.ERROR)
