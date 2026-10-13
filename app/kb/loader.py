"""Profile → knowledge files mapping, and loading them into the prompt (PLAN.md §5.4 stage A)."""

from pathlib import Path

import frontmatter

from app.graph.state import IntegrationProfile

SHARED_ALWAYS = ["_shared/overview.md", "_shared/prerequisites.md"]
SHARED_FIREBASE = "_shared/firebase-setup.md"


def files_for_profile(profile: IntegrationProfile) -> list[str]:
    """Every knowledge file this client needs, whether or not it has been written yet."""
    files = list(SHARED_ALWAYS)
    if any(p.config_mode == "firebase" for p in profile.platforms):
        files.append(SHARED_FIREBASE)
    for p in profile.platforms:
        if p.config_mode:
            files.append(f"{p.platform}/{p.config_mode}.md")
    return list(dict.fromkeys(files))


def render_versions(text: str) -> str:
    """Fill {{sdk_version}} from the file's own front-matter, the single place versions live."""
    version = frontmatter.loads(text).metadata.get("sdk_version")
    return text.replace("{{sdk_version}}", str(version)) if version else text


def read_files(rel_paths: list[str], kb_dir: Path) -> str:
    """Concatenate files with clear delimiters so content from different platforms never blurs.

    A file that doesn't exist yet is reported as missing, so the agent escalates instead of
    guessing.
    """
    parts = []
    for rel in rel_paths:
        path = kb_dir / rel
        if path.is_file():
            text = render_versions(path.read_text(encoding="utf-8"))
            parts.append(f'<file path="{rel}">\n{text}\n</file>')
        else:
            parts.append(
                f'<file path="{rel}" status="missing">This knowledge file has not been written '
                "yet. Do not guess its contents; tell the client and offer to escalate.</file>"
            )
    return "\n\n".join(parts)
