"""FastAPI app entry point."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .aggregator import aggregate
from .models import LookupRequest, LookupResponse
from .sources import REGISTRY


app = FastAPI(
    title="0sint — CPF Lookup",
    description=(
        "Sistema de consulta de CPF que agrega fontes OSINT brasileiras "
        "(baseado em github.com/osintbrazuca/osint-brazuca). "
        "Uso autorizado apenas (LGPD)."
    ),
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sources")
async def list_sources() -> dict[str, list[dict[str, object]]]:
    return {
        "sources": [
            {
                "name": s.name,
                "description": s.description,
                "requires_captcha": s.requires_captcha,
                "homepage": s.homepage,
            }
            for s in REGISTRY.values()
        ]
    }


@app.post("/lookup", response_model=LookupResponse)
async def lookup(req: LookupRequest) -> LookupResponse:
    if req.sources:
        unknown = [n for n in req.sources if n not in REGISTRY]
        if unknown:
            raise HTTPException(status_code=400, detail=f"Fonte(s) desconhecida(s): {unknown}")
    return await aggregate(req)
