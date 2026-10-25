import sqlite3
import time
from contextlib import contextmanager

from config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS verified_members (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    verified_at INTEGER NOT NULL
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)


def upsert_member(user_id: str, username: str, access_token: str,
                   refresh_token: str, expires_in: int):
    expires_at = int(time.time()) + int(expires_in)
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO verified_members
                (user_id, username, access_token, refresh_token, expires_at, verified_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                access_token=excluded.access_token,
                refresh_token=excluded.refresh_token,
                expires_at=excluded.expires_at
            """,
            (user_id, username, access_token, refresh_token, expires_at, int(time.time())),
        )


def update_tokens(user_id: str, access_token: str, refresh_token: str, expires_in: int):
    expires_at = int(time.time()) + int(expires_in)
    with get_conn() as conn:
        conn.execute(
            "UPDATE verified_members SET access_token=?, refresh_token=?, expires_at=? WHERE user_id=?",
            (access_token, refresh_token, expires_at, user_id),
        )


def get_all_members():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM verified_members ORDER BY verified_at ASC").fetchall()
        return [dict(r) for r in rows]


def get_member(user_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM verified_members WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def remove_member(user_id: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM verified_members WHERE user_id=?", (user_id,))
