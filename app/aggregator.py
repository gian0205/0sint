"""Run multiple source adapters in parallel and assemble a `LookupResponse`."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from . import audit
from .cpf import is_valid, mask, normalize, region
from .models import LookupRequest, LookupResponse, SourceResult
from .sources import get_sources


async def aggregate(req: LookupRequest) -> LookupResponse:
    cpf_digits = normalize(req.cpf)
    sources = get_sources(req.sources)
    audit.record_lookup(req, [s.name for s in sources])

    results: list[SourceResult] = await asyncio.gather(*(s.run(cpf_digits) for s in sources))

    return LookupResponse(
        cpf_masked=mask(cpf_digits),
        cpf_valid=is_valid(cpf_digits),
        region=region(cpf_digits),
        requested_at=datetime.now(timezone.utc),
        purpose=req.purpose,
        operator=req.operator,
        case_id=req.case_id,
        results=results,
    )
