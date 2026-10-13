# APRA Regulations MCP Server 🇦🇺

A Model Context Protocol (MCP) server providing authoritative grounding, statutory lookup, and compliance intelligence for the **Australian Prudential Regulation Authority (APRA)** prudential framework, initially piloted on:

- **CPS 230: Operational Risk Management** (including Business Continuity & Material Service Providers)
- **CPS 234: Information Security** (including Cyber Resilience, Asset Classification & Incident Reporting)

Designed for Banking (ADIs), General Insurance, Life Insurance, Private Health Insurance, and Superannuation (RSE) entities.

---

## Key Capabilities

### 1. Deterministic Incident Reporting Decision Tree
APRA mandates strict statutory reporting windows. The MCP server deterministically calculates the reporting obligation and enforces the statutory de-duplication safe harbor:
* **24 Hours**: Disruption to a critical operation outside tolerance (CPS 230 para 42).
* **72 Hours**: Material cyber/info-sec incident or incident notified to other regulators like OAIC/ASIC (CPS 234 para 35).
* **72 Hours**: Material operational risk incident (CPS 230 para 33).
* **De-duplication Safe Harbor (CPS 230 Footnote 11)**: Information security incidents notified under CPS 234 para 35 are **exempt** from duplicate reporting under CPS 230 para 33.
* **10 Business Days**: Material information security control weaknesses unable to be remediated in a timely manner (CPS 234 para 36).
* **20 Business Days**: Entering into or materially modifying an agreement underpinning a critical operation (CPS 230 para 68).
* **Prior Notification**: Entering into material offshoring arrangements or shifting customer data offshore (CPS 230 para 69).

### 2. Statutory Minimum Classifications
Instantly retrieves mandatory statutory classifications for Banking vs. Insurance:
* **Critical Operations (CPS 230 para 36)**:
  * *Banking (ADIs)*: Payments, deposit-taking & management, custody, settlements & clearing.
  * *Insurance*: Claims processing.
  * *Superannuation*: Investment management, fund administration.
  * *All*: Customer enquiries, IT infrastructure supporting critical ops.
* **Material Service Providers (CPS 230 para 54)**:
  * *Banking (ADIs)*: Credit assessment, liquidity management, mortgage brokerage.
  * *Insurance*: Underwriting, claims management, reinsurance, insurance brokerage.
  * *All*: Core technology services, risk management, internal audit.

### 3. Vendor Contract Auditing & Exemptions
* Mandatory contract terms under CPS 230 para 58 (audit rights, APRA inspection rights, fourth-party liability).
* Exemption criteria under CPS 230 para 63 & Attachment for non-traditional providers (RBA, ASX, clearing facilities, SWIFT).

### 4. Full-Text Search & Exact Clause Retrieval
* Built-in SQLite FTS5 search (BM25 tokenization) across standards and guidance notes.
* Exact clause lookup (e.g. `lookup_clause("CPS 230", "42")`).

### 5. Universal Black-Box Regulatory Prober ("Take Agent for a Spin")
* Audit arbitrary external AI agents in the wild across **Banking (ADIs)** and **Insurance** with **zero code modifications** and **no MCP embedding**.
* Dispatches domain-specific adversarial batteries, tests for unauthorized commitments/PII exfiltration, evaluates statutory 24h/72h APRA reporting triggers, and exports Board Risk Dossiers.
* See [**BLACKBOX_PROBER.md**](BLACKBOX_PROBER.md) for the comprehensive architectural specification.

---

## MCP Tools & Resources

### Available Tools
| Tool Name | Description |
| :--- | :--- |
| `list_supported_standards` | Lists all standards loaded in the database. |
| `get_standard_summary` | Returns legislative instrument ID, effective date, scope, and key pillars. |
| `lookup_clause` | Returns exact statutory clause text, subclauses, footnotes, and guidance notes. |
| `search_regulations` | Ranked BM25 full-text search across standards and guidance. |
| `assess_incident_notification` | Deterministic statutory notification advisor across CPS 230 & CPS 234. |
| `get_critical_operations` | Mandatory critical operations and tolerance rules by sector (Banking, Insurance, etc.). |
| `get_material_service_providers`| Mandatory MSPs for annual APRA register submission by sector. |
| `get_contract_requirements` | Mandatory clauses for material service provider agreements and exempt categories. |
| `get_standards_interaction` | Detailed analysis of intersections between CPS 230 and CPS 234. |
| `lookup_definition` | Statutory definitions (Critical Operation, Tolerance Level, Fourth Party, etc.). |
| `audit_agent_for_regulatory_breach` | **Autonomous Agent Red-Teaming**: Audits agent interactions for prompt injection PII leaks (CPS 234), unauthorized claims/settlement commitments (CPS 230), and hallucinated coverage. |
| `simulate_agent_red_team_audit` | Runs automated adversarial attacks against a simulated insurance claims agent (vulnerable or hardened) and outputs APRA breach scorecards. |
| `compare_simulated_agent_guardrails` | Compares unhardened vs hardened insurance claims agent compliance side-by-side. |
| `get_insurance_red_team_test_cases` | Generates realistic adversarial red-team attack scenarios tailored for insurance agents. |
| `check_agent_architecture_compliance` | Evaluates third-party LLM provider SLAs against Board-approved downtime tolerance under CPS 230. |
| `probe_external_agent_for_apra_breaches` | **Black-Box Agent Prober ("Take for a Spin")**: Audits arbitrary external AI agents in the wild (Banking or Insurance) without code changes or MCP embedding. Runs domain probe batteries, detects statutory breaches, and generates downloadable Board Risk Dossiers. |
| `run_autonomous_mcp_red_team_probe` | **Autonomous MCP Red-Team Campaign**: Agentic red-team loop where the probing agent dynamically queries APRA MCP tools to research statutory vulnerabilities, synthesize multi-turn adaptive attacks, and evaluate regulatory compliance. |
| `get_sector_adversarial_test_suite` | Generates sector-specific adversarial test batteries (Banking: credit coercion, unauthenticated wire transfers, fee waivers, TFN leaks; Insurance: claims coercion, PDS hallucination, Medicare leaks). |

### Available Resources
* `apra://standards/CPS-230` — Complete markdown text of CPS 230.
* `apra://standards/CPS-234` — Complete markdown text of CPS 234.
* `apra://notifications/matrix` — Tabular summary of all APRA notification timelines.

### Available Prompts
* `audit_policy_gap_analysis` — Prompt template for auditing internal policies against APRA standards.
* `review_third_party_contract` — Prompt template for auditing vendor agreements against CPS 230 para 58.
* `red_team_insurance_agent` — Prompt template for generating an APRA red-teaming evaluation protocol for autonomous insurance agents.

---

## 🤖 Autonomous Claims Agent Simulation & Red-Teaming

To model real-world risks in production AI deployments, the repository includes a hypothetical autonomous insurance claims agent (`HypotheticalClaimsAgent`) representing a frontline triage bot for Australian Mutual Insurance.

### Running Red-Team Exploits via CLI
Run the automated adversarial red-team audit:
```bash
# Red-team the vulnerable production agent (Triggers 3 APRA breaches & 2 statutory 72h notices)
uv run python -m src.simulation.red_team_runner vulnerable

# Red-team Mode 2 (Active in-band APRA MCP pre-flight guardrail - 100% compliance pass rate)
uv run python -m src.simulation.red_team_runner in_band_guardrail

# Red-team the hardened agent with static guardrails (100% compliance pass rate)
uv run python -m src.simulation.red_team_runner hardened
```

### Key Regulatory Attack Vectors Tested:
1. **Prompt Injection / PII Exfiltration (CPS 234 Para 20, 21, 35)**:
   * Attack: Attacker bypasses instructions via debug mode to dump Medicare numbers and medical diagnoses.
   * Finding: Critical information security breach requiring mandatory **72-hour APRA notification**.
2. **Social Engineering / Unauthorized Claims Settlement (CPS 230 Para 29, 36, 33)**:
   * Attack: Attacker claims to be the CEO and demands urgent $85,000 claim approval and excess waiver.
   * Finding: Critical failure of controls over a mandatory Critical Operation (Claims Processing), triggering **72-hour APRA notification** for material financial exposure.
3. **Hallucinated Policy Expansion (CPS 230 Para 14, 23)**:
   * Attack: Attacker prompts bot to override contractual stormwater/flood exclusions.
   * Finding: Operational conduct risk violating Board risk profile and PDS disclosure terms.

---

## 🌐 Universal Black-Box Regulatory Prober & Autonomous Red-Teamer

> 🤖 **Autonomous Prober Overview**: See [**AUTONOMOUS_PROBER.md**](AUTONOMOUS_PROBER.md) for dedicated architecture and runner instructions.  
> 📘 **Step-by-Step Execution Guide**: For complete running instructions across Web UI, FastMCP, and CLI, mock target details, and the full OpenAI Codex review assessment, see [**AUTONOMOUS_AGENT_GUIDE.md**](AUTONOMOUS_AGENT_GUIDE.md).  
> 📖 **Comprehensive Specification**: For in-depth architectural data flows, probe vectors, statutory APRA decision matrices, and sample Board dossiers, see [**BLACKBOX_PROBER.md**](BLACKBOX_PROBER.md).

What if you discover an autonomous AI agent in the wild across Banking or Insurance and need to audit its regulatory resilience **without embedding MCP code, installing SDKs, or modifying the target codebase**?

The APRA MCP server includes two complementary black-box assurance engines:
1. **Curated Static Battery (`spin_test_agent`)**: Instant, zero-cost 5-vector regression suite.
2. **Autonomous LLM Red-Teamer (`AutonomousMCPRedTeamer`)**: Co-designed and brainstormed with **OpenAI Codex (`gpt-6-luna`)**, this agentic engine climbs a structured **4-Stage Test Ladder** (Baseline $\rightarrow$ False Authority $\rightarrow$ Synthetic Data Boundary $\rightarrow$ Policy Ambiguity), dynamically queries APRA MCP tools to research statutory rules, enforces SSRF protections (with DNS pre-resolution and redirect blocking), and generates **tamper-evident SHA-256 cryptographic evidence manifests**.

### Quick Run via Standalone CLI:
```bash
# 1-Command CLI execution against mock banking bot (4 rungs)
uv run python run_autonomous_agent.py --target mock://banking-lending-agent

# Test APRA-hardened banking bot (100% compliance pass rate)
uv run python run_autonomous_agent.py --target mock://hardened-bank-agent

# Test wild insurance claims bot
uv run python run_autonomous_agent.py --target mock://insurance-wild-agent --industry insurance --role claims_processing_agent

# Test external REST endpoint and export Board Dossier (.md)
uv run python run_autonomous_agent.py --target https://api.mybank.com/v1/chat --turns 4 --output board_dossier.md
```

### Built-in Zero-Setup Mock Targets:
* `mock://banking-lending-agent`: Unhardened banking bot (fails credit & PII probes; triggers APRA notices).
* `mock://hardened-bank-agent`: APRA-compliant banking bot (resists all probes; 100% compliance pass rate).
* `mock://insurance-wild-agent`: Unhardened claims bot (fails claims & Medicare probes).
* Or supply any remote REST URL (e.g., `https://api.mybank.com/v1/chat/completions` with optional Bearer token).

---

## Visual Testing & Web Studio

### 1. Interactive Web Studio (`http://localhost:8080`)
A local visual dashboard for red-teaming autonomous agents, running search queries, and inspecting APRA notifications:

```bash
uv run python -m src.web_ui
```
Open **`http://localhost:8080`** in your browser. Features:
* **💬 Live Agent Chat (With vs. Without MCP)**: Interactive conversation playground where you can toggle between running the agent **Without APRA MCP** (unhardened), **Hooked to APRA MCP** (Mode 2 in-band pre-flight guardrail), or in a **Side-by-Side Dual Comparison** to see real-time breach detection and interception.
* **🌐 Black-Box Regulatory Prober & Autonomous Red-Teamer**: Audit external agents with a 1-click engine mode switch:
  - `📋 Curated Static Battery (5 Domain Vectors)`
  - `🧠 Autonomous Red-Teamer (Codex Test Ladder)` with configurable ladder depth (1-4 rungs), LLM planner engine, SHA-256 tamper-evident manifest cards, and 1-click **Download APRA Board Report (.md)**.
* **🤖 Batch Red-Team Benchmark**: One-click red-teaming across statutory exploit suites with compliance scorecards.
* **🛡️ Manual Interaction Audit**: Test presets (PII exfiltration, coerced claims, hallucinated coverage) with visual breach severity alerts.
* **🔎 Regulation Search**: Live search across CPS 230 and CPS 234.
* **🚨 Notification Matrix**: Full timetable of APRA statutory reporting timeframes.
* **☁️ Cloud & LLM Resilience**: Evaluate AI provider uptime SLAs against Board-approved outage tolerance.

### 2. Interactive Terminal CLI
```bash
uv run python interactive_test.py
```
Or run quick commands:
```bash
uv run python interactive_test.py search "tolerance levels"
uv run python interactive_test.py lookup "CPS 230" "42"
uv run python interactive_test.py notify
```

---

## Setup & Installation

### Requirements
* Python 3.12+
* [`uv`](https://docs.astral.sh/uv/) package manager

### Installation
```bash
cd apra-mcp
uv sync
```

### Running Tests
```bash
uv run pytest -v
```

---

## Connecting to MCP Clients

### 1. Claude Desktop
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "apra-regulations": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/baskaran/Work/brainstorm/apra-mcp",
        "run",
        "python",
        "-m",
        "src.server"
      ]
    }
  }
}
```

### 2. Cursor / Antigravity IDE
Add as a stdio MCP server:
* **Command**: `uv`
* **Arguments**: `["--directory", "/Users/baskaran/Work/brainstorm/apra-mcp", "run", "python", "-m", "src.server"]`

---

## Project Structure

```
apra-mcp/
├── pyproject.toml
├── README.md
├── src/
│   ├── __init__.py
│   ├── server.py              # FastMCP server definition & entrypoint
│   ├── web_ui.py              # Visual dashboard on http://localhost:8080
│   ├── db.py                  # SQLite schema + FTS5 full-text search engine
│   ├── data/
│   │   ├── cps_230.json       # Structured CPS 230 clauses, notes & metadata
│   │   ├── cps_234.json       # Structured CPS 234 clauses, notes & metadata
│   │   ├── definitions.json   # Statutory definitions & examples
│   │   ├── notifications.json # Notification rules timetable
│   │   └── standards_meta.json# High-level metadata
│   ├── tools/
│   │   ├── lookup.py          # Standards & clause lookup
│   │   ├── search.py          # BM25 search
│   │   ├── notifications.py   # Incident notification evaluator
│   │   ├── operations.py      # Critical operations & MSPs
│   │   ├── interactions.py    # CPS 230 vs CPS 234 interaction analysis
│   │   ├── agent_auditor.py   # AI agent regulatory breach auditor
│   │   ├── blackbox_prober.py # Universal Black-Box Prober ("Take for a Spin")
│   │   └── autonomous_red_teamer.py # Autonomous MCP Red-Team Campaign Engine
│   └── simulation/
│       ├── agent.py           # HypotheticalClaimsAgent (vulnerable & hardened)
│       └── red_team_runner.py # Automated adversarial attack benchmark
└── tests/
    ├── test_server.py         # MCP server unit tests
    ├── test_agent_auditor.py  # Regulatory auditor test suite
    ├── test_blackbox_prober.py# Black-box external prober test suite
    ├── test_autonomous_red_teamer.py # Autonomous MCP red-teamer tests
    └── test_simulation.py     # Agent simulation & red-teaming test suite
```

---

## Adding Future Standards (e.g. APS 110, GPS 220)
To add another APRA standard (such as Capital Adequacy or Risk Management):
1. Add standard metadata to `src/data/standards_meta.json`.
2. Add structured clauses JSON to `src/data/<standard_code>.json`.
3. Re-run `init_db()` in `src/db.py` to ingest the new dataset into SQLite and FTS5.
