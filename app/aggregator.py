"""Run multiple source adapters in parallel and assemble a `LookupResponse`.

Includes a TTL cache layer keyed by (CPF + sources). Cache hits still emit
audit log entries (with `cached: true`) so accountability is preserved.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from . import audit
from .cache import TTLCache, make_key
from .config import settings
from .cpf import is_valid, mask, normalize, region
from .models import LookupRequest, LookupResponse, Purpose, SourceResult
from .sources import get_sources


_cache = TTLCache(max_entries=settings.cache_max_entries, ttl_seconds=settings.cache_ttl_seconds)


def cache_clear() -> None:
    _cache.clear()


async def aggregate(req: LookupRequest, operator: str) -> LookupResponse:
    cpf_digits = normalize(req.cpf)
    sources = get_sources(req.sources)
    source_names = [s.name for s in sources]

    key = make_key(cpf_digits, source_names)
    cached: list[SourceResult] | None = _cache.get(key)

    if cached is not None:
        audit.record_lookup(req, operator, source_names, cached=True)
        results = cached
        is_cached = True
    else:
        audit.record_lookup(req, operator, source_names, cached=False)
        results = await asyncio.gather(*(s.run(cpf_digits) for s in sources))
        _cache.set(key, results)
        is_cached = False

    return LookupResponse(
        cpf_masked=mask(cpf_digits),
        cpf_valid=is_valid(cpf_digits),
        region=region(cpf_digits),
        requested_at=datetime.now(timezone.utc),
        purpose=req.purpose,
        operator=operator,
        case_id=req.case_id,
        results=results,
        cached=is_cached,
    )
