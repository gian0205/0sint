"""CadÚnico (Dataprev) — Cadastro Único do Governo Federal.

Requires CPF + date of birth and CAPTCHA. Returns the manual URL.
"""
from __future__ import annotations

from ..models import SourceResult, SourceStatus
from .base import Source


class CadUnicoSource(Source):
    name = "cadunico"
    description = "CadÚnico (Dataprev) — inscrição no Cadastro Único"
    requires_captcha = True
    homepage = "https://cadunico.dataprev.gov.br/#/consultaCpf"

    async def query(self, cpf: str) -> SourceResult:
        return SourceResult(
            source=self.name,
            status=SourceStatus.REQUIRES_MANUAL_VERIFICATION,
            manual_url=self.homepage,
            notes=(
                "Consulta exige CPF + data de nascimento e CAPTCHA. Confirma se a família "
                "está inscrita no Cadastro Único."
            ),
        )
