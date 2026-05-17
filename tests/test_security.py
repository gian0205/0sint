import time

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.config import settings
from app.security import current_operator, issue_token


def _creds(token: str, scheme: str = "Bearer") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)


def test_issue_and_decode_roundtrip():
    token, expiry = issue_token("alice")
    assert current_operator(_creds(token)) == "alice"
    assert expiry.timestamp() > time.time()


def test_missing_credentials_raises_401():
    with pytest.raises(HTTPException) as exc:
        current_operator(None)
    assert exc.value.status_code == 401


def test_wrong_scheme_raises_401():
    token, _ = issue_token("alice")
    with pytest.raises(HTTPException) as exc:
        current_operator(_creds(token, scheme="Basic"))
    assert exc.value.status_code == 401


def test_expired_token_raises_401():
    payload = {"sub": "alice", "exp": time.time() - 60}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(HTTPException) as exc:
        current_operator(_creds(token))
    assert exc.value.status_code == 401


def test_token_without_sub_raises_401():
    token = jwt.encode({"exp": time.time() + 60}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(HTTPException) as exc:
        current_operator(_creds(token))
    assert exc.value.status_code == 401
