"""Troubleshooting tools: log fix attempts, record a resolution, escalate to a human.

Escalation uses LangGraph's `interrupt()`: the thread pauses, an engineer answers in the admin
queue, and the thread resumes with their answer as this tool's result (chat assistant, PLAN.md §14).
"""

from typing import Annotated, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, interrupt

from app.graph.nodes.guardrails import redact
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
    error_signature: str,
    root_cause: str,
    fix: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    platform: Literal["android", "ios", "react-native", "flutter", "web"] | None = None,
    config_mode: Literal["firebase", "direct"] | None = None,
) -> Command:
    """Record that the client's problem is fixed, once they confirm it worked.

    This becomes a draft that a Capillary engineer reviews before it joins the knowledge base,
    and it is shared across clients. So write it generically: no company names, app IDs, emails,
    tokens or keys. error_signature: the symptom or exact error text (one line). root_cause: why it
    happened. fix: what resolved it. platform / config_mode: where it applies; omit them when the
    client has only one app (the system fills them in).
    """
    issue = state.get("open_issue") or {}
    profile = IntegrationProfile.model_validate(state.get("profile") or {})
    apps = [(p.platform, p.config_mode) for p in profile.platforms]
    if platform is None and len(apps) == 1:
        platform, config_mode = apps[0]
    record = {
        "error_signature": redact(error_signature)[:300],
        "root_cause": redact(root_cause)[:900],
        "fix": redact(fix)[:1300],
        "platform": platform,
        "config_mode": config_mode,
        "attempts": issue.get("attempts", 0),
        "tried": [redact(t) for t in issue.get("tried", [])],
        "step": _step(state),
    }
    return Command(
        update={
            "open_issue": None,
            "resolved_issues": [*(state.get("resolved_issues") or []), record],
            "messages": [ToolMessage("Recorded as resolved. It will be reviewed before it is added to the knowledge.", tool_call_id=tool_call_id)],
        }
    )


@tool
def report_doc_gap(
    question: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Report something the client needs that the documentation doesn't cover.

    Call it when you tell the client something isn't documented (a missing file, a `⚠️ Gap:`, or
    no matching section), so Capillary can fill the gap. question: what the client needs, in one
    generic line (no names, IDs, tokens or keys). Then carry on helping, or escalate.
    """
    gaps = [*(state.get("doc_gaps") or []), {"question": redact(question)[:400], "step": _step(state)}]
    return Command(
        update={
            "doc_gaps": gaps,
            "messages": [ToolMessage("Reported to Capillary's documentation team.", tool_call_id=tool_call_id)],
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


TOOLS = [log_fix_attempt, resolve_issue, report_doc_gap, escalate_to_human]
