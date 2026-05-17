from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_index_returns_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "0sint" in r.text


def test_generate_returns_valid_cpfs():
    from app.cpf import is_valid

    r = client.get("/generate?count=5")
    assert r.status_code == 200
    cpfs = r.json()["cpfs"]
    assert len(cpfs) == 5
    for cpf in cpfs:
        assert is_valid(cpf)


def test_generate_clamps_count():
    r = client.get("/generate?count=999")
    assert len(r.json()["cpfs"]) <= 50


def test_list_sources():
    r = client.get("/sources")
    assert r.status_code == 200
    names = {s["name"] for s in r.json()["sources"]}
    assert "validator" in names


def test_lookup_requires_authentication():
    r = client.post(
        "/lookup",
        json={"cpf": "111.444.777-35", "purpose": "authorized_osint"},
    )
    assert r.status_code == 401


def test_lookup_rejects_invalid_token():
    r = client.post(
        "/lookup",
        json={"cpf": "111.444.777-35", "purpose": "authorized_osint"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert r.status_code == 401


def test_auth_token_requires_admin_secret():
    r = client.post(
        "/auth/token",
        json={"operator": "investigator-1", "admin_token": "wrong"},
    )
    assert r.status_code == 401


def test_auth_token_issues_jwt_and_unlocks_lookup():
    r = client.post(
        "/auth/token",
        json={"operator": "investigator-1", "admin_token": settings.admin_token},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    token = body["access_token"]

    r2 = client.post(
        "/lookup",
        json={"cpf": "111.444.777-35", "purpose": "authorized_osint", "case_id": "C1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    payload = r2.json()
    assert payload["operator"] == "investigator-1"
    assert payload["cached"] is False


def test_lookup_returns_cached_on_second_call(auth_headers):
    body = {"cpf": "111.444.777-35", "purpose": "authorized_osint"}
    first = client.post("/lookup", json=body, headers=auth_headers)
    second = client.post("/lookup", json=body, headers=auth_headers)
    assert first.json()["cached"] is False
    assert second.json()["cached"] is True


def test_lookup_rejects_unknown_source(auth_headers):
    r = client.post(
        "/lookup",
        json={
            "cpf": "111.444.777-35",
            "purpose": "authorized_osint",
            "sources": ["validator", "does_not_exist"],
        },
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_rate_limit_returns_429(monkeypatch, auth_headers):
    from app.main import rate_limiter

    # Drain the bucket: take all tokens
    operator = "test-operator"
    bucket = rate_limiter._buckets.get(operator)
    if bucket is None:
        # prime the bucket by making one call
        client.post(
            "/lookup",
            json={"cpf": "111.444.777-35", "purpose": "authorized_osint"},
            headers=auth_headers,
        )
        bucket = rate_limiter._buckets[operator]
    bucket.tokens = 0

    r = client.post(
        "/lookup",
        json={"cpf": "111.444.777-35", "purpose": "authorized_osint"},
        headers=auth_headers,
    )
    assert r.status_code == 429
    assert "Retry-After" in r.headers
