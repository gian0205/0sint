"""In-memory TTL cache for lookup responses, keyed by CPF + sources."""
from __future__ import annotations

import time
from collections import OrderedDict
from threading import Lock
from typing import Any


class TTLCache:
    def __init__(self, max_entries: int, ttl_seconds: int) -> None:
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = Lock()

    def _expired(self, ts: float) -> bool:
        return (time.monotonic() - ts) > self.ttl_seconds

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            ts, value = entry
            if self._expired(ts):
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.monotonic(), value)
            self._store.move_to_end(key)
            while len(self._store) > self.max_entries:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


def make_key(cpf_digits: str, sources: list[str] | None) -> str:
    src = ",".join(sorted(sources)) if sources else "*"
    return f"{cpf_digits}|{src}"
