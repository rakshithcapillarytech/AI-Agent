"""The review queue for things the system learns (PLAN.md §4 ⑥): issue drafts and doc gaps.

Nothing here reaches the knowledge base by itself. An issue draft becomes a knowledge file only
when an admin approves it (app/learning/issues.py). Postgres in the app, in memory for tests.
"""

import hashlib
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

ISSUE_DRAFT = "issue_draft"
DOC_GAP = "doc_gap"


def item_key(session_id: str, kind: str, payload: dict) -> str:
    """Stable per item, so syncing the same session state twice never creates duplicates."""
    raw = f"{session_id}|{kind}|" + "|".join(f"{k}={payload[k]}" for k in sorted(payload))
    return hashlib.sha1(raw.encode()).hexdigest()


@dataclass
class LearningItem:
    id: str
    kind: str  # issue_draft | doc_gap
    key: str
    session_id: str
    payload: dict
    status: str = "pending"  # pending | approved | rejected (issue_draft); pending | handled (doc_gap)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    reviewed_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class InMemoryLearningStore:
    def __init__(self):
        self._rows: dict[str, LearningItem] = {}

    async def setup(self) -> None:
        return None

    async def add_if_absent(self, kind: str, session_id: str, payload: dict) -> LearningItem | None:
        """The new item, or None if this exact one was already recorded."""
        key = item_key(session_id, kind, payload)
        if any(r.key == key for r in self._rows.values()):
            return None
        row = LearningItem(uuid.uuid4().hex, kind, key, session_id, payload)
        self._rows[row.id] = row
        return row

    async def get(self, item_id: str) -> LearningItem | None:
        return self._rows.get(item_id)

    async def list(self, kind: str, status: str | None = None) -> list[LearningItem]:
        rows = [r for r in self._rows.values() if r.kind == kind and status in (None, r.status)]
        return sorted(rows, key=lambda r: r.created_at)

    async def update(self, item_id: str, status: str, payload: dict | None = None) -> None:
        row = self._rows[item_id]
        row.status = status
        row.payload = payload if payload is not None else row.payload
        row.reviewed_at = datetime.now(UTC).isoformat()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS learning_items (
    id          text PRIMARY KEY,
    kind        text NOT NULL,
    key         text NOT NULL UNIQUE,
    status      text NOT NULL DEFAULT 'pending',
    session_id  text NOT NULL,
    payload     jsonb NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    reviewed_at timestamptz
);
CREATE INDEX IF NOT EXISTS learning_items_kind_idx ON learning_items (kind, status, created_at);
"""
_COLUMNS = "id, kind, key, session_id, payload, status, created_at, reviewed_at"


def _row(r: dict) -> LearningItem:
    for name in ("created_at", "reviewed_at"):
        if r[name] is not None:
            r[name] = r[name].isoformat()
    return LearningItem(**r)


class PostgresLearningStore:
    """Low volume, so one short connection per call (same approach as the escalation queue)."""

    def __init__(self, url: str):
        self._url = url

    def _connect(self):
        return psycopg.AsyncConnection.connect(self._url, autocommit=True, row_factory=dict_row)

    async def setup(self) -> None:
        async with await self._connect() as conn:
            await conn.execute(_SCHEMA)

    async def add_if_absent(self, kind: str, session_id: str, payload: dict) -> LearningItem | None:
        async with await self._connect() as conn:
            cur = await conn.execute(
                f"INSERT INTO learning_items (id, kind, key, session_id, payload) "
                f"VALUES (%s, %s, %s, %s, %s) ON CONFLICT (key) DO NOTHING RETURNING {_COLUMNS}",
                (uuid.uuid4().hex, kind, item_key(session_id, kind, payload), session_id, Jsonb(payload)),
            )
            row = await cur.fetchone()
            return _row(row) if row else None

    async def get(self, item_id: str) -> LearningItem | None:
        async with await self._connect() as conn:
            cur = await conn.execute(f"SELECT {_COLUMNS} FROM learning_items WHERE id = %s", (item_id,))
            row = await cur.fetchone()
            return _row(row) if row else None

    async def list(self, kind: str, status: str | None = None) -> list[LearningItem]:
        async with await self._connect() as conn:
            cur = await conn.execute(
                f"SELECT {_COLUMNS} FROM learning_items WHERE kind = %s AND (%s::text IS NULL OR status = %s) "
                "ORDER BY created_at",
                (kind, status, status),
            )
            return [_row(r) for r in await cur.fetchall()]

    async def update(self, item_id: str, status: str, payload: dict | None = None) -> None:
        async with await self._connect() as conn:
            await conn.execute(
                "UPDATE learning_items SET status = %s, reviewed_at = now(), "
                "payload = COALESCE(%s, payload) WHERE id = %s",
                (status, Jsonb(payload) if payload is not None else None, item_id),
            )
