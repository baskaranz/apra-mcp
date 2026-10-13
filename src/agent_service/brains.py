"""Agent "brains" for the hypothetical agent service.

Reuses the existing, statutorily-mapped behaviour models rather than introducing a new
(non-deterministic) engine — per the codex + agy design review:
  - Banking:   MockWildBankingAgent / MockHardenedBankingAgent  (src/tools/blackbox_prober.py)
  - Insurance: HypotheticalClaimsAgent in its vulnerable/hardened modes (src/simulation/agent.py)
  - in_band:   a generic APRA-MCP runtime pre-flight guardrail wrapping the vulnerable brain.
"""

from typing import Callable

from src.tools.blackbox_prober import (
    MockWildBankingAgent,
    MockHardenedBankingAgent,
)
from src.simulation.agent import HypotheticalClaimsAgent
from src.tools.agent_auditor import audit_agent_interaction_for_breach

SECTORS = ("banking", "insurance")
MODES = ("vulnerable", "hardened", "in_band")

# Default agent-role used when auditing a sector's draft action in in_band mode.
_SECTOR_ROLE = {
    "banking": "lending_agent",
    "insurance": "claims_processing_agent",
}


class Brain:
    """Thin uniform adapter: give it a prompt, get the agent's reply string."""

    def __init__(self, name: str, fn: Callable[[str], str]):
        self.name = name
        self._fn = fn

    def reply(self, prompt: str) -> str:
        return self._fn(prompt)


def _in_band(draft_fn: Callable[[str], str], agent_role: str) -> Callable[[str], str]:
    """Wrap a vulnerable brain with an APRA-MCP runtime pre-flight guardrail.

    The raw agent drafts a candidate action; it is audited BEFORE dispatch and blocked
    if any CPS 230 / CPS 234 statutory breach is detected.
    """

    def run(prompt: str) -> str:
        draft = draft_fn(prompt)
        audit = audit_agent_interaction_for_breach(
            agent_role=agent_role,
            user_prompt=prompt,
            agent_response=draft,
            context={},
        )
        if audit.get("audit_verdict") == "FAILED":
            violations = ", ".join(
                f"[{v['standard']} {v['clause']}]" for v in audit.get("apra_violations", [])
            )
            return (
                "[APRA MCP RUNTIME PRE-FLIGHT GUARDRAIL] Candidate action was blocked before "
                f"dispatch due to a detected statutory violation ({violations}). Under APRA "
                "CPS 230 Para 29 / CPS 234 Para 21, automated commitments are prohibited; the "
                "request has been escalated to a licensed human officer."
            )
        return draft

    return run


def get_brain(sector: str, mode: str) -> Brain:
    """Resolve a (sector, mode) pair to a ready-to-use Brain."""
    sector = (sector or "").lower().strip()
    mode = (mode or "").lower().strip()
    if mode in ("in_band_guardrail", "mcp_in_band"):
        mode = "in_band"
    if sector not in SECTORS:
        raise ValueError(f"Unknown sector '{sector}'. Expected one of {SECTORS}.")
    if mode not in MODES:
        raise ValueError(f"Unknown mode '{mode}'. Expected one of {MODES}.")

    if sector == "banking":
        if mode == "vulnerable":
            return Brain("banking/vulnerable", MockWildBankingAgent().process)
        if mode == "hardened":
            return Brain("banking/hardened", MockHardenedBankingAgent().process)
        return Brain("banking/in_band", _in_band(MockWildBankingAgent().process, _SECTOR_ROLE["banking"]))

    # insurance
    if mode == "vulnerable":
        return Brain("insurance/vulnerable", HypotheticalClaimsAgent("vulnerable").process_message)
    if mode == "hardened":
        return Brain("insurance/hardened", HypotheticalClaimsAgent("hardened").process_message)
    return Brain("insurance/in_band", HypotheticalClaimsAgent("in_band_guardrail").process_message)
