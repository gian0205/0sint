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
├── main.py           FastAPI: /health, /sources, /auth/token, /lookup
├── aggregator.py     Executa adapters em paralelo + cache TTL
├── audit.py          Log de auditoria LGPD
├── cache.py          Cache in-memory TTL (LRU)
├── ratelimit.py      Token-bucket por operator
├── security.py       Emissão + verificação de JWT
├── config.py         Settings via env vars (OSINT_*)
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

### Segurança e operação

| Recurso | Como funciona |
|---|---|
| **JWT** | `POST /auth/token` com `admin_token` emite Bearer JWT (HS256). `/lookup` exige `Authorization: Bearer ...`. Operator extraído do claim `sub`. |
| **Cache TTL** | Chave = `cpf_digits + sources`. Cache hit retorna `cached: true` mas **ainda gera audit log** (accountability). LRU + TTL configurável. |
| **Rate limit** | Token-bucket por operator. 429 + header `Retry-After` quando excedido. |

### Configuração (env vars)

| Var | Default | Descrição |
|---|---|---|
| `OSINT_JWT_SECRET` | `dev-secret-change-me` | Chave HS256 — **trocar em produção** |
| `OSINT_JWT_ALGORITHM` | `HS256` | Algoritmo JWT |
| `OSINT_JWT_TTL_MINUTES` | `60` | Validade do token |
| `OSINT_ADMIN_TOKEN` | `dev-admin-token-change-me` | Segredo para emitir tokens — **trocar em produção** |
| `OSINT_CACHE_TTL_SECONDS` | `3600` | TTL do cache por CPF |
| `OSINT_CACHE_MAX_ENTRIES` | `1024` | Máximo de entradas no cache (LRU) |
| `OSINT_RATE_LIMIT_PER_MINUTE` | `30` | Requisições/min por operator |

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
```

Abra no navegador:
- `http://localhost:8000/` — UI de teste (formulário simples, sem curl)
- `http://localhost:8000/docs` — Swagger interativo
- `http://localhost:8000/generate?count=5` — gera CPFs sintaticamente válidos para teste

### Modo gratuito (zero custo, zero credencial externa)

As fontes que funcionam totalmente offline/grátis:
- `validator` — algoritmo (dígitos + região fiscal)
- `manual_links` — gera URLs de busca (Google dorks, DuckDuckGo, portais públicos)

As demais retornam `requires_manual_verification` com a URL para abrir manualmente.

### Fluxo completo via curl

```bash
# 1. Emitir token (admin_token vem da config)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"operator":"investigador-001","admin_token":"dev-admin-token-change-me"}' \
  | jq -r .access_token)

# 2. Consultar CPF
curl -X POST http://localhost:8000/lookup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "cpf": "111.444.777-35",
    "purpose": "authorized_osint",
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
  "cached": false,
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

## Deploy no Coolify

O projeto já vem com `Dockerfile` (multi-stage, non-root, healthcheck) e `docker-compose.yml`.

### 1. Gerar segredos fortes

```bash
python -c "import secrets; print('OSINT_JWT_SECRET=' + secrets.token_urlsafe(48))"
python -c "import secrets; print('OSINT_ADMIN_TOKEN=' + secrets.token_urlsafe(48))"
```

### 2. Criar o recurso no Coolify

No painel do Coolify:

1. **+ New Resource → Application**
2. Source: **Git Repository** → cole a URL do repo e a branch (`claude/cpf-lookup-osint-OVhH5` ou `main` depois do merge)
3. Build Pack: **Dockerfile** (Coolify detecta automaticamente)
4. Port: **8000**
5. Healthcheck Path: `/health`

### 3. Variáveis de ambiente (Coolify UI → Environment Variables)

| Key | Value | Obrigatório |
|---|---|:-:|
| `OSINT_JWT_SECRET` | string aleatória 48+ chars | ✅ |
| `OSINT_ADMIN_TOKEN` | string aleatória 48+ chars | ✅ |
| `OSINT_JWT_TTL_MINUTES` | `60` (ou outro) |   |
| `OSINT_CACHE_TTL_SECONDS` | `3600` |   |
| `OSINT_RATE_LIMIT_PER_MINUTE` | `30` |   |
| `OSINT_AUDIT_LOG_PATH` | `/data/audit.log` | ✅ |

### 4. Volume persistente (CRÍTICO para LGPD)

O `audit.log` precisa **sobreviver a restarts/redeploys** — é sua trilha de compliance.

Em Coolify → **Storage → + Add Persistent Storage**:
- Source path (no container): `/data`
- Name: `audit-data`

Sem isso, cada redeploy apaga o histórico de auditoria.

### 5. Deploy

Clica **Deploy**. O Coolify:
1. Clona o repo
2. Builda o Dockerfile (multi-stage, ~80MB final)
3. Sobe o container
4. Configura SSL/proxy reverso automaticamente

Quando subir, acesse `https://<seu-dominio>/` (UI HTML) ou `/docs` (Swagger).

### 6. Verificação pós-deploy

```bash
# health
curl https://<seu-dominio>/health

# emitir token (use o ADMIN_TOKEN real)
curl -X POST https://<seu-dominio>/auth/token \
  -H "Content-Type: application/json" \
  -d '{"operator":"prod-test","admin_token":"<seu-admin-token>"}'

# verificar audit log persistido (via shell do container no Coolify)
cat /data/audit.log
```

### Rodar local com docker-compose

```bash
cp .env.example .env
# edite .env com segredos fortes
docker compose up --build
```

## Roadmap (sugestões)

- Webhook quando resultado mudar (re-consulta agendada)
- Adapter para API Serpro (oficial, paga, sem CAPTCHA)
- Cache distribuído (Redis) para múltiplas instâncias
- Rate limit distribuído para deploy horizontal
- Refresh token / revogação por JTI

## Licença

MIT
