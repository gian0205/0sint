"""Receita Federal — Consulta Situação Cadastral do CPF.

The official endpoint requires CAPTCHA and is not currently automated.
This adapter returns the manual lookup URL.
"""
from __future__ import annotations

from ..models import SourceResult, SourceStatus
from .base import Source


class ReceitaFederalSource(Source):
    name = "receita_federal"
    description = "Receita Federal — situação cadastral do CPF (oficial)"
    requires_captcha = True
    homepage = (
        "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
    )

    async def query(self, cpf: str) -> SourceResult:
        return SourceResult(
            source=self.name,
            status=SourceStatus.REQUIRES_MANUAL_VERIFICATION,
            manual_url=self.homepage,
            notes=(
                "Portal oficial da Receita Federal exige CAPTCHA. Acesse a URL manualmente "
                "informando CPF e data de nascimento."
            ),
        )
