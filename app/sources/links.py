"""Manual investigation URLs.

Returns ready-to-click URLs for OSINT sources listed in osint-brazuca that
require manual interaction (CAPTCHA, login, etc.). The investigator opens
these in a browser to complete the lookup.
"""
from __future__ import annotations

from ..cpf import format_cpf, normalize
from ..models import SourceResult, SourceStatus
from .base import Source


class ManualLinksSource(Source):
    name = "manual_links"
    description = "URLs prontas para investigação manual em fontes OSINT brasileiras"
    homepage = "https://github.com/osintbrazuca/osint-brazuca"

    async def query(self, cpf: str) -> SourceResult:
        c = normalize(cpf)
        formatted = format_cpf(cpf)
        links = {
            "receita_federal_situacao": "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp",
            "cadunico_dataprev": "https://cadunico.dataprev.gov.br/#/consultaCpf",
            "situacao_cadastral_com": f"https://www.situacao-cadastral.com/?q={c}",
            "trt3_feitos_trabalhistas": "https://sistemas.trt3.jus.br/certidao/feitosTrabalhistas/aba1.emissao.htm",
            "google_dork_cpf": f'https://www.google.com/search?q=%22{formatted}%22',
            "google_dork_cpf_digits": f'https://www.google.com/search?q=%22{c}%22',
            "duckduckgo_cpf": f'https://duckduckgo.com/?q=%22{formatted}%22',
        }
        return SourceResult(
            source=self.name,
            status=SourceStatus.OK,
            data={"manual_lookup_urls": links},
            notes="Fontes listadas requerem interação humana (CAPTCHA/UI). Abra os links em um navegador autorizado.",
        )
