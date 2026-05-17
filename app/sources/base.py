"""Base class for OSINT source adapters."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod

from ..models import SourceResult, SourceStatus


class Source(ABC):
    """A pluggable OSINT data source.

    Each source receives a normalized 11-digit CPF and returns a `SourceResult`.
    Sources must never raise on network errors — return `UNAVAILABLE` with notes.
    """

    name: str
    description: str
    requires_captcha: bool = False
    homepage: str | None = None

    @abstractmethod
    async def query(self, cpf: str) -> SourceResult: ...

    async def run(self, cpf: str) -> SourceResult:
        start = time.perf_counter()
        try:
            result = await self.query(cpf)
        except Exception as exc:  # noqa: BLE001 - adapters must never propagate
            result = SourceResult(
                source=self.name,
                status=SourceStatus.ERROR,
                notes=f"unhandled exception: {type(exc).__name__}: {exc}",
            )
        result.elapsed_ms = int((time.perf_counter() - start) * 1000)
        return result
