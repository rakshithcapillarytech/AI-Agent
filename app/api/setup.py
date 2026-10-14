"""Starting a session from the portal's setup wizard.

The wizard collects the profile with structured inputs, so a complete profile arrives already
confirmed by the client: the session starts in the prerequisites phase with the matching
knowledge files loaded. An incomplete one (e.g. "not sure" whether the app uses Firebase) starts
in discovery, and the agent asks for what's missing.
"""

from app.graph.state import IntegrationProfile
from app.kb.loader import files_for_profile

# History entries starting with this are rendered as a setup card rather than a chat bubble.
SETUP_HEADER = "Here are our setup details from the onboarding form:"

_PLATFORM_LABELS = {
    "android": "Android (native)",
    "ios": "iOS (native)",
    "react-native": "React Native",
    "flutter": "Flutter",
    "web": "Web",
}
_MODE_LABELS = {"firebase": "uses Firebase", "direct": "doesn't use Firebase", None: "not sure about Firebase"}


def setup_message(profile: IntegrationProfile) -> str:
    """The client's opening message, written from the form so the agent sees the same facts."""
    platforms = "; ".join(
        f"{_PLATFORM_LABELS[p.platform]} ({_MODE_LABELS[p.config_mode]})" for p in profile.platforms
    )
    lines = [
        SETUP_HEADER,
        f"- Company: {profile.company or 'not given'}",
        f"- Apps: {platforms or 'not given'}",
        f"- Features: {', '.join(profile.modules) or 'not given'}",
        f"- Environment: {profile.environment or 'not given'}",
        f"- Region: {profile.region or 'not given'}",
        f"- Customer ID type: {profile.customer_id_type or 'not given'}",
    ]
    if profile.contacts:
        lines.append(f"- Contacts: {', '.join(profile.contacts)}")
    if profile.go_live_date:
        lines.append(f"- Target go-live: {profile.go_live_date}")
    lines.append("Please start our onboarding.")
    return "\n".join(lines)


def initial_state(profile: IntegrationProfile) -> dict:
    """Graph state for a session started from the wizard (excluding the opening message)."""
    profile = profile.model_copy(update={"confirmed": not profile.missing_required()})
    return {
        "profile": profile.model_dump(),
        "phase": "prerequisites" if profile.confirmed else "discovery",
        "loaded_files": files_for_profile(profile) if profile.confirmed else [],
    }
