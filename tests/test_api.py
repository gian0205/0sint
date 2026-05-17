from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_sources():
    r = client.get("/sources")
    assert r.status_code == 200
    names = {s["name"] for s in r.json()["sources"]}
    assert "validator" in names
    assert "receita_federal" in names


def test_lookup_requires_purpose_and_operator(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = client.post("/lookup", json={"cpf": "111.444.777-35"})
    assert r.status_code == 422


def test_lookup_returns_aggregated_results(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = client.post(
        "/lookup",
        json={
            "cpf": "111.444.777-35",
            "purpose": "authorized_osint",
            "operator": "ag-001",
            "case_id": "CASE-1",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["cpf_valid"] is True
    assert body["cpf_masked"] == "***.444.777-**"
    assert any(res["source"] == "validator" for res in body["results"])


def test_lookup_rejects_unknown_source(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = client.post(
        "/lookup",
        json={
            "cpf": "111.444.777-35",
            "purpose": "authorized_osint",
            "operator": "ag-001",
            "sources": ["validator", "does_not_exist"],
        },
    )
    assert r.status_code == 400
