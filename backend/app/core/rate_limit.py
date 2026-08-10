"""Simple in-memory sliding-window rate limiter (per-IP + optional key)."""

import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> bool:
        """Return True if the request is allowed, False if rate-limited."""
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] <= now - self.window:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return False
            bucket.append(now)
            return True
