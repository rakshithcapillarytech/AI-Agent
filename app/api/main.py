"""HTTP API for the portal: create and start sessions, stream agent replies (SSE), read state."""

import json
import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from pydantic import BaseModel

from app.api.setup import SETUP_HEADER, initial_state, setup_message
from app.config import get_settings
from app.graph.builder import build_graph
from app.graph.messages import message_text
from app.graph.nodes.guardrails import redact
from app.graph.state import IntegrationProfile
from app.kb.guide import GuideNotReady, build_guide, guide_filename

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sessions are LangGraph threads checkpointed in Postgres, so a client can resume days later.
    async with AsyncPostgresSaver.from_conn_string(get_settings().database_url) as checkpointer:
        await checkpointer.setup()
        app.state.graph = build_graph(checkpointer=checkpointer)
        yield


app = FastAPI(title="Experience+ Integration Copilot", lifespan=lifespan)


class MessageIn(BaseModel):
    content: str


class StartIn(BaseModel):
    profile: IntegrationProfile


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
        except Exception:
            log.exception("agent turn failed for session %s", session_id)
            yield _sse({"type": "error", "text": "Something went wrong on our side. Please retry."})
        yield _sse({"type": "done"})

    return StreamingResponse(events(), media_type="text/event-stream")


async def _values(session_id: str) -> dict:
    snapshot = await app.state.graph.aget_state(_config(session_id))
    return snapshot.values or {}


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
            history.append({"role": "user", "text": text, "kind": kind})
        elif isinstance(message, AIMessage) and (text := message_text(message.content)):
            history.append({"role": "assistant", "text": text, "kind": "chat"})
    profile = IntegrationProfile.model_validate(values.get("profile") or {})
    return {
        "phase": values.get("phase", "discovery"),
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


@app.post("/sessions/{session_id}/messages")
async def post_message(session_id: str, body: MessageIn) -> StreamingResponse:
    return _stream_turn(session_id, {"messages": [HumanMessage(content=redact(body.content))]})


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
