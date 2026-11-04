"""Prerequisite tools: show the client's checklist and record progress on it.

The checklist itself is built deterministically from the profile (app/rules/prereq_engine.py);
these tools only read it and change an item's status.
"""

from typing import Annotated, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from app.config import get_settings
from app.graph.state import PrereqItem
from app.rules.prereq_engine import check_value, load_rules

DONE = {"provided", "verified", "not_applicable"}
NO_CHECKLIST = (
    "There is no checklist yet: it's built once the client's profile is confirmed. "
    "Finish discovery first."
)


def checklist_summary(items: list[PrereqItem]) -> str:
    """The checklist as the agent sees it: grouped by owner, with ids for record_prerequisite."""
    lines = ["Prerequisites checklist (ids are for record_prerequisite; don't show them to the client)."]
    for owner, heading in (("client", "The client does or provides"), ("capillary", "Capillary provides")):
        group = [item for item in items if item.owner == owner]
        if not group:
            continue
        lines.append(f"\n{heading}:")
        for item in group:
            if not item.blocking:
                flags = ", optional or later"
            elif owner == "client":
                flags = ", needed before integration"
            else:  # Capillary's values go into the code; placeholders stand in until they arrive
                flags = ", required in code, doesn't hold up integration"
            value = f", value: {item.value}" if item.value else ""
            lines.append(f"- [{item.status}{flags}{value}] {item.id}: {item.title}")
            lines.append(f"  How: {item.how} ({item.source})")
    open_client = [i for i in items if i.owner == "client" and i.status not in DONE]
    waiting = [i.id for i in open_client if i.blocking]
    later = [i.id for i in open_client if not i.blocking]
    lines.append(
        f"\nStill needed from the client before integration: {', '.join(waiting)}"
        if waiting
        else "\nEvery client item needed before integration is done."
    )
    if later:
        lines.append(f"Client items still open for later (mention them; don't call everything done): {', '.join(later)}")
    return "\n".join(lines)


def _items(state: dict) -> list[PrereqItem]:
    return [PrereqItem.model_validate(p) for p in state.get("prerequisites") or []]


@tool
def get_checklist(
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Show the client's prerequisites checklist and the status of each item."""
    items = _items(state)
    text = checklist_summary(items) if items else NO_CHECKLIST
    return Command(update={"messages": [ToolMessage(text, tool_call_id=tool_call_id)]})


@tool
def record_prerequisite(
    item_id: str,
    status: Literal["provided", "not_applicable", "pending"],
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    value: str | None = None,
) -> Command:
    """Record progress on one checklist item, after the client says so.

    status: "provided" once the client has done or received it, "not_applicable" if the client
    says it doesn't apply to them, "pending" to undo. value: only for identifiers the client
    states (application ID, bundle ID, SHA256); never pass keys, tokens or other secrets.
    """
    items = _items(state)

    def error(text: str) -> Command:
        msg = ToolMessage(text, tool_call_id=tool_call_id, status="error")
        return Command(update={"messages": [msg]})

    if not items:
        return error(NO_CHECKLIST)
    item = next((i for i in items if i.id == item_id), None)
    if item is None:
        return error(f"Unknown item '{item_id}'. Valid ids: {', '.join(i.id for i in items)}")
    note = ""
    if value is not None and value.strip():
        rule = load_rules(get_settings().knowledge_base_dir).by_id()[item_id]
        if not rule.value:
            # Dropped rather than rejected: storing nothing is the safe outcome, and an error
            # would only cost another model call to retry without it.
            note = f"Status recorded. The value was not stored: '{item_id}' doesn't take one.\n\n"
        elif problem := check_value(rule, value.strip()):
            return error(problem)
        else:
            item.value = value.strip()
    item.status = status

    return Command(
        update={
            "prerequisites": [i.model_dump() for i in items],
            "messages": [ToolMessage(note + checklist_summary(items), tool_call_id=tool_call_id)],
        }
    )


TOOLS = [get_checklist, record_prerequisite]
