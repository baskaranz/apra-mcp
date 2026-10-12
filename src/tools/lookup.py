"""Lookup tools for APRA standards and specific regulatory clauses."""

from typing import Any, Dict, List, Optional
from src.db import get_standard_by_code, get_clause_by_number, get_connection


def list_standards() -> List[Dict[str, Any]]:
    """List all APRA standards currently supported by the MCP server."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, title, short_name, status, effective_date, legislative_instrument FROM standards")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_standard_overview(standard_code: str) -> Dict[str, Any]:
    """Get high-level details, legal instrument, statutory scope, and summary of an APRA standard."""
    std = get_standard_by_code(standard_code)
    if not std:
        return {
            "error": f"Standard '{standard_code}' not found. Supported standards are 'CPS 230' and 'CPS 234'."
        }
    return std


def lookup_specific_clause(standard_code: str, clause_number: str) -> Dict[str, Any]:
    """Retrieve exact statutory text, subclauses, and notes for a specific APRA clause."""
    clause = get_clause_by_number(standard_code, clause_number)
    if not clause:
        return {
            "error": f"Clause '{clause_number}' not found in standard '{standard_code}'."
        }
    return {
        "id": clause["id"],
        "standard": clause["standard_code"],
        "clause_number": clause["clause_number"],
        "section": clause["section_name"],
        "heading": clause["heading"],
        "statutory_text": clause["text"],
        "subclauses": clause["subclauses"],
        "is_mandatory": clause["is_mandatory"],
        "notification_trigger": clause["notification_trigger"],
        "notes_and_guidance": clause["notes"]
    }
