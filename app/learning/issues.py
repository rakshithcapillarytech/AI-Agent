"""Learned issues: from a resolved thread to an approved knowledge file (PLAN.md §4 ⑥, §5.3). Drafts come from the report-back form (or, today, the chat assistant).

The agent writes a generic draft when the client confirms a fix (`resolve_issue`). An admin edits
and approves it; only then does `publish_issue` write `knowledge_base/issues/<platform>-<slug>.md`,
which search ranks first. `lint_issue` is the gate: a draft that fails it can't be published.
"""

import re
from datetime import date
from pathlib import Path

import frontmatter

from app.graph.nodes.guardrails import redact
from app.kb.search import clear_index

PLATFORMS = {"android", "ios", "react-native", "flutter", "web"}
CONFIG_MODES = {"firebase", "direct"}
FIELDS = ("error_signature", "root_cause", "fix", "platform", "config_mode")
LIMITS = {"error_signature": 200, "root_cause": 800, "fix": 1200}
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
CHANGELOG_HEADING = "## Learned issues (approved in the admin page)"


def slugify(text: str, limit: int = 50) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit].strip("-") or "issue"


def issue_filename(payload: dict) -> str:
    return f"{payload['platform']}-{slugify(payload['error_signature'])}.md"


def clean(payload: dict) -> dict:
    """Only the editable fields, trimmed; an empty config_mode means 'both modes'."""
    out = {k: (str(payload.get(k) or "").strip() or None) for k in FIELDS}
    out["config_mode"] = out["config_mode"] or None
    return out


def lint_issue(payload: dict, kb_dir: Path) -> list[str]:
    """Why this draft can't be published yet (empty list: it can)."""
    p = clean(payload)
    errors = []
    for name, limit in LIMITS.items():
        value = p[name]
        if not value:
            errors.append(f"{name} is required.")
        elif len(value) > limit:
            errors.append(f"{name} is longer than {limit} characters.")
        elif redact(value) != value:
            errors.append(f"{name} contains a secret (token or key). Remove it.")
        elif _EMAIL.search(value):
            errors.append(f"{name} contains an email address. Issues are shared across clients.")
    if p["platform"] not in PLATFORMS:
        errors.append(f"platform must be one of {', '.join(sorted(PLATFORMS))}.")
    elif p["config_mode"] and p["config_mode"] not in CONFIG_MODES:
        errors.append("config_mode must be firebase, direct, or empty.")
    elif p["config_mode"] and not (kb_dir / p["platform"] / f"{p['config_mode']}.md").is_file():
        errors.append(f"There is no knowledge file for {p['platform']}/{p['config_mode']}.")
    if not errors and (kb_dir / "issues" / issue_filename(p)).exists():
        errors.append("An issue with this platform and error text already exists.")
    return errors


def _sdk_version(p: dict, kb_dir: Path) -> str | None:
    if not p["config_mode"]:
        return None
    return frontmatter.load(kb_dir / p["platform"] / f"{p['config_mode']}.md").metadata.get("sdk_version")


def render_issue(payload: dict, kb_dir: Path, session_id: str) -> str:
    p = clean(payload)
    meta = {
        "platform": p["platform"],
        "config_mode": p["config_mode"],
        "sdk_version": _sdk_version(p, kb_dir),
        "status": "approved",
        "error_signature": p["error_signature"],
        "root_cause": p["root_cause"],
        "fix": p["fix"],
        "source_session": session_id,
        "approved": date.today().isoformat(),
    }
    body = (
        f"# {p['error_signature']}\n\n## Cause\n{p['root_cause']}\n\n## Fix\n{p['fix']}\n"
    )
    return frontmatter.dumps(frontmatter.Post(body, **{k: v for k, v in meta.items() if v is not None}))


def publish_issue(payload: dict, kb_dir: Path, session_id: str) -> Path:
    """Write the issue file and log it in CHANGELOG.md. Run lint_issue first."""
    p = clean(payload)
    path = kb_dir / "issues" / issue_filename(p)
    path.parent.mkdir(exist_ok=True)
    path.write_text(render_issue(p, kb_dir, session_id), encoding="utf-8")

    changelog = kb_dir / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8") if changelog.exists() else "# Knowledge base changelog\n"
    if CHANGELOG_HEADING not in text:
        text = text.rstrip("\n") + f"\n\n{CHANGELOG_HEADING}\n"
    scope = f"{p['platform']}/{p['config_mode']}" if p["config_mode"] else p["platform"]
    entry = f"- {date.today().isoformat()}: `issues/{path.name}` ({scope}): {p['error_signature']}\n"
    changelog.write_text(text.rstrip("\n") + "\n" + entry, encoding="utf-8")

    clear_index()  # the new issue is searchable immediately
    return path
