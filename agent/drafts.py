"""Draft store — for replies Wira wants to send but isn't yet trusted to.

In draft mode, every generated reply lands here instead of going out on
WhatsApp. The customer reviews drafts (today: via this DB or logs;
roadmap: via the web dashboard) and approves them by hand.
"""

import logging
import sqlite3
import time
from pathlib import Path

import config

logger = logging.getLogger("wira.drafts")


class Drafts:
    def __init__(self, db_path: str = config.DRAFTS_DB_PATH):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    sender_name TEXT,
                    incoming TEXT NOT NULL,
                    draft TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status, id DESC)")

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def record(self, chat: str, sender: str, sender_name: str, incoming: str, draft: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO drafts (chat, sender, sender_name, incoming, draft, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (chat, sender, sender_name, incoming, draft, time.time()),
            )
            draft_id = cur.lastrowid
        logger.info(
            "Draft #%d queued for %s (%s): %s",
            draft_id,
            sender_name or sender,
            sender,
            draft,
        )
        return draft_id

    def pending(self, limit: int = 50) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, chat, sender, sender_name, incoming, draft, created_at"
                " FROM drafts WHERE status = 'pending' ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": r[0], "chat": r[1], "sender": r[2], "sender_name": r[3],
                "incoming": r[4], "draft": r[5], "created_at": r[6],
            }
            for r in rows
        ]

    def mark(self, draft_id: int, status: str):
        with self._conn() as conn:
            conn.execute("UPDATE drafts SET status = ? WHERE id = ?", (status, draft_id))
