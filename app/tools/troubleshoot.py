"""Troubleshooting tools: log fix attempts, record a resolution, escalate to a human.

Escalation uses LangGraph's `interrupt()`: the thread pauses, an engineer answers in the admin
queue, and the thread resumes with their answer as this tool's result (PLAN.md §4 ⑥).
"""

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, interrupt

from app.graph.state import IntegrationProfile

MAX_ATTEMPTS = 3


def _step(state: dict) -> str | None:
    steps, current = state.get("plan_steps") or [], state.get("current_step") or 0
    return steps[current] if current < len(steps) else None


@tool
def log_fix_attempt(
    problem: str,
    fix: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Record that you proposed a fix for the client's current problem.

    Call it each time you suggest a fix. problem: the issue in one line (error text, platform,
    step). fix: what you proposed. After 3 fixes without success the system tells you to escalate.
    """
    issue = state.get("open_issue") or {"attempts": 0, "tried": []}
    issue = {
        "problem": problem[:400],
        "attempts": issue["attempts"] + 1,
        "tried": [*issue["tried"], fix[:400]],
    }
    text = f"Logged fix attempt {issue['attempts']} for this problem."
    if issue["attempts"] >= MAX_ATTEMPTS:
        text += (
            f" {MAX_ATTEMPTS} fixes have been tried without success: if the client says this "
            "one didn't work either, call escalate_to_human instead of guessing again."
        )
    return Command(update={"open_issue": issue, "messages": [ToolMessage(text, tool_call_id=tool_call_id)]})


@tool
def resolve_issue(
    problem: str,
    resolution: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Record that the client's problem is fixed, once they confirm it. problem and resolution in one line each."""
    issue = state.get("open_issue") or {}
    profile = IntegrationProfile.model_validate(state.get("profile") or {})
    record = {
        "problem": problem[:400],
        "resolution": resolution[:600],
        "attempts": issue.get("attempts", 0),
        "tried": issue.get("tried", []),
        "step": _step(state),
        "apps": [f"{p.platform}/{p.config_mode}" for p in profile.platforms],
    }
    return Command(
        update={
            "open_issue": None,
            "resolved_issues": [*(state.get("resolved_issues") or []), record],
            "messages": [ToolMessage("Recorded as resolved.", tool_call_id=tool_call_id)],
        }
    )


@tool
def escalate_to_human(
    summary: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Hand the client's problem to a Capillary engineer and wait for their answer.

    Use it when 3 fixes have failed, when the knowledge doesn't cover what the client needs
    (a missing file, a `⚠️ Gap:`), or when the client asks for a human. summary: what the client
    is trying to do and what is going wrong, with the exact error text. Tell the client an
    engineer has been asked to help *before* you call it; the reply arrives later in this chat.
    """
    issue = state.get("open_issue") or {}
    answer = interrupt(
        {
            "summary": summary[:1000],
            "tried": issue.get("tried", []),
            "step": _step(state),
            "phase": state.get("phase"),
        }
    )
    text = (
        f"A Capillary engineer replied:\n{answer}\n\n"
        "Relay this to the client in your own words and ask them to try it and tell you the result."
    )
    return Command(update={"open_issue": None, "messages": [ToolMessage(text, tool_call_id=tool_call_id)]})


TOOLS = [log_fix_attempt, resolve_issue, escalate_to_human]
