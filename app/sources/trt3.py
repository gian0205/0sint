"""TRT3 — Certidão de feitos trabalhistas.

Pode retornar nome completo a partir do CPF/CNPJ. Requer CAPTCHA.
"""
from __future__ import annotations

from ..models import SourceResult, SourceStatus
from .base import Source


class TRT3Source(Source):
    name = "trt3"
    description = "TRT3 — Certidão de feitos trabalhistas (pode retornar nome)"
    requires_captcha = True
    homepage = "https://sistemas.trt3.jus.br/certidao/feitosTrabalhistas/aba1.emissao.htm"

    async def query(self, cpf: str) -> SourceResult:
        return SourceResult(
            source=self.name,
            status=SourceStatus.REQUIRES_MANUAL_VERIFICATION,
            manual_url=self.homepage,
            notes=(
                "Portal do TRT-MG exige CAPTCHA. Útil para descobrir nome completo a partir de CPF."
            ),
        )
