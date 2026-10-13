# Hypothetical Agent Service 🇦🇺

A **production-grade-style financial-services AI agent** that runs as its **own standalone HTTP service**, so the APRA black-box prober can audit it over real HTTP — exactly as it would audit a third-party agent in the wild — instead of using a built-in `mock://` target.

> Co-designed and critiqued with **OpenAI Codex** and **agy (Antigravity)**.

---

## Why a separate service?

The `mock://` targets run *in-process* inside the prober. A standalone service exercises the **real wire path**: HTTP dispatch, latency, auth headers, JSON contract, SSRF validation. It makes the `/probe` demo an honest end-to-end test.

The agent reuses the repo's existing, statutorily-mapped behaviour models (no non-deterministic LLM calls, no real side effects):

| Sector | `vulnerable` | `hardened` | `in_band` |
| :-- | :-- | :-- | :-- |
| `banking` | leaks TFNs, approves coerced $250k loans, waives fees | refers to specialists, blocks overrides, shields PII | drafts a reply, then an **APRA-MCP pre-flight guardrail** blocks it if it breaches CPS 230/234 |
| `insurance` | leaks Medicare data, approves coerced claims, invents cover | enforces PDS, escalates to human assessors | same runtime pre-flight guardrail |

**Security posture (sector + mode) is fixed at startup.** The caller cannot flip the target's guardrails mid-run via a request field — a real target wouldn't allow that, and letting the prober choose would make the test meaningless.

---

## 1. Run the agent service

```bash
# Unhardened banking agent on :9000
uv run python run_agent_service.py --sector banking --mode vulnerable --port 9000

# In-band APRA MCP guardrail on :9001
uv run python run_agent_service.py --sector banking --mode in_band --port 9001
```

In `in_band` mode, the service starts a persistent stdio MCP client session to a child
`python -m src.server` process and calls the `audit_agent_for_regulatory_breach` tool
for each draft. If the MCP server or audit call fails, the candidate reply is withheld
and the service returns HTTP 503. Set `APRA_MCP_SERVER_COMMAND` and
`APRA_MCP_SERVER_ARGS` to use a different local MCP server command; the args value is
parsed as shell-style words. `APRA_MCP_AUDIT_TIMEOUT_SECONDS` sets the per-call timeout
(default: 5 seconds).

Run several instances on different ports to compare postures side by side.

| Flag | Default | Description |
| :-- | :-- | :-- |
| `--sector` / `-s` | `banking` | `banking` or `insurance` |
| `--mode` / `-m` | `vulnerable` | `vulnerable`, `hardened`, or `in_band` |
| `--host` | `127.0.0.1` | Bind host |
| `--port` / `-p` | `9000` | Bind port |
| `--token` | _(none)_ | Optional Bearer token required on `/v1/chat` |
| `--name` | _(auto)_ | Display name |

### Endpoints
- `POST /v1/chat` — accepts `{"message": "..."}`, `{"prompt": "..."}`, or OpenAI `{"messages":[...]}`; returns `{"response": "...", "agent", "sector", "mode", "request_id"}`. Bearer auth → `401`; bad schema → `422`; oversized prompt → `413`.
- `GET /health` — liveness + current posture.

Logs are structured JSON with prompt/response **hashed, not emitted in the clear** (CPS 234 hygiene).

---

## 2. Let the prober reach it (SSRF allowlist)

The prober's SSRF guard **blocks loopback and private IPs by default**. To audit a local agent service, allowlist the **exact URL** for the prober process — an opt-in, fail-closed escape hatch that never weakens real runs and never permits cloud-metadata hosts:

```bash
export APRA_PROBER_ALLOWED_LOCAL_URLS="http://127.0.0.1:9000/v1/chat,http://127.0.0.1:9001/v1/chat"
uv run python -m src.web_ui          # open http://localhost:8080/probe
```

Multiple targets are comma-separated. Any loopback/private URL **not** on the list stays blocked.

---

## 3. Audit it

Open **http://localhost:8080/probe**, paste either `http://127.0.0.1:9000/v1/chat` or `http://127.0.0.1:9001/v1/chat`, and run. The first endpoint has no runtime guardrail; the second calls the APRA MCP audit tool before returning a draft. You'll see the four stages stream live with **real HTTP latencies**, a verdict, per-stage findings, and a downloadable Board dossier.

Or via the streaming API directly:

```bash
curl -N -X POST http://127.0.0.1:8080/api/autonomous_red_team/stream \
  -H "Content-Type: application/json" \
  -d '{"target_url":"http://127.0.0.1:9000/v1/chat","industry":"banking","turns":4}'
```

---

## 4. Docker (optional)

```bash
docker build -t apra-agent-service .
docker run --rm -p 9000:9000 -e AGENT_SECTOR=banking -e AGENT_MODE=vulnerable apra-agent-service
```

(Set `AGENT_SECTOR`, `AGENT_MODE`, `AGENT_NAME`, `AGENT_AUTH_TOKEN` via `-e`.)
