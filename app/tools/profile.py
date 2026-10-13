"""Discovery tools: record and confirm the client's IntegrationProfile."""

from typing import Annotated, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import BaseModel

from app.graph.state import IntegrationProfile, Module, PlatformDetails


class ProfileUpdate(BaseModel):
    """Only fields the client has actually stated. Omit everything else."""

    company: str | None = None
    platforms: list[PlatformDetails] | None = None
    modules: list[Module] | None = None
    environment: Literal["uat", "production"] | None = None
    region: Literal["IN", "US", "ME"] | None = None
    customer_id_type: Literal["mobile", "email", "externalId", "InTouchUserId", "FCMToken"] | None = None
    contacts: list[str] | None = None
    go_live_date: str | None = None


def merge_profile(current: IntegrationProfile, updates: ProfileUpdate) -> IntegrationProfile:
    data = current.model_dump()
    changes = updates.model_dump(exclude_none=True)

    # Platforms merge by name so details given one platform at a time accumulate.
    if "platforms" in changes:
        by_name = {p["platform"]: p for p in data["platforms"]}
        for incoming in changes.pop("platforms"):
            existing = by_name.get(incoming["platform"], {})
            by_name[incoming["platform"]] = {
                **existing,
                **{k: v for k, v in incoming.items() if v is not None},
            }
        data["platforms"] = list(by_name.values())

    data.update(changes)
    data["confirmed"] = False  # any change needs the client to re-confirm
    return IntegrationProfile.model_validate(data)


def _summary(profile: IntegrationProfile) -> str:
    missing = profile.missing_required()
    return (
        f"Current profile: {profile.model_dump_json(exclude_none=True)}\n"
        f"Still missing: {', '.join(missing) if missing else 'nothing; ask the client to confirm'}"
    )


@tool
def update_profile(
    updates: ProfileUpdate,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Record facts the client has stated about their app and integration needs."""
    if isinstance(updates, dict):
        updates = ProfileUpdate.model_validate(updates)
    current = IntegrationProfile.model_validate(state.get("profile") or {})
    profile = merge_profile(current, updates)
    return Command(
        update={
            "profile": profile.model_dump(),
            "messages": [ToolMessage(_summary(profile), tool_call_id=tool_call_id)],
        }
    )


@tool
def confirm_profile(
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Mark the profile as confirmed. Call only after the client explicitly says it is correct."""
    profile = IntegrationProfile.model_validate(state.get("profile") or {})
    missing = profile.missing_required()
    if missing:
        msg = ToolMessage(
            f"Cannot confirm yet. Missing: {', '.join(missing)}",
            tool_call_id=tool_call_id,
            status="error",
        )
        return Command(update={"messages": [msg]})
    profile.confirmed = True
    return Command(
        update={
            "profile": profile.model_dump(),
            "messages": [ToolMessage("Profile confirmed.", tool_call_id=tool_call_id)],
        }
    )


TOOLS = [update_profile, confirm_profile]
