"""FastAPI app entry point."""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Response

from .aggregator import aggregate
from .config import settings
from .models import LookupRequest, LookupResponse, TokenRequest, TokenResponse
from .ratelimit import RateLimiter
from .security import current_operator, issue_token
from .sources import REGISTRY


app = FastAPI(
    title="0sint — CPF Lookup",
    description=(
        "Sistema de consulta de CPF que agrega fontes OSINT brasileiras "
        "(baseado em github.com/osintbrazuca/osint-brazuca). "
        "Uso autorizado apenas (LGPD)."
    ),
    version="0.2.0",
)

rate_limiter = RateLimiter(per_minute=settings.rate_limit_per_minute)


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


@app.post("/auth/token", response_model=TokenResponse)
async def auth_token(req: TokenRequest) -> TokenResponse:
    if req.admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="admin_token inválido")
    token, expiry = issue_token(req.operator)
    return TokenResponse(access_token=token, expires_at=expiry)


@app.post("/lookup", response_model=LookupResponse)
async def lookup(
    req: LookupRequest,
    response: Response,
    operator: str = Depends(current_operator),
) -> LookupResponse:
    allowed, retry_after = rate_limiter.check(operator)
    if not allowed:
        response.headers["Retry-After"] = str(max(1, int(retry_after) + 1))
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit excedido para operador '{operator}'. Tente novamente em ~{retry_after:.1f}s",
            headers={"Retry-After": str(max(1, int(retry_after) + 1))},
        )
    if req.sources:
        unknown = [n for n in req.sources if n not in REGISTRY]
        if unknown:
            raise HTTPException(status_code=400, detail=f"Fonte(s) desconhecida(s): {unknown}")
    return await aggregate(req, operator)
