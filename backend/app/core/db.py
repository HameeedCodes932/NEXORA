import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workspace_files (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    extension TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    modified_at TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reason TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS file_embeddings (
                    file_id TEXT PRIMARY KEY,
                    vector TEXT NOT NULL,
                    engine TEXT NOT NULL,
                    FOREIGN KEY(file_id) REFERENCES workspace_files(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS organization_plans (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    actions TEXT NOT NULL,
                    summary TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS activity_log (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    file_id TEXT,
                    filename TEXT NOT NULL,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    metadata TEXT NOT NULL
                );
                """
            )

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(query, tuple(params)).fetchone()
        return dict(row) if row else None

    def execute(self, query: str, params: Iterable[Any] = ()) -> None:
        with self.connect() as conn:
            conn.execute(query, tuple(params))

    def execute_many(self, query: str, rows: Iterable[Iterable[Any]]) -> None:
        with self.connect() as conn:
            conn.executemany(query, rows)


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


def from_json(value: str | None, fallback: Any = None) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback
