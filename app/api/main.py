"""HTTP API for the portal: create and start sessions, stream agent replies (SSE), read state."""

import json
import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from pydantic import BaseModel

from app.api.setup import SETUP_HEADER, initial_state, setup_message
from app.config import get_settings
from app.escalation.store import PostgresEscalationStore
from app.graph.builder import build_graph
from app.graph.messages import message_text
from app.graph.nodes.guardrails import redact
from app.graph.nodes.phase_transition import phase_transition
from app.graph.state import IntegrationProfile
from app.kb.guide import GuideNotReady, build_guide, guide_filename
from app.learning.issues import clean, lint_issue, publish_issue
from app.learning.store import DOC_GAP, ISSUE_DRAFT, PostgresLearningStore
from app.validators.upload import MAX_UPLOAD_BYTES, UPLOAD_HEADER, process_upload, safe_filename

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sessions are LangGraph threads checkpointed in Postgres, so a client can resume days later.
    async with AsyncPostgresSaver.from_conn_string(get_settings().database_url) as checkpointer:
        await checkpointer.setup()
        app.state.graph = build_graph(checkpointer=checkpointer)
        app.state.escalations = PostgresEscalationStore(get_settings().database_url)
        await app.state.escalations.setup()
        app.state.learning = PostgresLearningStore(get_settings().database_url)
        await app.state.learning.setup()
        yield


app = FastAPI(title="Experience+ Integration Copilot", lifespan=lifespan)


class MessageIn(BaseModel):
    content: str


class StartIn(BaseModel):
    profile: IntegrationProfile


class AnswerIn(BaseModel):
    answer: str


class IssueEdit(BaseModel):
    """What the reviewer may change before approving; omitted fields keep the draft's value."""

    error_signature: str | None = None
    root_cause: str | None = None
    fix: str | None = None
    platform: str | None = None
    config_mode: str | None = None


class HandleGaps(BaseModel):
    ids: list[str]


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


def _stream_turn(session_id: str, inputs: dict) -> StreamingResponse:
    """Run one agent turn and stream its visible text as SSE `token` events, then `done`."""
    graph = app.state.graph

    async def events() -> AsyncIterator[str]:
        last_message_id = None
        try:
            async for chunk, meta in graph.astream(
                inputs, _config(session_id), stream_mode="messages"
            ):
                if meta.get("langgraph_node") != "agent" or not isinstance(chunk, AIMessageChunk):
                    continue
                text = message_text(chunk.content)
                if not text:
                    continue
                # A turn can contain several agent calls (agent → tools → agent); separate them.
                if last_message_id is not None and chunk.id != last_message_id:
                    yield _sse({"type": "token", "text": "\n\n"})
                last_message_id = chunk.id
                yield _sse({"type": "token", "text": text})
            # The guardrails node's note isn't model output, so it doesn't stream; send it now.
            values = await _values(session_id)
            last = (values.get("messages") or [None])[-1]
            if last is not None and last.additional_kwargs.get("guardrail"):
                yield _sse({"type": "token", "text": "\n\n" + message_text(last.content)})
            await _sync_learning(session_id)
            if await _sync_escalation(session_id):
                yield _sse({"type": "escalated"})
        except Exception:
            log.exception("agent turn failed for session %s", session_id)
            yield _sse({"type": "error", "text": "Something went wrong on our side. Please retry."})
        yield _sse({"type": "done"})

    return StreamingResponse(events(), media_type="text/event-stream")


async def _values(session_id: str) -> dict:
    snapshot = await app.state.graph.aget_state(_config(session_id))
    return snapshot.values or {}


def _pending_interrupts(snapshot) -> list:
    return [i for task in snapshot.tasks for i in task.interrupts]


async def _has_open_escalation(session_id: str) -> bool:
    return bool(_pending_interrupts(await app.state.graph.aget_state(_config(session_id))))


def _trim(text: str, limit: int = 1500) -> str:
    return text if len(text) <= limit else text[:limit] + "…"


async def _sync_escalation(session_id: str):
    """If the thread paused on escalate_to_human, make sure the admin queue has an entry for it."""
    snapshot = await app.state.graph.aget_state(_config(session_id))
    interrupts = _pending_interrupts(snapshot)
    if not interrupts:
        return None
    payload = interrupts[0].value if isinstance(interrupts[0].value, dict) else {}
    values = snapshot.values or {}
    profile = values.get("profile") or {}
    recent = [
        {"role": "client" if isinstance(m, HumanMessage) else "assistant", "text": _trim(message_text(m.content))}
        for m in values.get("messages", [])
        if isinstance(m, HumanMessage | AIMessage) and message_text(m.content).strip()
    ][-8:]
    context = {
        "company": profile.get("company"),
        "apps": [f"{p['platform']}/{p.get('config_mode')}" for p in profile.get("platforms", [])],
        "environment": profile.get("environment"),
        "region": profile.get("region"),
        "phase": values.get("phase"),
        "step": payload.get("step"),
        "tried": payload.get("tried", []),
        "recent_messages": recent,
    }
    return await app.state.escalations.open_for_session(
        session_id, str(payload.get("summary", "")), context
    )


async def _sync_learning(session_id: str) -> None:
    """Copy fixes the client confirmed and gaps the agent reported into the review queue.

    Idempotent (items are keyed by content), and it never breaks the chat: it only logs.
    """
    store = getattr(app.state, "learning", None)
    if store is None:
        return
    try:
        values = await _values(session_id)
        for record in values.get("resolved_issues") or []:
            await store.add_if_absent(ISSUE_DRAFT, session_id, record)
        for gap in values.get("doc_gaps") or []:
            await store.add_if_absent(DOC_GAP, session_id, gap)
    except Exception:
        log.exception("syncing learning items for session %s failed", session_id)


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/sessions")
async def create_session() -> dict:
    return {"session_id": str(uuid.uuid4())}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    values = await _values(session_id)
    history = []
    for message in values.get("messages", []):
        if isinstance(message, HumanMessage):
            text = message_text(message.content)
            kind = "setup" if text.startswith(SETUP_HEADER) else "chat"
            if text.startswith(UPLOAD_HEADER):  # show "Uploaded file: x", not the check result
                kind, text = "upload", text.splitlines()[0]
            history.append({"role": "user", "text": text, "kind": kind})
        elif isinstance(message, AIMessage) and (text := message_text(message.content)):
            if message.additional_kwargs.get("guardrail") and history and history[-1]["role"] == "assistant":
                history[-1]["text"] += "\n\n" + text  # one reply with its note
            else:
                history.append({"role": "assistant", "text": text, "kind": "chat"})
    profile = IntegrationProfile.model_validate(values.get("profile") or {})
    waiting = await _has_open_escalation(session_id)
    return {
        "phase": values.get("phase", "discovery"),
        "plan_steps": values.get("plan_steps", []),
        "current_step": values.get("current_step", 0),
        "escalation": {"status": "open"} if waiting else None,
        "profile": values.get("profile", {}),
        # The downloadable guide needs every app's config mode (Firebase or not).
        "guide_ready": bool(profile.platforms) and all(p.config_mode for p in profile.platforms),
        "prerequisites": values.get("prerequisites", []),
        "loaded_files": values.get("loaded_files", []),
        "messages": history,
    }


@app.post("/sessions/{session_id}/start")
async def start_session(session_id: str, body: StartIn) -> StreamingResponse:
    """Begin a session from the setup wizard; the agent replies to the submitted profile."""
    if (await _values(session_id)).get("messages"):
        raise HTTPException(status_code=409, detail="This session has already started.")
    inputs = {
        **initial_state(body.profile),
        "messages": [HumanMessage(content=redact(setup_message(body.profile)))],
    }
    return _stream_turn(session_id, inputs)


WAITING = "An engineer is looking into this. Their reply will appear here."


@app.post("/sessions/{session_id}/messages")
async def post_message(session_id: str, body: MessageIn) -> StreamingResponse:
    # The thread is paused mid tool call; a new message would leave that call without a result.
    if await _has_open_escalation(session_id):
        raise HTTPException(status_code=409, detail=WAITING)
    return _stream_turn(session_id, {"messages": [HumanMessage(content=redact(body.content))]})


@app.post("/sessions/{session_id}/files")
async def upload_file(
    session_id: str, request: Request, name: str = Query(max_length=200)
) -> StreamingResponse:
    """A file from the checklist (e.g. google-services.json), sent as the raw request body.

    The system checks it against the client's stated identifiers and updates the checklist; the
    agent only sees the result, never the file, and replies to it like to any other message.
    """
    values = await _values(session_id)
    if not values.get("messages"):
        raise HTTPException(status_code=404, detail="This onboarding hasn't started.")
    if await _has_open_escalation(session_id):
        raise HTTPException(status_code=409, detail=WAITING)
    if not values.get("prerequisites"):
        raise HTTPException(status_code=409, detail="Confirm your setup details first.")
    if int(request.headers.get("content-length") or 0) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="That file is too large.")
    content = await request.body()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="That file is too large.")

    update = process_upload(values, safe_filename(name), content)
    # Marking the last blocking item verified should move the phase on within this turn.
    update.update(phase_transition({**values, **update}))
    return _stream_turn(session_id, update)


@app.get("/sessions/{session_id}/guide")
async def download_guide(session_id: str) -> Response:
    """The client's integration guide as one Markdown file, for their own AI assistant."""
    values = await _values(session_id)
    if not values.get("messages"):
        raise HTTPException(status_code=404, detail="This onboarding hasn't started.")
    profile = IntegrationProfile.model_validate(values.get("profile") or {})
    try:
        markdown = build_guide(profile, get_settings().knowledge_base_dir)
    except GuideNotReady as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return Response(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{guide_filename(profile)}"'},
    )


# ── Admin: the escalation queue (no authentication yet: SSO/login comes later, PLAN.md §11) ──


@app.get("/admin/escalations")
async def list_escalations(status: str | None = Query(default="open")) -> list[dict]:
    return [row.to_dict() for row in await app.state.escalations.list(status or None)]


@app.post("/admin/escalations/{escalation_id}/answer")
async def answer_escalation(escalation_id: str, body: AnswerIn) -> dict:
    """Resume the paused thread with the engineer's answer; the agent relays it to the client."""
    row = await app.state.escalations.get(escalation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="No such escalation.")
    if row.status != "open":
        raise HTTPException(status_code=409, detail="Already answered.")
    answer = redact(body.answer.strip())
    if not answer:
        raise HTTPException(status_code=422, detail="The answer is empty.")
    try:
        async for _ in app.state.graph.astream(
            Command(resume=answer), _config(row.session_id), stream_mode="updates"
        ):
            pass
    except Exception as error:
        log.exception("resuming session %s failed", row.session_id)
        raise HTTPException(status_code=502, detail="Couldn't resume the session; try again.") from error
    await app.state.escalations.mark_answered(row.id, answer)
    await _sync_learning(row.session_id)
    await _sync_escalation(row.session_id)  # the agent may have escalated again
    return {"ok": True}


# ── Admin: what the system learned (reviewed before it reaches the knowledge base) ────────────


@app.get("/admin/issue-drafts")
async def list_issue_drafts(status: str | None = Query(default="pending")) -> list[dict]:
    return [row.to_dict() for row in await app.state.learning.list(ISSUE_DRAFT, status or None)]


async def _pending_draft(draft_id: str):
    row = await app.state.learning.get(draft_id)
    if row is None or row.kind != ISSUE_DRAFT:
        raise HTTPException(status_code=404, detail="No such draft.")
    if row.status != "pending":
        raise HTTPException(status_code=409, detail=f"Already {row.status}.")
    return row


@app.post("/admin/issue-drafts/{draft_id}/approve")
async def approve_issue_draft(draft_id: str, edits: IssueEdit) -> dict:
    """Publish the draft (after the reviewer's edits) as knowledge_base/issues/<platform>-<slug>.md."""
    row = await _pending_draft(draft_id)
    payload = {**row.payload, **{k: v for k, v in edits.model_dump().items() if v is not None}}
    kb_dir = get_settings().knowledge_base_dir
    if errors := lint_issue(payload, kb_dir):
        raise HTTPException(status_code=422, detail=errors)
    path = publish_issue(payload, kb_dir, row.session_id)
    await app.state.learning.update(row.id, "approved", {**row.payload, **clean(payload)})
    return {"file": f"issues/{path.name}"}


@app.post("/admin/issue-drafts/{draft_id}/reject")
async def reject_issue_draft(draft_id: str) -> dict:
    row = await _pending_draft(draft_id)
    await app.state.learning.update(row.id, "rejected")
    return {"ok": True}


@app.get("/admin/doc-gaps")
async def list_doc_gaps() -> list[dict]:
    """Open gaps, grouped by question so a gap many clients hit shows up as one line with a count."""
    groups: dict[str, dict] = {}
    for row in await app.state.learning.list(DOC_GAP, "pending"):
        question = row.payload.get("question", "")
        group = groups.setdefault(
            " ".join(question.lower().split()),
            {"question": question, "count": 0, "sessions": set(), "ids": [], "last_seen": row.created_at},
        )
        group["count"] += 1
        group["sessions"].add(row.session_id)
        group["ids"].append(row.id)
        group["last_seen"] = max(group["last_seen"], row.created_at)
    ranked = sorted(groups.values(), key=lambda g: (-len(g["sessions"]), g["last_seen"]))
    return [{**g, "sessions": len(g["sessions"])} for g in ranked]


@app.post("/admin/doc-gaps/handle")
async def handle_doc_gaps(body: HandleGaps) -> dict:
    """Mark gaps handled once the documentation has been written."""
    for item_id in body.ids:
        row = await app.state.learning.get(item_id)
        if row is not None and row.kind == DOC_GAP:
            await app.state.learning.update(item_id, "handled")
    return {"ok": True}
