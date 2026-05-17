"""Single-page HTML test UI served at GET /."""
from __future__ import annotations


INDEX_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>0sint — CPF Lookup (teste)</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
         max-width: 900px; margin: 2rem auto; padding: 0 1rem;
         background: #0d1117; color: #c9d1d9; }
  h1 { color: #58a6ff; margin-bottom: .3rem; }
  .sub { color: #8b949e; margin-bottom: 2rem; font-size: .9rem; }
  fieldset { border: 1px solid #30363d; border-radius: 6px;
             padding: 1rem 1.2rem; margin-bottom: 1.2rem; }
  legend { color: #58a6ff; padding: 0 .5rem; }
  label { display: block; margin: .6rem 0 .2rem; font-size: .85rem; color: #8b949e; }
  input, select, textarea { width: 100%; background: #161b22; color: #c9d1d9;
                            border: 1px solid #30363d; border-radius: 6px;
                            padding: .5rem .7rem; font: inherit; }
  button { background: #238636; color: white; border: 0; border-radius: 6px;
           padding: .6rem 1.2rem; font: inherit; cursor: pointer; margin-top: .8rem; }
  button:hover { background: #2ea043; }
  button.secondary { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; }
  pre { background: #161b22; border: 1px solid #30363d; border-radius: 6px;
        padding: 1rem; overflow-x: auto; font-size: .8rem; max-height: 500px; }
  .row { display: flex; gap: .5rem; align-items: end; }
  .row > * { flex: 1; }
  .row button { flex: 0 0 auto; }
  .status { font-size: .8rem; color: #8b949e; margin-top: .5rem; }
  .ok { color: #3fb950; }
  .err { color: #f85149; }
  a { color: #58a6ff; }
</style>
</head>
<body>
<h1>0sint — CPF Lookup</h1>
<div class="sub">
  UI de teste para investigação OSINT autorizada.
  <a href="/docs">Swagger</a> · <a href="/sources">/sources</a>
</div>

<fieldset>
  <legend>1. Token JWT</legend>
  <label>Operator (sua identificação)</label>
  <input id="operator" value="investigador-teste">
  <label>Admin token (dev default abaixo — trocar em prod)</label>
  <input id="admin" value="dev-admin-token-change-me">
  <button onclick="getToken()">Emitir token</button>
  <div class="status" id="tokenStatus"></div>
</fieldset>

<fieldset>
  <legend>2. CPF para consultar</legend>
  <div class="row">
    <div>
      <label>CPF (com ou sem máscara)</label>
      <input id="cpf" placeholder="111.444.777-35">
    </div>
    <button class="secondary" onclick="genCpf()">Gerar CPF de teste</button>
  </div>
  <label>Finalidade (LGPD)</label>
  <select id="purpose">
    <option value="authorized_osint">authorized_osint</option>
    <option value="forensic">forensic</option>
    <option value="fraud_investigation">fraud_investigation</option>
    <option value="kyc">kyc</option>
    <option value="compliance">compliance</option>
  </select>
  <label>Case ID (opcional)</label>
  <input id="caseId" placeholder="CASE-2026-001">
  <button onclick="lookup()">Consultar</button>
  <div class="status" id="lookupStatus"></div>
</fieldset>

<fieldset>
  <legend>3. Resultado</legend>
  <pre id="result">// aguardando consulta</pre>
</fieldset>

<script>
let token = null;

function setStatus(id, msg, cls) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = "status " + (cls || "");
}

async function getToken() {
  try {
    const r = await fetch("/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        operator: document.getElementById("operator").value,
        admin_token: document.getElementById("admin").value,
      }),
    });
    const data = await r.json();
    if (!r.ok) { setStatus("tokenStatus", "erro: " + JSON.stringify(data), "err"); return; }
    token = data.access_token;
    setStatus("tokenStatus", "token ok — expira em " + data.expires_at, "ok");
  } catch (e) { setStatus("tokenStatus", "erro: " + e, "err"); }
}

async function genCpf() {
  const r = await fetch("/generate");
  const data = await r.json();
  document.getElementById("cpf").value = data.cpfs[0];
}

async function lookup() {
  if (!token) { setStatus("lookupStatus", "emita um token primeiro", "err"); return; }
  setStatus("lookupStatus", "consultando...", "");
  try {
    const r = await fetch("/lookup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
      },
      body: JSON.stringify({
        cpf: document.getElementById("cpf").value,
        purpose: document.getElementById("purpose").value,
        case_id: document.getElementById("caseId").value || null,
      }),
    });
    const data = await r.json();
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
    if (r.ok) setStatus("lookupStatus", data.cached ? "ok (cached)" : "ok", "ok");
    else setStatus("lookupStatus", "erro " + r.status, "err");
  } catch (e) { setStatus("lookupStatus", "erro: " + e, "err"); }
}
</script>
</body>
</html>
"""
