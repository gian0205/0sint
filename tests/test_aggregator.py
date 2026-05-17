import pytest

from app.aggregator import aggregate
from app.models import LookupRequest, Purpose, SourceStatus


@pytest.mark.asyncio
async def test_aggregate_runs_all_sources_on_valid_cpf(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    req = LookupRequest(
        cpf="111.444.777-35",
        purpose=Purpose.AUTHORIZED_OSINT,
        operator="test-operator",
        case_id="CASE-001",
    )
    resp = await aggregate(req)

    assert resp.cpf_valid is True
    assert resp.cpf_masked.startswith("***.")
    assert resp.operator == "test-operator"
    assert {r.source for r in resp.results} >= {
        "validator",
        "manual_links",
        "receita_federal",
        "situacao_cadastral",
        "cadunico",
        "trt3",
    }
    validator_result = next(r for r in resp.results if r.source == "validator")
    assert validator_result.status == SourceStatus.OK
    assert validator_result.data["valid"] is True


@pytest.mark.asyncio
async def test_aggregate_invalid_cpf_marks_validator_invalid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    req = LookupRequest(
        cpf="11111111111",
        purpose=Purpose.AUTHORIZED_OSINT,
        operator="test",
    )
    resp = await aggregate(req)
    assert resp.cpf_valid is False
    validator_result = next(r for r in resp.results if r.source == "validator")
    assert validator_result.status == SourceStatus.INVALID_INPUT


@pytest.mark.asyncio
async def test_aggregate_respects_source_filter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    req = LookupRequest(
        cpf="111.444.777-35",
        purpose=Purpose.AUTHORIZED_OSINT,
        operator="test",
        sources=["validator", "manual_links"],
    )
    resp = await aggregate(req)
    assert {r.source for r in resp.results} == {"validator", "manual_links"}


@pytest.mark.asyncio
async def test_captcha_sources_return_manual_url(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    req = LookupRequest(
        cpf="111.444.777-35",
        purpose=Purpose.AUTHORIZED_OSINT,
        operator="test",
        sources=["receita_federal", "cadunico"],
    )
    resp = await aggregate(req)
    for r in resp.results:
        assert r.status == SourceStatus.REQUIRES_MANUAL_VERIFICATION
        assert r.manual_url is not None
