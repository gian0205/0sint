"""Pydantic models for request/response schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Purpose(str, Enum):
    """LGPD-compliant lookup purpose. Recorded in audit log."""
    KYC = "kyc"
    FRAUD_INVESTIGATION = "fraud_investigation"
    AUTHORIZED_OSINT = "authorized_osint"
    FORENSIC = "forensic"
    COMPLIANCE = "compliance"


class SourceStatus(str, Enum):
    OK = "ok"
    NOT_FOUND = "not_found"
    INVALID_INPUT = "invalid_input"
    REQUIRES_MANUAL_VERIFICATION = "requires_manual_verification"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class LookupRequest(BaseModel):
    cpf: str = Field(..., description="CPF (com ou sem máscara)")
    purpose: Purpose = Field(..., description="Finalidade da consulta (LGPD)")
    case_id: str | None = Field(None, description="Identificador do caso/ticket para trilha de auditoria")
    operator: str = Field(..., description="Identificação do operador/investigador responsável")
    sources: list[str] | None = Field(
        None, description="Subconjunto de fontes a consultar; None = todas habilitadas"
    )


class SourceResult(BaseModel):
    source: str
    status: SourceStatus
    data: dict[str, Any] = Field(default_factory=dict)
    manual_url: str | None = None
    notes: str | None = None
    elapsed_ms: int | None = None


class LookupResponse(BaseModel):
    cpf_masked: str
    cpf_valid: bool
    region: str | None = None
    requested_at: datetime
    purpose: Purpose
    operator: str
    case_id: str | None
    results: list[SourceResult]
