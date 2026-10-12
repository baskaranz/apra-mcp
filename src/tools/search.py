"""Full-text and semantic search engine across APRA prudential standards."""

from typing import Any, Dict, List, Optional
from src.db import search_clauses


def execute_search(
    query: str,
    standard_code: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Execute search over APRA regulations with ranked scoring and snippets."""
    results = search_clauses(query=query, standard_code=standard_code, limit=limit)
    
    formatted = []
    for r in results:
        formatted.append({
            "id": r["id"],
            "standard": r["standard_code"],
            "clause_number": r["clause_number"],
            "section": r["section_name"],
            "heading": r["heading"],
            "text": r["text"],
            "subclauses": r["subclauses"][:3] if r.get("subclauses") else [],
            "notification_trigger": r.get("notification_trigger"),
            "notes": r.get("notes")
        })

    return {
        "query": query,
        "standard_filter": standard_code or "all",
        "total_results": len(formatted),
        "results": formatted
    }
