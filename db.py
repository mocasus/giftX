"""SQLite database for giftX — order tracking and session management."""

import sqlite3
from pathlib import Path
from config import DB_PATH

def _get_db_path() -> Path:
    p = Path(DB_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def _conn():
    return sqlite3.connect(str(_get_db_path()))

def init_db():
    """Create tables if not exist."""
    with _conn() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_username TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error TEXT,
                screenshot_path TEXT
            );
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                state TEXT DEFAULT 'idle',
                data TEXT DEFAULT '{}'
            );
        """)

def add_order(user_id: int, target_username: str) -> int:
    with _conn() as db:
        cur = db.execute(
            "INSERT INTO orders (user_id, target_username) VALUES (?, ?)",
            (user_id, target_username)
        )
        return cur.lastrowid

def update_order(order_id: int, status: str, error: str = None, screenshot: str = None):
    with _conn() as db:
        if status == 'done':
            db.execute(
                "UPDATE orders SET status=?, completed_at=CURRENT_TIMESTAMP, error=?, screenshot_path=? WHERE id=?",
                (status, error, screenshot, order_id)
            )
        else:
            db.execute(
                "UPDATE orders SET status=?, error=?, screenshot_path=? WHERE id=?",
                (status, error, screenshot, order_id)
            )

def get_user_orders(user_id: int, limit: int = 10):
    with _conn() as db:
        return db.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()

def get_order(order_id: int):
    with _conn() as db:
        return db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

def get_stats():
    with _conn() as db:
        total = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        done = db.execute("SELECT COUNT(*) FROM orders WHERE status='done'").fetchone()[0]
        failed = db.execute("SELECT COUNT(*) FROM orders WHERE status='failed'").fetchone()[0]
        return total, done, failed
