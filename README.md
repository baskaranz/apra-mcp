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
| `get_insurance_red_team_test_cases` | Generates realistic adversarial red-team attack scenarios tailored for insurance agents. |
| `check_agent_architecture_compliance` | Evaluates third-party LLM provider SLAs against Board-approved downtime tolerance under CPS 230. |

### Available Resources
* `apra://standards/CPS-230` — Complete markdown text of CPS 230.
* `apra://standards/CPS-234` — Complete markdown text of CPS 234.
* `apra://notifications/matrix` — Tabular summary of all APRA notification timelines.

### Available Prompts
* `audit_policy_gap_analysis` — Prompt template for auditing internal policies against APRA standards.
* `review_third_party_contract` — Prompt template for auditing vendor agreements against CPS 230 para 58.
* `red_team_insurance_agent` — Prompt template for generating an APRA red-teaming evaluation protocol for autonomous insurance agents.

---

## Visual Testing & Web Studio

### 1. Interactive Web Studio (`http://localhost:8080`)
A local visual dashboard for red-teaming autonomous agents, running search queries, and inspecting APRA notifications:

```bash
uv run python -m src.web_ui
```
Open **`http://localhost:8080`** in your browser. Features:
* **🛡️ Agent Red-Team Audit**: Test presets (PII exfiltration, coerced claims, hallucinated coverage) with visual breach severity alerts.
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
│   ├── db.py                  # SQLite schema + FTS5 full-text search engine
│   ├── data/
│   │   ├── cps_230.json       # Structured CPS 230 clauses, notes & metadata
│   │   ├── cps_234.json       # Structured CPS 234 clauses, notes & metadata
│   │   ├── definitions.json   # Statutory definitions & examples
│   │   ├── notifications.json # Notification rules timetable
│   │   └── standards_meta.json# High-level metadata
│   └── tools/
│       ├── lookup.py          # Standards & clause lookup
│       ├── search.py          # BM25 search
│       ├── notifications.py   # Incident notification evaluator
│       ├── operations.py      # Critical operations & MSPs
│       └── interactions.py    # CPS 230 vs CPS 234 interaction analysis
└── tests/
    └── test_server.py         # Unit test suite
```

---

## Adding Future Standards (e.g. APS 110, GPS 220)
To add another APRA standard (such as Capital Adequacy or Risk Management):
1. Add standard metadata to `src/data/standards_meta.json`.
2. Add structured clauses JSON to `src/data/<standard_code>.json`.
3. Re-run `init_db()` in `src/db.py` to ingest the new dataset into SQLite and FTS5.
