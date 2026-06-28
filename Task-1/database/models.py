"""
SQLite database models and operations for translation history.
The database file is auto-created on first import.
"""

import os
import sqlite3
from datetime import datetime

from config import DATABASE_PATH, DATABASE_DIR, MAX_HISTORY_ENTRIES


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS translations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text     TEXT    NOT NULL,
    translated_text TEXT    NOT NULL,
    source_language VARCHAR(50) NOT NULL,
    target_language VARCHAR(50) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create the database directory and translations table if they don't exist."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = _get_connection()
    try:
        conn.execute(_CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CRUD Operations
# ---------------------------------------------------------------------------

def add_translation(
    source_text: str,
    translated_text: str,
    source_language: str,
    target_language: str,
) -> int:
    """
    Insert a new translation record.

    Returns the row id of the inserted record.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO translations (source_text, translated_text, source_language, target_language, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_text, translated_text, source_language, target_language, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        row_id = cursor.lastrowid

        # Enforce maximum history size — delete oldest entries beyond the limit
        _trim_history(conn)

        return row_id
    finally:
        conn.close()


def get_history(limit: int = MAX_HISTORY_ENTRIES) -> list[dict]:
    """
    Retrieve translation history, newest first.

    Parameters
    ----------
    limit : int
        Maximum number of entries to return.

    Returns
    -------
    list[dict]
        Each dict contains: id, source_text, translated_text,
        source_language, target_language, created_at.
    """
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM translations ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def clear_history() -> int:
    """
    Delete all translation history records.

    Returns the number of rows deleted.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute("DELETE FROM translations")
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trim_history(conn: sqlite3.Connection) -> None:
    """Remove oldest records if total count exceeds MAX_HISTORY_ENTRIES."""
    count = conn.execute("SELECT COUNT(*) FROM translations").fetchone()[0]
    if count > MAX_HISTORY_ENTRIES:
        excess = count - MAX_HISTORY_ENTRIES
        conn.execute(
            """
            DELETE FROM translations
            WHERE id IN (
                SELECT id FROM translations
                ORDER BY created_at ASC
                LIMIT ?
            )
            """,
            (excess,),
        )
        conn.commit()


# Auto-initialize on import
init_db()
