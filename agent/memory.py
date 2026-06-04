"""Per-contact conversation memory for Wira (SQLite).

Each WhatsApp chat (a JID) gets its own running history, so Wira picks up
each conversation where it left off.
"""

import logging
import sqlite3
import time
from contextlib import closing
from pathlib import Path

import config

logger = logging.getLogger("wira.memory")


class Memory:
    def __init__(self, db_path: str = config.MEMORY_DB_PATH):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()
        logger.info("Memory ready at %s", db_path)

    def _init_db(self):
        with closing(self._conn()) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chat_id ON messages(chat, id DESC)"
            )
            conn.commit()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def save(self, chat: str, role: str, content: str):
        with closing(self._conn()) as conn:
            conn.execute(
                "INSERT INTO messages (chat, timestamp, role, content) VALUES (?, ?, ?, ?)",
                (chat, time.time(), role, content),
            )
            conn.commit()
        self._prune()

    def get_recent(self, chat: str, n: int = config.MAX_HISTORY_MESSAGES) -> list[dict]:
        """Most recent N messages for one chat, oldest-first (chronological)."""
        with closing(self._conn()) as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE chat = ? ORDER BY id DESC LIMIT ?",
                (chat, n),
            ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def _prune(self):
        with closing(self._conn()) as conn:
            count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            if count > config.MAX_STORED_MESSAGES:
                excess = count - config.MAX_STORED_MESSAGES
                conn.execute(
                    "DELETE FROM messages WHERE id IN "
                    "(SELECT id FROM messages ORDER BY id ASC LIMIT ?)",
                    (excess,),
                )
                conn.commit()
                logger.debug("Pruned %d old messages", excess)
