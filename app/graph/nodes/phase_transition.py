"""Deterministic phase transitions: the LLM never decides when a phase is complete."""

from app.graph.state import IntegrationProfile, OnboardingState, Phase, PrereqItem
from app.kb.loader import files_for_profile

DONE_STATUSES = {"provided", "verified", "not_applicable"}


def next_phase(
    phase: Phase,
    profile: IntegrationProfile,
    prerequisites: list[PrereqItem],
    plan_steps: list[str],
    current_step: int,
) -> Phase:
    if phase == "discovery" and profile.confirmed:
        return "prerequisites"
    if phase == "prerequisites" and prerequisites:
        blocking = [p for p in prerequisites if p.blocking and p.owner == "client"]
        if all(p.status in DONE_STATUSES for p in blocking):
            return "integration"
    if phase == "integration" and plan_steps and current_step >= len(plan_steps):
        return "verification"
    return phase


def phase_transition(state: OnboardingState) -> dict:
    phase = state.get("phase") or "discovery"
    profile = IntegrationProfile.model_validate(state.get("profile") or {})
    new_phase = next_phase(
        phase,
        profile,
        [PrereqItem.model_validate(p) for p in state.get("prerequisites") or []],
        state.get("plan_steps") or [],
        state.get("current_step") or 0,
    )
    if new_phase == phase:
        return {}
    update: dict = {"phase": new_phase}
    if phase == "discovery":
        # Knowledge for this client's platforms × config modes, loaded whole from here on.
        update["loaded_files"] = files_for_profile(profile)
    return update
