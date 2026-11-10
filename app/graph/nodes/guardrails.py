"""Guardrails: redact secrets from client input, and flag identifiers the knowledge doesn't contain.

Output check (PLAN.md §6.1, simplified): code-like names in the agent's reply (`HydraConfig.Builder`,
`onScreenChanged`) must appear in the loaded knowledge or in what the client and tools said. If
one doesn't, a note is appended so the client double-checks it. History is never edited: the
note is a separate message, hidden from the model on later turns (see agent node).
"""

import re

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage

from app.config import get_settings
from app.graph.messages import message_text
from app.graph.state import OnboardingState
from app.kb.loader import read_files

_SECRET_PATTERNS = [
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bwk_live_[A-Za-z0-9]+"), "[REDACTED_GAMIFICATION_KEY]"),
    (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
        "[REDACTED_PRIVATE_KEY]",
    ),
]


def redact(text: str) -> str:
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


_FENCED = re.compile(r"```.*?```", re.DOTALL)
_INLINE = re.compile(r"`([^`\n]{3,80})`")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
_CODE_LIKE = re.compile(r"[a-z][A-Z]|_")  # camelCase, PascalCase or snake_case
MAX_FLAGGED = 5


def ungrounded_symbols(reply: str, corpus: str) -> list[str]:
    """Code-like names in inline code spans of `reply` that don't appear anywhere in `corpus`."""
    flagged = []
    for span in _INLINE.findall(_FENCED.sub("", reply)):
        symbol = span.split("(")[0].strip()
        if not _IDENTIFIER.fullmatch(symbol) or not _CODE_LIKE.search(symbol):
            continue
        if symbol in corpus or all(part in corpus for part in symbol.split(".") if part):
            continue
        flagged.append(symbol)
    return list(dict.fromkeys(flagged))[:MAX_FLAGGED]


def _note(symbols: list[str]) -> str:
    names = ", ".join(f"`{s}`" for s in symbols)
    return (
        f"> Note: I couldn't find {names} in the documentation I have for your setup. "
        "Please double-check with Capillary before relying on it."
    )


async def guardrails(state: OnboardingState) -> dict:
    """Runs after the agent's final reply of a turn."""
    messages = state["messages"]
    last = messages[-1] if messages else None
    if not isinstance(last, AIMessage | AIMessageChunk):
        return {}
    reply = message_text(last.content)
    if not reply.strip():
        return {}

    settings = get_settings()
    said = " ".join(
        message_text(m.content) for m in messages if isinstance(m, HumanMessage | ToolMessage)
    )
    checklist = " ".join(
        f"{p.get('title', '')} {p.get('value') or ''}" for p in state.get("prerequisites") or []
    )
    knowledge = read_files(state.get("loaded_files") or [], settings.knowledge_base_dir)
    flagged = ungrounded_symbols(reply, f"{knowledge}\n{said}\n{checklist}")
    if not flagged:
        return {}
    return {"messages": [AIMessage(content=_note(flagged), additional_kwargs={"guardrail": True})]}
