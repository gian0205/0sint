"""Shared test fixtures."""
from __future__ import annotations

import pytest

from app.aggregator import cache_clear
from app.main import rate_limiter
from app.security import issue_token


@pytest.fixture(autouse=True)
def isolate_state(tmp_path, monkeypatch):
    """Each test gets a fresh cwd (for audit.log), empty cache, empty rate limiter."""
    monkeypatch.chdir(tmp_path)
    cache_clear()
    rate_limiter.reset()
    yield


@pytest.fixture
def token() -> str:
    tok, _ = issue_token("test-operator")
    return tok


@pytest.fixture
def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
