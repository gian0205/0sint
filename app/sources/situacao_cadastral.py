"""situacao-cadastral.com — agregador terceiro.

Listed in osint-brazuca. The site uses CAPTCHA and anti-bot protection.
This adapter returns the manual lookup URL with the CPF pre-filled.
"""
from __future__ import annotations

from ..cpf import normalize
from ..models import SourceResult, SourceStatus
from .base import Source


class SituacaoCadastralSource(Source):
    name = "situacao_cadastral"
    description = "situacao-cadastral.com — agregador terceiro (CAPTCHA)"
    requires_captcha = True
    homepage = "https://www.situacao-cadastral.com/"

    async def query(self, cpf: str) -> SourceResult:
        c = normalize(cpf)
        return SourceResult(
            source=self.name,
            status=SourceStatus.REQUIRES_MANUAL_VERIFICATION,
            manual_url=f"https://www.situacao-cadastral.com/?q={c}",
            notes="Portal terceiro com CAPTCHA. Use o link manual para consulta.",
        )
