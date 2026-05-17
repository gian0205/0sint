# 0sint — Consulta de CPF (OSINT)

Sistema de consulta de CPF que agrega múltiplas fontes OSINT brasileiras, baseado no projeto [osintbrazuca/osint-brazuca](https://github.com/osintbrazuca/osint-brazuca).

> **AVISO LEGAL — LGPD**
>
> Esta ferramenta destina-se exclusivamente a **investigação autorizada (OSINT/forense)**, due diligence, antifraude e cumprimento de obrigações legais. CPF é dado pessoal sensível protegido pela **Lei nº 13.709/2018 (LGPD)**. O uso indevido pode caracterizar crime e responsabilização cível/administrativa.
>
> Toda consulta é registrada em `audit.log` com operador, finalidade, identificação do caso e CPF mascarado, em conformidade com o princípio da **prestação de contas** (art. 6º, X da LGPD). O CPF completo nunca é gravado em log.

## Arquitetura

```
app/
├── main.py           FastAPI: /health, /sources, /lookup
├── aggregator.py     Executa adapters em paralelo
├── audit.py          Log de auditoria LGPD
├── cpf.py            Validação algorítmica, normalização, máscara, região
├── models.py         Schemas Pydantic
└── sources/          Adapters plugáveis
    ├── base.py
    ├── validator.py            Validação local (algoritmo)
    ├── links.py                Gera URLs de busca manual
    ├── receita_federal.py      CAPTCHA — retorna URL manual
    ├── situacao_cadastral.py   CAPTCHA — retorna URL manual
    ├── cadunico.py             CAPTCHA — retorna URL manual
    └── trt3.py                 CAPTCHA — retorna URL manual
```

### Fontes implementadas

| Fonte | Status | Tipo |
|---|---|---|
| `validator` | Funcional | Algoritmo local — dígitos verificadores + região fiscal |
| `manual_links` | Funcional | Gera URLs prontas (Google dorks, DuckDuckGo, portais) |
| `receita_federal` | Manual | Portal oficial — exige CAPTCHA |
| `situacao_cadastral` | Manual | Portal terceiro — exige CAPTCHA |
| `cadunico` | Manual | Dataprev — exige CPF + data nasc. + CAPTCHA |
| `trt3` | Manual | Certidão trabalhista — pode retornar nome — CAPTCHA |

> Fontes com CAPTCHA retornam `status: requires_manual_verification` e `manual_url` para abertura no navegador. Conforme decidido, **nenhum solver de CAPTCHA é integrado**.

## Como usar

### Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Subir a API

```bash
uvicorn app.main:app --reload
# http://localhost:8000/docs  (Swagger)
```

### Consulta via curl

```bash
curl -X POST http://localhost:8000/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "111.444.777-35",
    "purpose": "authorized_osint",
    "operator": "investigador-001",
    "case_id": "CASE-2026-001"
  }'
```

### Resposta (exemplo abreviado)

```json
{
  "cpf_masked": "***.444.777-**",
  "cpf_valid": true,
  "region": "ES, RJ",
  "purpose": "authorized_osint",
  "operator": "investigador-001",
  "case_id": "CASE-2026-001",
  "results": [
    {
      "source": "validator",
      "status": "ok",
      "data": { "valid": true, "formatted": "111.444.777-35", "region": "ES, RJ" }
    },
    {
      "source": "manual_links",
      "status": "ok",
      "data": { "manual_lookup_urls": { "google_dork_cpf": "...", "cadunico_dataprev": "..." } }
    },
    {
      "source": "receita_federal",
      "status": "requires_manual_verification",
      "manual_url": "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp"
    }
  ]
}
```

## Adicionar uma nova fonte

1. Crie `app/sources/minha_fonte.py` implementando `Source`:

```python
from ..models import SourceResult, SourceStatus
from .base import Source

class MinhaFonteSource(Source):
    name = "minha_fonte"
    description = "..."
    homepage = "https://..."

    async def query(self, cpf: str) -> SourceResult:
        # cpf vem normalizado (só dígitos)
        return SourceResult(source=self.name, status=SourceStatus.OK, data={...})
```

2. Registre em `app/sources/__init__.py`.

## Testes

```bash
pytest
```

## Roadmap (sugestões)

- Cache com TTL por CPF para reduzir chamadas externas
- Rate limiting por operador
- Autenticação JWT no endpoint `/lookup`
- Webhook quando resultado mudar (re-consulta agendada)
- Adapter para API Serpro (oficial, paga, sem CAPTCHA)

## Licença

MIT
