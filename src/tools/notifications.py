"""Statutory notification advisor and decision tree for APRA incidents."""

from typing import Any, Dict, List
from src.db import get_all_notifications


def assess_notification_requirements(
    incident_type: str,
    is_cyber_or_infosec: bool = False,
    exceeds_tolerance: bool = False,
    is_material_impact: bool = True,
    notified_to_other_regulators: bool = False,
    is_control_weakness: bool = False
) -> Dict[str, Any]:
    """
    Evaluates an operational incident or control finding against APRA statutory notification mandates.
    Applies the specific rules from CPS 230 (paras 33, 42) and CPS 234 (paras 35, 36).
    """
    applicable_obligations: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # 1. 24-HOUR NOTIFICATION: Disruption outside tolerance (CPS 230 para 42)
    if exceeds_tolerance:
        applicable_obligations.append({
            "standard": "CPS 230",
            "clause": "Paragraph 42",
            "timeframe": "24 hours",
            "urgency": "CRITICAL",
            "trigger": "Disruption to a critical operation outside Board-approved tolerance levels (outage duration, data loss, or minimum service level).",
            "mandatory_reporting_content": [
                "Nature of disruption",
                "Immediate actions taken",
                "Likely impact on depositors/policyholders/customers",
                "Estimated timeframe for returning to normal operations"
            ]
        })
        warnings.append("CRITICAL: Disruption outside tolerance triggers APRA's strictest 24-hour notification deadline.")

    # 2. 72-HOUR NOTIFICATION: Cyber / Information Security Incident (CPS 234 para 35)
    if is_cyber_or_infosec and (is_material_impact or notified_to_other_regulators):
        applicable_obligations.append({
            "standard": "CPS 234",
            "clause": "Paragraph 35",
            "timeframe": "72 hours",
            "urgency": "HIGH",
            "trigger": "Material information security incident (affecting confidentiality, integrity, availability) OR incident notified to other regulators (e.g. OAIC under Notifiable Data Breaches, ASIC, ACSC).",
            "mandatory_reporting_content": [
                "Description of cyber/security incident and affected assets",
                "Impact on customer data, confidentiality, integrity, availability",
                "Containment actions and status of investigations",
                "Details of other regulators notified (OAIC, ACSC, etc.)"
            ]
        })

    # 3. 72-HOUR NOTIFICATION: General Operational Risk Incident (CPS 230 para 33)
    if not is_cyber_or_infosec and is_material_impact and not exceeds_tolerance:
        applicable_obligations.append({
            "standard": "CPS 230",
            "clause": "Paragraph 33",
            "timeframe": "72 hours",
            "urgency": "HIGH",
            "trigger": "Operational risk incident determined likely to have a material financial impact or material impact on maintaining critical operations.",
            "mandatory_reporting_content": [
                "Description of operational failure and root cause",
                "Financial impact assessment",
                "Impact on critical operations",
                "Remediation roadmap"
            ]
        })

    # 4. DE-DUPLICATION RULE (CPS 230 Footnote 11)
    deduplication_applied = False
    if is_cyber_or_infosec and is_material_impact:
        deduplication_applied = True
        warnings.append(
            "DE-DUPLICATION RULE APPLIED (CPS 230 Footnote 11): Because this is an information security incident "
            "reported under CPS 234 (para 35), you are EXEMPT from submitting a duplicate operational risk incident report "
            "under CPS 230 (para 33). However, if the disruption also exceeds approved tolerance levels, the separate 24-hour "
            "notification under CPS 230 (para 42) remains mandatory."
        )

    # 5. 10-BUSINESS-DAY NOTIFICATION: Control Weakness (CPS 234 para 36)
    if is_control_weakness:
        applicable_obligations.append({
            "standard": "CPS 234",
            "clause": "Paragraph 36",
            "timeframe": "10 business days",
            "urgency": "MEDIUM",
            "trigger": "Material information security control weakness identified that cannot be remediated in a timely manner.",
            "mandatory_reporting_content": [
                "Description of control vulnerability",
                "Impacted systems and information assets",
                "Reasons timely remediation is unachievable",
                "Compensating controls and revised remediation plan"
            ]
        })

    if not applicable_obligations:
        applicable_obligations.append({
            "standard": "None triggered",
            "clause": "N/A",
            "timeframe": "No immediate statutory reporting triggered",
            "urgency": "ROUTINE",
            "trigger": "Incident appears to be within internal risk appetite and tolerance levels without material customer or financial impact.",
            "mandatory_reporting_content": [
                "Log in internal incident register and track near misses per CPS 230 para 32."
            ]
        })

    return {
        "incident_assessment": {
            "incident_type": incident_type,
            "is_cyber": is_cyber_or_infosec,
            "tolerance_exceeded": exceeds_tolerance,
            "material_impact": is_material_impact
        },
        "applicable_statutory_obligations": applicable_obligations,
        "deduplication_rule_active": deduplication_applied,
        "advisory_notes": warnings
    }


def list_all_notification_rules() -> List[Dict[str, Any]]:
    """Returns the comprehensive table of all APRA notification triggers across CPS 230 and CPS 234."""
    return get_all_notifications()
