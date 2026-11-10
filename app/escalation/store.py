"""The escalation queue: one record per hand-off to a Capillary engineer (PLAN.md §4 ⑥).

The paused thread itself lives in the LangGraph checkpoint; this table is only the admin's
worklist. Postgres in the app, in memory for tests. Both give the same methods.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


@dataclass
class Escalation:
    id: str
    session_id: str
    summary: str
    context: dict
    status: str = "open"  # open | answered
    answer: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    answered_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class InMemoryEscalationStore:
    def __init__(self):
        self._rows: dict[str, Escalation] = {}

    async def setup(self) -> None:
        return None

    async def open_for_session(self, session_id: str, summary: str, context: dict) -> Escalation:
        """The session's open escalation; a second call for the same pause returns the same one."""
        for row in self._rows.values():
            if row.session_id == session_id and row.status == "open":
                return row
        row = Escalation(uuid.uuid4().hex, session_id, summary, context)
        self._rows[row.id] = row
        return row

    async def get(self, escalation_id: str) -> Escalation | None:
        return self._rows.get(escalation_id)

    async def list(self, status: str | None = None) -> list[Escalation]:
        rows = [r for r in self._rows.values() if status in (None, r.status)]
        return sorted(rows, key=lambda r: r.created_at)

    async def mark_answered(self, escalation_id: str, answer: str) -> None:
        row = self._rows[escalation_id]
        row.status, row.answer = "answered", answer
        row.answered_at = datetime.now(UTC).isoformat()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS escalations (
    id          text PRIMARY KEY,
    session_id  text NOT NULL,
    status      text NOT NULL DEFAULT 'open',
    summary     text NOT NULL,
    context     jsonb NOT NULL,
    answer      text,
    created_at  timestamptz NOT NULL DEFAULT now(),
    answered_at timestamptz
);
CREATE INDEX IF NOT EXISTS escalations_status_idx ON escalations (status, created_at);
"""
_COLUMNS = "id, session_id, summary, context, status, answer, created_at, answered_at"


def _row(r: dict) -> Escalation:
    for key in ("created_at", "answered_at"):
        if r[key] is not None:
            r[key] = r[key].isoformat()
    return Escalation(**r)


class PostgresEscalationStore:
    """Low volume (a handful of hand-offs a day), so one short connection per call is enough."""

    def __init__(self, url: str):
        self._url = url

    def _connect(self):
        return psycopg.AsyncConnection.connect(self._url, autocommit=True, row_factory=dict_row)

    async def setup(self) -> None:
        async with await self._connect() as conn:
            await conn.execute(_SCHEMA)

    async def open_for_session(self, session_id: str, summary: str, context: dict) -> Escalation:
        async with await self._connect() as conn:
            cur = await conn.execute(
                f"SELECT {_COLUMNS} FROM escalations WHERE session_id = %s AND status = 'open'",
                (session_id,),
            )
            if existing := await cur.fetchone():
                return _row(existing)
            cur = await conn.execute(
                f"INSERT INTO escalations (id, session_id, summary, context) VALUES (%s, %s, %s, %s)"
                f" RETURNING {_COLUMNS}",
                (uuid.uuid4().hex, session_id, summary, Jsonb(context)),
            )
            return _row(await cur.fetchone())

    async def get(self, escalation_id: str) -> Escalation | None:
        async with await self._connect() as conn:
            cur = await conn.execute(f"SELECT {_COLUMNS} FROM escalations WHERE id = %s", (escalation_id,))
            row = await cur.fetchone()
            return _row(row) if row else None

    async def list(self, status: str | None = None) -> list[Escalation]:
        async with await self._connect() as conn:
            cur = await conn.execute(
                f"SELECT {_COLUMNS} FROM escalations WHERE (%s::text IS NULL OR status = %s) "
                "ORDER BY created_at",
                (status, status),
            )
            return [_row(r) for r in await cur.fetchall()]

    async def mark_answered(self, escalation_id: str, answer: str) -> None:
        async with await self._connect() as conn:
            await conn.execute(
                "UPDATE escalations SET status = 'answered', answer = %s, answered_at = now() WHERE id = %s",
                (answer, escalation_id),
            )
