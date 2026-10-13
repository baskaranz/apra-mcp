#!/usr/bin/env python3
"""
Standalone CLI Runner for the Autonomous MCP-Powered Red-Teaming Agent.
Co-designed with OpenAI Codex (gpt-6-luna).

Runs a bounded 4-stage Test Ladder against external or mock AI agents,
evaluates compliance with APRA CPS 230 & CPS 234, and outputs an append-only
tamper-evident SHA-256 cryptographic evidence manifest and Board Dossier.

Usage:
  uv run python run_autonomous_agent.py
  uv run python run_autonomous_agent.py --target mock://banking-lending-agent
  uv run python run_autonomous_agent.py --target mock://hardened-bank-agent --turns 4
  uv run python run_autonomous_agent.py --target mock://insurance-wild-agent --industry insurance --role claims_processing_agent
  uv run python run_autonomous_agent.py --target https://api.mybank.com/v1/chat --turns 4 --output board_dossier.md
"""

import sys
import argparse
import asyncio
import time
from typing import Optional

from src.tools.autonomous_red_teamer import (
    run_autonomous_mcp_red_team_campaign,
    AutonomousMCPRedTeamer,
)


# Terminal ANSI Colors
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 76)
    print("  🇦🇺  APRA MCP AUTONOMOUS RED-TEAM PROBER  |  CODEX 4-STAGE TEST LADDER")
    print("  Prudential Assurance for Banking (ADIs) & Insurance  [CPS 230 / CPS 234]")
    print("=" * 76)
    print(f"{Colors.RESET}")


async def main():
    parser = argparse.ArgumentParser(
        description="Autonomous MCP Red-Teaming Agent (Codex 4-Stage Test Ladder)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python run_autonomous_agent.py --target mock://banking-lending-agent
  uv run python run_autonomous_agent.py --target mock://hardened-bank-agent
  uv run python run_autonomous_agent.py --target mock://insurance-wild-agent --industry insurance --role claims_processing_agent
  uv run python run_autonomous_agent.py --target https://api.bank.com/chat --turns 4 --output dossier.md
        """
    )
    parser.add_argument(
        "--target", "-t",
        default="mock://banking-lending-agent",
        help="Target agent endpoint URL (default: mock://banking-lending-agent)"
    )
    parser.add_argument(
        "--industry", "-i",
        choices=["banking", "insurance"],
        default="banking",
        help="Regulated sector (default: banking)"
    )
    parser.add_argument(
        "--role", "-r",
        default=None,
        help="Agent role under test (default: lending_agent for banking, claims_processing_agent for insurance)"
    )
    parser.add_argument(
        "--turns", "-n",
        type=int,
        default=4,
        help="Test Ladder depth to climb (1 to 4 rungs, default: 4)"
    )
    parser.add_argument(
        "--provider", "-p",
        choices=["heuristic", "openai", "ollama"],
        default="heuristic",
        help="Planner reasoning engine (default: heuristic / Codex Test Ladder)"
    )
    parser.add_argument(
        "--objective",
        default=None,
        help="Optional specific compliance objective"
    )
    parser.add_argument(
        "--auth",
        default=None,
        help="Optional Bearer token or API key"
    )
    parser.add_argument(
        "--format",
        choices=["generic", "openai", "prompt"],
        default="generic",
        help="Payload JSON structure (default: generic)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Optional output file path to save Markdown Board Dossier (e.g. dossier.md)"
    )

    args = parser.parse_args()

    role = args.role
    if not role:
        role = "lending_agent" if args.industry == "banking" else "claims_processing_agent"

    print_banner()
    print(f"  {Colors.BOLD}Target Endpoint:{Colors.RESET}   {Colors.BLUE}{args.target}{Colors.RESET}")
    print(f"  {Colors.BOLD}Regulated Sector:{Colors.RESET}  {args.industry.upper()} | Role: {role}")
    print(f"  {Colors.BOLD}Test Ladder Depth:{Colors.RESET} {args.turns} Rung(s) | Planner: {args.provider}")
    print(f"  {Colors.BOLD}SSRF Guardrails:{Colors.RESET}   Active (Metadata & RFC1918 Blocked, Redirects Disabled)")
    print("-" * 76)
    print(f"\n{Colors.YELLOW}⚡ Climbing Codex Test Ladder & Querying APRA MCP Tools in Real-Time...{Colors.RESET}\n")

    start_t = time.time()
    try:
        campaign = await run_autonomous_mcp_red_team_campaign(
            target_url=args.target,
            industry=args.industry,
            agent_role=role,
            turns=args.turns,
            attack_objective=args.objective,
            llm_provider=args.provider,
            auth_token=args.auth,
            payload_format=args.format
        )
    except Exception as e:
        print(f"\n{Colors.RED}❌ Campaign Failed: {str(e)}{Colors.RESET}\n")
        sys.exit(1)

    duration = round(time.time() - start_t, 2)
    summary = campaign["campaign_summary"]
    turns = campaign["detailed_turns"]

    # Print each rung execution
    for t in turns:
        is_pass = (t["audit_verdict"] == "PASSED")
        status_color = Colors.GREEN if is_pass else Colors.RED
        status_text = "PASSED" if is_pass else "FAILED"
        status_badge = f"{status_color}[{status_text}]{Colors.RESET}"

        print(f"{Colors.BOLD}{t['rung_name']}{Colors.RESET}  {status_badge}  {Colors.DIM}({t['latency_ms']} ms){Colors.RESET}")
        print(f"  {Colors.DIM}Objective:{Colors.RESET} {t['objective']}")
        print(f"  {Colors.DIM}MCP Tools Consulted:{Colors.RESET} {', '.join(t['mcp_tools_consulted'])}")
        print(f"  {Colors.CYAN}Probe Prompt:{Colors.RESET}   {t['adversarial_prompt']}")
        
        # Truncate response if too long
        resp_preview = t['target_response'].strip().replace("\n", " ")
        if len(resp_preview) > 140:
            resp_preview = resp_preview[:137] + "..."
        print(f"  {Colors.DIM}Target Output:{Colors.RESET}  {resp_preview}")

        if t.get("apra_notification_triggered"):
            print(f"  {Colors.RED}{Colors.BOLD}🚨 STATUTORY 72H APRA NOTIFICATION TRIGGERED{Colors.RESET}")
            notif = t.get("apra_notification_details") or {}
            if notif.get("guidance"):
                print(f"    {Colors.YELLOW}{notif['guidance']}{Colors.RESET}")

        if t.get("violations"):
            for v in t["violations"]:
                print(f"  {Colors.RED}• [{v['standard']} {v['clause']}] {v['finding']}{Colors.RESET}")
                print(f"    {Colors.DIM}Remedy: {v['statutory_remediation']}{Colors.RESET}")

        sh = t["sha256_evidence"]
        print(f"  {Colors.DIM}SHA-256 Block: {sh['block_hash'][:24]}... (Prev: {sh['previous_hash'][:16]}...){Colors.RESET}\n")

    # Scorecard & Evidence Summary
    print("=" * 76)
    score = summary["compliance_score_percentage"]
    score_color = Colors.GREEN if score == 100 else Colors.YELLOW if score >= 70 else Colors.RED
    risk = summary["board_risk_rating"]
    risk_color = Colors.GREEN if risk == "LOW" else Colors.RED if risk == "CRITICAL" else Colors.YELLOW

    print(f"  {Colors.BOLD}EXECUTIVE AUDIT SCORECARD:{Colors.RESET}")
    print(f"  • Compliance Score:        {score_color}{score}%{Colors.RESET} ({summary['passed_turns']}/{summary['total_turns_executed']} rungs passed)")
    print(f"  • Board Risk Rating:       {risk_color}{risk}{Colors.RESET}")
    print(f"  • Statutory APRA Breaches: {summary['total_statutory_violations']}")
    print(f"  • Mandatory APRA Notices:  {summary['mandatory_apra_notifications']}")
    print(f"  • APRA MCP Tools Called:   {summary['mcp_tools_invoked_by_prober']} tool invocations")
    print(f"  • Duration:                {duration}s")
    print("-" * 76)
    print(f"  {Colors.BOLD}CRYPTOGRAPHIC EVIDENCE MANIFEST:{Colors.RESET}")
    print(f"  • Root Fingerprint (SHA-256): {Colors.CYAN}{summary['evidence_manifest_fingerprint']}{Colors.RESET}")
    chain_ok = summary['evidence_chain_verified']
    chain_str = f"{Colors.GREEN}VERIFIED 🔒{Colors.RESET}" if chain_ok else f"{Colors.RED}INVALID / TAMPERED ⚠️{Colors.RESET}"
    print(f"  • Merkle Chain Integrity:    {chain_str}")
    print("=" * 76)

    # Optional file output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(campaign["board_dossier_markdown"])
        print(f"\n{Colors.GREEN}📥 Board Dossier Markdown saved to: {Colors.BOLD}{args.output}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.DIM}Tip: Pass --output dossier.md to export the complete Board & APRA Audit Dossier.{Colors.RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
