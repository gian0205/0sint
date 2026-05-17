"""Local CPF validation — algorithm only, no network calls.

Always available and always safe to call.
"""
from __future__ import annotations

from ..cpf import format_cpf, is_valid, region
from ..models import SourceResult, SourceStatus
from .base import Source


class ValidatorSource(Source):
    name = "validator"
    description = "Validação algorítmica do CPF (dígitos verificadores) e região fiscal"
    homepage = "https://www.gov.br/receitafederal"

    async def query(self, cpf: str) -> SourceResult:
        valid = is_valid(cpf)
        return SourceResult(
            source=self.name,
            status=SourceStatus.OK if valid else SourceStatus.INVALID_INPUT,
            data={
                "valid": valid,
                "formatted": format_cpf(cpf) if valid else None,
                "region": region(cpf) if valid else None,
            },
            notes=None if valid else "CPF reprovado na verificação de dígitos",
        )
