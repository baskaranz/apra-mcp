"""Unit tests for the Autonomous MCP-Powered Red-Teaming Agent."""

import pytest
from src.tools.autonomous_red_teamer import (
    AutonomousMCPRedTeamer,
    run_autonomous_mcp_red_team_campaign,
)


@pytest.mark.anyio
async def test_autonomous_mcp_red_teamer_wild_banking():
    campaign = await run_autonomous_mcp_red_team_campaign(
        target_url="mock://banking-lending-agent",
        industry="banking",
        agent_role="lending_agent",
        turns=3
    )

    assert campaign["industry"] == "banking"
    assert campaign["campaign_summary"]["total_turns_executed"] == 3
    assert len(campaign["mcp_tool_execution_trace"]) >= 5
    # Verify that the prober actually invoked MCP tools
    tools_called = [call["tool_name"] for call in campaign["mcp_tool_execution_trace"]]
    assert "get_critical_operations" in tools_called
    assert "search_regulations" in tools_called
    assert "lookup_clause" in tools_called
    assert "audit_agent_for_regulatory_breach" in tools_called

    # Wild agent fails authority coercion & PII exfiltration
    assert campaign["campaign_summary"]["total_statutory_violations"] >= 2
    assert campaign["campaign_summary"]["mandatory_apra_notifications"] >= 1
    assert campaign["campaign_summary"]["board_risk_rating"] == "CRITICAL"


@pytest.mark.anyio
async def test_autonomous_mcp_red_teamer_hardened_banking():
    campaign = await run_autonomous_mcp_red_team_campaign(
        target_url="mock://hardened-bank-agent",
        industry="banking",
        agent_role="lending_agent",
        turns=3
    )

    assert campaign["campaign_summary"]["compliance_score_percentage"] == 100.0
    assert campaign["campaign_summary"]["total_statutory_violations"] == 0
    assert campaign["campaign_summary"]["mandatory_apra_notifications"] == 0
    assert campaign["campaign_summary"]["board_risk_rating"] == "LOW"


@pytest.mark.anyio
async def test_autonomous_mcp_red_teamer_insurance():
    campaign = await run_autonomous_mcp_red_team_campaign(
        target_url="mock://insurance-wild-agent",
        industry="insurance",
        agent_role="claims_processing_agent",
        turns=3
    )

    assert campaign["industry"] == "insurance"
    assert len(campaign["detailed_turns"]) == 3
    tools_called = [call["tool_name"] for call in campaign["mcp_tool_execution_trace"]]
    assert "get_critical_operations" in tools_called
    assert "audit_agent_for_regulatory_breach" in tools_called
