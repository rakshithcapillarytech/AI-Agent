"""HTTP API for the portal: create sessions, stream agent replies (SSE), read session state."""

import json
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from pydantic import BaseModel

from app.config import get_settings
from app.graph.builder import build_graph
from app.graph.nodes.guardrails import redact

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


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _text(content) -> str:
    """Visible text of a message: plain str, or the text blocks of Anthropic content blocks."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/sessions")
async def create_session() -> dict:
    return {"session_id": str(uuid.uuid4())}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    snapshot = await app.state.graph.aget_state(_config(session_id))
    values = snapshot.values or {}
    history = []
    for message in values.get("messages", []):
        if isinstance(message, HumanMessage):
            history.append({"role": "user", "text": _text(message.content)})
        elif isinstance(message, AIMessage) and (text := _text(message.content)):
            history.append({"role": "assistant", "text": text})
    return {
        "phase": values.get("phase", "discovery"),
        "profile": values.get("profile", {}),
        "prerequisites": values.get("prerequisites", []),
        "loaded_files": values.get("loaded_files", []),
        "messages": history,
    }


@app.post("/sessions/{session_id}/messages")
async def post_message(session_id: str, body: MessageIn) -> StreamingResponse:
    graph = app.state.graph
    inputs = {"messages": [HumanMessage(content=redact(body.content))]}

    async def events():
        last_message_id = None
        try:
            async for chunk, meta in graph.astream(
                inputs, _config(session_id), stream_mode="messages"
            ):
                if meta.get("langgraph_node") != "agent" or not isinstance(chunk, AIMessageChunk):
                    continue
                text = _text(chunk.content)
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
