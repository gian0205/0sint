"""Token-bucket rate limiter per operator (in-memory)."""
from __future__ import annotations

import time
from threading import Lock


class TokenBucket:
    """Fixed-rate token bucket. `capacity` tokens, refilled at `rate` tokens/sec."""

    __slots__ = ("capacity", "rate", "tokens", "last", "lock")

    def __init__(self, capacity: float, rate: float) -> None:
        self.capacity = capacity
        self.rate = rate
        self.tokens = capacity
        self.last = time.monotonic()
        self.lock = Lock()

    def take(self, cost: float = 1.0) -> tuple[bool, float]:
        """Try to consume `cost` tokens. Returns (allowed, retry_after_seconds)."""
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens >= cost:
                self.tokens -= cost
                return True, 0.0
            missing = cost - self.tokens
            return False, missing / self.rate if self.rate > 0 else float("inf")


class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = Lock()

    def check(self, operator: str) -> tuple[bool, float]:
        with self._lock:
            bucket = self._buckets.get(operator)
            if bucket is None:
                bucket = TokenBucket(capacity=self.per_minute, rate=self.per_minute / 60.0)
                self._buckets[operator] = bucket
        return bucket.take(1.0)

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()
