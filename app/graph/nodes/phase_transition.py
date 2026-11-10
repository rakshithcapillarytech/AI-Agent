"""Deterministic phase transitions: the LLM never decides when a phase is complete."""

from app.config import get_settings
from app.graph.state import IntegrationProfile, OnboardingState, Phase, PrereqItem
from app.kb.loader import files_for_profile
from app.kb.steps import steps_for_files
from app.rules.prereq_engine import build_checklist, load_rules

DONE_STATUSES = {"provided", "verified", "not_applicable"}


def next_phase(
    phase: Phase,
    profile: IntegrationProfile,
    prerequisites: list[PrereqItem],
    plan_steps: list[str],
    current_step: int,
    verified: bool = False,
) -> Phase:
    if phase == "discovery" and profile.confirmed:
        return "prerequisites"
    if phase == "prerequisites" and prerequisites:
        blocking = [p for p in prerequisites if p.blocking and p.owner == "client"]
        if all(p.status in DONE_STATUSES for p in blocking):
            return "integration"
    if phase == "integration" and plan_steps and current_step >= len(plan_steps):
        return "verification"
    if phase == "verification" and verified:
        return "done"
    return phase


def phase_transition(state: OnboardingState) -> dict:
    phase = state.get("phase") or "discovery"
    profile = IntegrationProfile.model_validate(state.get("profile") or {})
    checklist = [PrereqItem.model_validate(p) for p in state.get("prerequisites") or []]
    update: dict = {}

    # From the moment discovery ends, the knowledge files and the checklist follow the profile,
    # so a platform or module added later (e.g. "we also have an iOS app") is picked up.
    if phase != "discovery" or profile.confirmed:
        files = files_for_profile(profile)
        if files != (state.get("loaded_files") or []):
            update["loaded_files"] = files
        rules = load_rules(get_settings().knowledge_base_dir)
        rebuilt = build_checklist(profile, rules, existing=checklist)
        if rebuilt != checklist:
            update["prerequisites"] = [item.model_dump() for item in rebuilt]
        checklist = rebuilt

    plan = state.get("plan_steps") or []
    step = state.get("current_step") or 0
    new_phase = next_phase(phase, profile, checklist, plan, step, bool(state.get("verified")))
    if new_phase != phase:
        update["phase"] = new_phase

    # The integration plan comes from the Steps sections of the loaded files, built once when the
    # phase starts (not at every change, so the client's progress through it is never reset).
    if new_phase == "integration" and not plan:
        files = update.get("loaded_files", state.get("loaded_files") or [])
        update["plan_steps"] = steps_for_files(files, get_settings().knowledge_base_dir)
        update["current_step"] = 0
    return update
