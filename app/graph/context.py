"""Builds the system prompt: a static block, then a phase/knowledge block.

Keep anything that changes per turn (timestamps, the evolving profile) out of here: the profile
reaches the model through tool results instead. The second block changes only on phase
transitions, so a cached prefix survives for most of a session (PLAN.md §6.2).
- Claude: both blocks get explicit `cache_control` breakpoints.
- Gemini: caching is implicit (prefix-based), so one plain string with the same ordering.
"""

from pathlib import Path

from langchain_core.messages import SystemMessage

from app.config import get_settings
from app.graph.state import OnboardingState
from app.kb.loader import read_files

PROMPTS_DIR = Path(__file__).parent / "prompts"
_CACHE = {"type": "ephemeral"}


def build_system_message(state: OnboardingState) -> SystemMessage:
    settings = get_settings()
    phase = state.get("phase") or "discovery"
    static = (PROMPTS_DIR / "system.md").read_text(encoding="utf-8")
    phase_instructions = (PROMPTS_DIR / "phases" / f"{phase}.md").read_text(encoding="utf-8")

    loaded = state.get("loaded_files") or []
    knowledge = (
        read_files(loaded, settings.knowledge_base_dir)
        if loaded
        else "No platform files loaded yet; they load once the client confirms their profile."
    )
    dynamic = (
        f'<phase name="{phase}">\n{phase_instructions}\n</phase>\n\n'
        f"<knowledge>\n{knowledge}\n</knowledge>"
    )

    if settings.llm_provider == "anthropic":
        return SystemMessage(
            content=[
                {"type": "text", "text": static, "cache_control": _CACHE},
                {"type": "text", "text": dynamic, "cache_control": _CACHE},
            ]
        )
    return SystemMessage(content=f"{static}\n\n{dynamic}")
