"""The downloadable integration guide: one Markdown file tailored to a client's profile.

The client attaches it to their own AI assistant (Claude, Cursor, ChatGPT …), so it carries its
own instructions and contains only the knowledge for their platforms and config modes.
"""

import re
from datetime import date
from pathlib import Path

import frontmatter

from app.graph.state import IntegrationProfile
from app.kb.loader import files_for_profile, render_versions


class GuideNotReady(Exception):
    """The profile doesn't yet say which platform files apply (e.g. Firebase is "not sure")."""


PLATFORM_LABELS = {
    "android": "Android (native)",
    "ios": "iOS (native)",
    "react-native": "React Native",
    "flutter": "Flutter",
    "web": "Web",
}
MODE_LABELS = {"firebase": "with Firebase", "direct": "without Firebase Remote Config"}
MODULE_LABELS = {
    "core": "User tracking (core)",
    "push": "Push notifications",
    "inapp": "In-app messages",
    "inbox_api": "Notification inbox",
    "inbox_ui": "Ready-made inbox screen",
    "visitor": "Guest users (visitor flow)",
    "gamification": "Gamification",
    "multi_account": "Several brands in one app (multi-account)",
}
CUSTOMER_ID_LABELS = {
    "mobile": "Mobile number",
    "email": "Email address",
    "externalId": "Your own customer ID (externalId)",
    "InTouchUserId": "Capillary user ID (InTouchUserId)",
    "FCMToken": "Device token (FCMToken)",
}
PLACEHOLDER_LEGEND = [
    ("{{account_id}}", "Account Id, from Capillary"),
    ("{{base_url}}", "Base URL, from Capillary"),
    ("{{ssl_public_key}}", "SSL public key, from Capillary (mobile only)"),
    ("{{org_id}}", "Org Id, from Capillary"),
    ("{{gamification_key}}", "Gamification write key, from Capillary"),
    ("{{gamification_region}}", "Gamification region (IN, US or ME), from Capillary"),
    ("{{gamification_base_url}}", "Gamification base URL, from Capillary (if provided)"),
    ("{{banner_id}} / {{embed_id}} / {{loyalty_id}}", "Gamification view IDs, from Capillary"),
    ("{{application_id}}", "Your Android application ID (package name)"),
    ("{{bundle_id}}", "Your iOS bundle ID"),
]

INSTRUCTIONS = """\
> **For the AI assistant reading this file.** You are helping a developer integrate Capillary's
> Hydra SDK (Experience+) into the app described above. Follow these rules:
> 1. Use **only** this file for SDK facts: method names, config keys, versions, file locations
>    and step order. Copy names exactly as written. If something isn't covered here, say so and
>    suggest asking Capillary. Don't fill the gap from general knowledge.
> 2. Each platform section applies only to that platform and mode. Never mix steps or keys
>    between sections.
> 3. `⚠️ Correction:` lines override everything else here: always use the **✅ Use** value and
>    never recommend the **❌ Don't use** value.
> 4. `⚠️ Gap:` lines mark things the documentation doesn't cover. Tell the developer and suggest
>    confirming with their Capillary contact.
> 5. `{{placeholders}}` are values Capillary or the developer supplies (see the table above).
>    Never invent values for them.
> 6. Never ask for secrets (GitHub tokens, private keys). They stay on the developer's machine."""

_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^(#{1,5}) ")


def _demote_headings(markdown: str) -> str:
    """Push every heading one level down (outside code fences) so files nest under the guide."""
    out, in_fence = [], False
    for line in markdown.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and _HEADING.match(line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "client"


def guide_filename(profile: IntegrationProfile) -> str:
    platforms = "-".join(p.platform for p in profile.platforms)
    return f"hydra-integration-guide-{_slug(profile.company or 'client')}-{platforms}.md"


def build_guide(profile: IntegrationProfile, kb_dir: Path, today: date | None = None) -> str:
    """Render the guide. Raises GuideNotReady if any platform's config mode is still unknown."""
    if not profile.platforms or any(p.config_mode is None for p in profile.platforms):
        raise GuideNotReady("Choose whether each app uses Firebase before downloading the guide.")

    today = today or date.today()
    apps = ", ".join(f"{PLATFORM_LABELS[p.platform]} {MODE_LABELS[p.config_mode]}" for p in profile.platforms)
    rows = [
        ("Company", profile.company or "—"),
        ("Apps", apps),
        ("Features", ", ".join(MODULE_LABELS[m] for m in profile.modules) or "—"),
        ("Environment", {"uat": "Testing (UAT)", "production": "Live (Production)"}.get(profile.environment or "", "—")),
        ("Region", profile.region or "—"),
        ("Customers sign in with", CUSTOMER_ID_LABELS.get(profile.customer_id_type or "", "—")),
    ]

    parts = [
        f"# Hydra SDK integration guide: {profile.company or 'your app'}",
        "",
        f"Generated by the Experience+ Integration Copilot on {today.isoformat()}. "
        "Attach this file to your AI assistant (Claude, Cursor, ChatGPT …) and ask your question; "
        "it contains only the documentation for your setup.",
        "",
        "## Your setup",
        "",
        "| | |",
        "|---|---|",
        *[f"| {label} | {value} |" for label, value in rows],
        "",
        INSTRUCTIONS,
        "",
        "## Placeholders used in the code",
        "",
        "| Placeholder | Replace with |",
        "|---|---|",
        *[f"| `{name}` | {meaning} |" for name, meaning in PLACEHOLDER_LEGEND],
        "",
        "> This guide is a draft that Capillary engineers are still reviewing. When something "
        "doesn't work as described, check with your Capillary contact.",
    ]

    for rel in files_for_profile(profile):
        path = kb_dir / rel
        if not path.is_file():
            continue
        content = frontmatter.loads(render_versions(path.read_text(encoding="utf-8"))).content
        parts += ["", "---", "", _demote_headings(content.strip())]

    return "\n".join(parts) + "\n"
