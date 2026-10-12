"""Database access and full-text search engine for APRA regulations."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).parent / "apra_regulations.db"
DATA_DIR = Path(__file__).parent / "data"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite schema including FTS5 tables and seed with data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS standards (
        code TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        short_name TEXT NOT NULL,
        legislative_instrument TEXT NOT NULL,
        effective_date TEXT NOT NULL,
        amended_date TEXT NOT NULL,
        status TEXT NOT NULL,
        sectors TEXT NOT NULL,
        entity_types TEXT NOT NULL,
        superseded_standards TEXT NOT NULL,
        companion_guidance TEXT NOT NULL,
        summary TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clauses (
        id TEXT PRIMARY KEY,
        standard_code TEXT NOT NULL,
        clause_number TEXT NOT NULL,
        section_name TEXT NOT NULL,
        heading TEXT NOT NULL,
        text TEXT NOT NULL,
        subclauses TEXT NOT NULL,
        is_mandatory INTEGER NOT NULL,
        notification_trigger TEXT,
        key_topics TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (standard_code) REFERENCES standards(code)
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS clauses_fts USING fts5(
        id UNINDEXED,
        standard_code,
        clause_number,
        section_name,
        heading,
        text,
        subclauses,
        key_topics,
        notes,
        tokenize='porter unicode61'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS definitions (
        term TEXT PRIMARY KEY,
        standard TEXT NOT NULL,
        clause TEXT NOT NULL,
        definition TEXT NOT NULL,
        mandatory_examples TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        standard TEXT NOT NULL,
        clause TEXT NOT NULL,
        event_type TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        timeframe_hours INTEGER,
        urgency TEXT NOT NULL,
        trigger_condition TEXT NOT NULL,
        apra_reporting_content TEXT NOT NULL,
        interaction_notes TEXT NOT NULL
    );
    """)

    # Seed data if empty
    cursor.execute("SELECT COUNT(*) FROM standards;")
    if cursor.fetchone()[0] == 0:
        _seed_data(cursor)

    conn.commit()
    conn.close()


def _seed_data(cursor: sqlite3.Cursor) -> None:
    # 1. Seed standards
    meta_path = DATA_DIR / "standards_meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            for std in meta.get("standards", []):
                cursor.execute("""
                INSERT OR REPLACE INTO standards VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    std["code"],
                    std["title"],
                    std["short_name"],
                    std["legislative_instrument"],
                    std["effective_date"],
                    std["amended_date"],
                    std["status"],
                    json.dumps(std["sectors"]),
                    json.dumps(std["entity_types"]),
                    json.dumps(std["superseded_standards"]),
                    json.dumps(std["companion_guidance"]),
                    std["summary"]
                ))

    # 2. Seed clauses
    for code, file_name in [("CPS 230", "cps_230.json"), ("CPS 234", "cps_234.json")]:
        file_path = DATA_DIR / file_name
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for cl in data.get("clauses", []):
                    subclauses_str = json.dumps(cl.get("subclauses", []))
                    key_topics_str = json.dumps(cl.get("key_topics", []))
                    cursor.execute("""
                    INSERT OR REPLACE INTO clauses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cl["id"],
                        code,
                        cl["clause_number"],
                        cl["section_name"],
                        cl["heading"],
                        cl["text"],
                        subclauses_str,
                        1 if cl.get("is_mandatory", True) else 0,
                        cl.get("notification_trigger"),
                        key_topics_str,
                        cl.get("notes")
                    ))

                    # Insert into FTS
                    cursor.execute("""
                    INSERT INTO clauses_fts (id, standard_code, clause_number, section_name, heading, text, subclauses, key_topics, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cl["id"],
                        code,
                        cl["clause_number"],
                        cl["section_name"],
                        cl["heading"],
                        cl["text"],
                        " ".join(cl.get("subclauses", [])),
                        " ".join(cl.get("key_topics", [])),
                        cl.get("notes", "")
                    ))

    # 3. Seed definitions
    def_path = DATA_DIR / "definitions.json"
    if def_path.exists():
        with open(def_path, "r", encoding="utf-8") as f:
            defs = json.load(f)
            for d in defs.get("definitions", []):
                cursor.execute("""
                INSERT OR REPLACE INTO definitions VALUES (?, ?, ?, ?, ?)
                """, (
                    d["term"],
                    d["standard"],
                    d["clause"],
                    d["definition"],
                    json.dumps(d.get("mandatory_examples", {}))
                ))

    # 4. Seed notifications
    notif_path = DATA_DIR / "notifications.json"
    if notif_path.exists():
        with open(notif_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
            for r in rules.get("rules", []):
                cursor.execute("""
                INSERT INTO notifications (standard, clause, event_type, timeframe, timeframe_hours, urgency, trigger_condition, apra_reporting_content, interaction_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["standard"],
                    r["clause"],
                    r["event_type"],
                    r["timeframe"],
                    r.get("timeframe_hours"),
                    r["urgency"],
                    r["trigger_condition"],
                    json.dumps(r.get("apra_reporting_content", [])),
                    r.get("interaction_notes", "")
                ))


def get_standard_by_code(code: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM standards WHERE code = ? OR code LIKE ?", (code, f"%{code}%"))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["sectors"] = json.loads(d["sectors"])
    d["entity_types"] = json.loads(d["entity_types"])
    d["superseded_standards"] = json.loads(d["superseded_standards"])
    d["companion_guidance"] = json.loads(d["companion_guidance"])
    return d


def get_clause_by_number(standard_code: str, clause_number: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM clauses 
    WHERE (standard_code = ? OR standard_code LIKE ?) 
      AND (clause_number = ? OR clause_number = ?)
    """, (standard_code, f"%{standard_code}%", str(clause_number), str(clause_number).strip()))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["subclauses"] = json.loads(d["subclauses"])
    d["key_topics"] = json.loads(d["key_topics"])
    d["is_mandatory"] = bool(d["is_mandatory"])
    return d


def search_clauses(
    query: str,
    standard_code: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Hybrid FTS and keyword search over clauses."""
    conn = get_connection()
    cursor = conn.cursor()

    # Clean query for FTS syntax
    clean_q = "".join([c if c.isalnum() or c in (" ", "-", "_") else " " for c in query]).strip()
    words = [w for w in clean_q.split() if len(w) > 1]
    
    results = []
    if words:
        fts_query = " OR ".join(f"{w}*" for w in words)
        sql = """
        SELECT c.*, bm25(clauses_fts) as rank
        FROM clauses_fts
        JOIN clauses c ON clauses_fts.id = c.id
        WHERE clauses_fts MATCH ?
        """
        params = [fts_query]

        if standard_code:
            sql += " AND c.standard_code LIKE ?"
            params.append(f"%{standard_code}%")

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                item = dict(r)
                item["subclauses"] = json.loads(item["subclauses"])
                item["key_topics"] = json.loads(item["key_topics"])
                item["is_mandatory"] = bool(item["is_mandatory"])
                results.append(item)
        except sqlite3.OperationalError:
            # Fallback to standard LIKE search
            pass

    # If FTS returned nothing or query has symbols, fallback to LIKE
    if not results:
        like_pattern = f"%{query.strip()}%"
        sql = """
        SELECT * FROM clauses
        WHERE (text LIKE ? OR heading LIKE ? or section_name LIKE ? or notes LIKE ?)
        """
        params = [like_pattern, like_pattern, like_pattern, like_pattern]
        if standard_code:
            sql += " AND standard_code LIKE ?"
            params.append(f"%{standard_code}%")
        sql += " LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        for r in cursor.fetchall():
            item = dict(r)
            item["subclauses"] = json.loads(item["subclauses"])
            item["key_topics"] = json.loads(item["key_topics"])
            item["is_mandatory"] = bool(item["is_mandatory"])
            results.append(item)

    conn.close()
    return results


def get_all_notifications() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications ORDER BY timeframe_hours ASC NULLS LAST")
    rows = cursor.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["apra_reporting_content"] = json.loads(d["apra_reporting_content"])
        out.append(d)
    return out


def get_all_definitions() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM definitions")
    rows = cursor.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["mandatory_examples"] = json.loads(d["mandatory_examples"])
        out.append(d)
    return out
