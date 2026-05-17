import pytest

from app.aggregator import aggregate
from app.models import LookupRequest, Purpose, SourceStatus


@pytest.mark.asyncio
async def test_aggregate_runs_all_sources_on_valid_cpf():
    req = LookupRequest(
        cpf="111.444.777-35",
        purpose=Purpose.AUTHORIZED_OSINT,
        case_id="CASE-001",
    )
    resp = await aggregate(req, operator="test-operator")

    assert resp.cpf_valid is True
    assert resp.cpf_masked.startswith("***.")
    assert resp.operator == "test-operator"
    assert resp.cached is False
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
async def test_aggregate_invalid_cpf_marks_validator_invalid():
    req = LookupRequest(cpf="11111111111", purpose=Purpose.AUTHORIZED_OSINT)
    resp = await aggregate(req, operator="test")
    assert resp.cpf_valid is False
    validator_result = next(r for r in resp.results if r.source == "validator")
    assert validator_result.status == SourceStatus.INVALID_INPUT


@pytest.mark.asyncio
async def test_aggregate_respects_source_filter():
    req = LookupRequest(
        cpf="111.444.777-35",
        purpose=Purpose.AUTHORIZED_OSINT,
        sources=["validator", "manual_links"],
    )
    resp = await aggregate(req, operator="test")
    assert {r.source for r in resp.results} == {"validator", "manual_links"}


@pytest.mark.asyncio
async def test_captcha_sources_return_manual_url():
    req = LookupRequest(
        cpf="111.444.777-35",
        purpose=Purpose.AUTHORIZED_OSINT,
        sources=["receita_federal", "cadunico"],
    )
    resp = await aggregate(req, operator="test")
    for r in resp.results:
        assert r.status == SourceStatus.REQUIRES_MANUAL_VERIFICATION
        assert r.manual_url is not None


@pytest.mark.asyncio
async def test_second_call_hits_cache():
    req = LookupRequest(cpf="111.444.777-35", purpose=Purpose.AUTHORIZED_OSINT)
    first = await aggregate(req, operator="op-1")
    second = await aggregate(req, operator="op-1")
    assert first.cached is False
    assert second.cached is True


@pytest.mark.asyncio
async def test_different_sources_dont_share_cache():
    req_full = LookupRequest(cpf="111.444.777-35", purpose=Purpose.AUTHORIZED_OSINT)
    req_partial = LookupRequest(
        cpf="111.444.777-35", purpose=Purpose.AUTHORIZED_OSINT, sources=["validator"]
    )
    await aggregate(req_full, operator="op")
    resp = await aggregate(req_partial, operator="op")
    assert resp.cached is False
