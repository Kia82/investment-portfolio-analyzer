from functools import wraps
from datetime import datetime
from typing import Dict, Any, Optional
from pandas import Timestamp

class DataCache:
    def __init__(self, ttl: int):
        """Initialize cache with time-to-live in seconds"""
        self.ttl = ttl
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None

        if (Timestamp.now() - self._timestamps[key]).total_seconds() > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        return self._cache[key]

    def set(self, key: str, value: Any):
        self._cache[key] = value
        self._timestamps[key] = Timestamp.now()

    def clear(self) -> None:
        self._cache.clear()
        self._timestamps.clear()