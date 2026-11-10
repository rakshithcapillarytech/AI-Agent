"""Integration tools: show the step plan, and move through it one step at a time.

The plan itself is built by the system when integration starts (phase_transition), from the
Steps section of each loaded platform file. The agent only reads it and reports progress.
"""

from typing import Annotated, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

NO_PLAN = "There is no integration plan yet: it's built once every prerequisite the client owns is done."


def plan_summary(steps: list[str], current: int) -> str:
    lines = ["Integration plan (ids are for the system; read each step from the named file section):"]
    for i, step in enumerate(steps):
        mark = "done" if i < current else "CURRENT" if i == current else "todo"
        lines.append(f"{i + 1}. [{mark}] {step}")
    if current >= len(steps):
        lines.append("\nEvery step is done. The system moves on to verification.")
    else:
        lines.append(
            f"\nWalk the client through step {current + 1} now. When they confirm it works, "
            "call complete_step."
        )
    return "\n".join(lines)


@tool
def get_integration_plan(state: Annotated[dict, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Show the integration steps for the client's platforms and which one is current."""
    steps, current = state.get("plan_steps") or [], state.get("current_step") or 0
    text = plan_summary(steps, current) if steps else NO_PLAN
    return Command(update={"messages": [ToolMessage(text, tool_call_id=tool_call_id)]})


@tool
def complete_step(
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    status: Literal["done", "skipped"] = "done",
) -> Command:
    """Finish the current step and move to the next, after the client confirms it works.

    status: "done" when the client completed it, "skipped" when the step doesn't apply to them
    (for example a CocoaPods step when they use SPM). Never skip a step just to hurry.
    """
    steps, current = state.get("plan_steps") or [], state.get("current_step") or 0

    def error(text: str) -> Command:
        return Command(update={"messages": [ToolMessage(text, tool_call_id=tool_call_id, status="error")]})

    if not steps:
        return error(NO_PLAN)
    if current >= len(steps):
        return error("Every step is already done.")
    return Command(
        update={
            "current_step": current + 1,
            "messages": [ToolMessage(plan_summary(steps, current + 1), tool_call_id=tool_call_id)],
        }
    )


@tool
def confirm_verification(
    state: Annotated[dict, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Record that the client has confirmed every verification check passes.

    Call it only after the client has reported each check from the Verification section of
    every platform file as working (not before, and not for a check that failed).
    """
    if state.get("phase") != "verification":
        msg = ToolMessage(
            "Verification hasn't started: finish the integration steps first.",
            tool_call_id=tool_call_id,
            status="error",
        )
        return Command(update={"messages": [msg]})
    return Command(
        update={
            "verified": True,
            "messages": [ToolMessage("Verification recorded. The integration is complete.", tool_call_id=tool_call_id)],
        }
    )


TOOLS = [get_integration_plan, complete_step, confirm_verification]
