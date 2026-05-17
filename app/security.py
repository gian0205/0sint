"""JWT issuance and verification."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings


_bearer = HTTPBearer(auto_error=False)


def issue_token(operator: str) -> tuple[str, datetime]:
    """Return (token, expiry_utc)."""
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_ttl_minutes)
    payload = {
        "sub": operator,
        "iat": datetime.now(timezone.utc),
        "exp": expiry,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expiry


def current_operator(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization Bearer token requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(status_code=401, detail="Token sem claim 'sub'")
    return sub
