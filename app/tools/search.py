"""Search tools. Documentation search covers the client's own files by default; approved past
issues (knowledge_base/issues/) are searched separately and rank first."""

from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.kb.search import search

NO_RESULTS = "No matching sections found."


def _apps(state: dict) -> set[tuple[str, str | None]]:
    profile = IntegrationProfile.model_validate(state.get("profile") or {})
    return {(p.platform, p.config_mode) for p in profile.platforms}


@tool
def search_knowledge(
    query: str, state: Annotated[dict, InjectedState], all_platforms: bool = False
) -> str:
    """Find where the documentation covers something: an error message, API name or topic.

    Searches this client's own knowledge files, and also approved past issues that match their
    apps. Set all_platforms only to look at other platforms' files; never carry their steps,
    keys or code over to this client.
    """
    kb = get_settings().knowledge_base_dir
    files = None if all_platforms else state.get("loaded_files") or None
    hits = search(kb, query, files=files, apps=_apps(state))
    if not hits:
        return NO_RESULTS + " Say so plainly and offer to bring in a Capillary engineer."
    return "Matches, best first (cite them as file › heading):\n" + "\n".join(h.render() for h in hits)


@tool
def search_issues(query: str, state: Annotated[dict, InjectedState]) -> str:
    """Find approved past issues (symptom, cause, fix) that match the client's error or problem."""
    kb = get_settings().knowledge_base_dir
    hits = search(kb, query, apps=_apps(state), issues_only=True)
    if not hits:
        return (
            "No approved past issue matches. Check the Known Issues section of the client's "
            "platform file with search_knowledge."
        )
    return "Past issues, best first:\n" + "\n".join(h.render() for h in hits)


TOOLS = [search_knowledge, search_issues]
