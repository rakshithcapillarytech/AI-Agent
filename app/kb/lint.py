"""`kb lint`: enforce the platform-file template (PLAN.md §5.2).

    uv run python -m app.kb.lint            # all platform files
    uv run python -m app.kb.lint FILE...    # specific files
"""

import re
import sys
from pathlib import Path

import frontmatter

from app.config import get_settings

PLATFORMS = {"android", "ios", "react-native", "flutter", "web"}
CONFIG_MODES = {"firebase", "direct"}
MODULES = {
    "core", "push", "inapp", "inbox_api", "inbox_ui", "visitor", "gamification", "multi_account"
}
REQUIRED_FIELDS = [
    "platform", "config_mode", "sdk_package", "sdk_version", "modules_covered",
    "modules_missing", "sources", "owner", "last_verified", "review_status",
]
REQUIRED_HEADINGS = [
    "Coverage", "Requirements", "Prerequisites", "Steps", "Modules",
    "Verification", "Known Issues", "API Reference",
]
PLACEHOLDERS = {
    "account_id", "base_url", "ssl_public_key", "org_id", "application_id", "bundle_id",
    "gamification_key", "gamification_region", "gamification_base_url",
    "banner_id", "embed_id", "loyalty_id", "sdk_version",
}
_PLACEHOLDER = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
_H2 = re.compile(r"^## (.+?)\s*$", re.M)
_CALLOUT_KIND = re.compile(r"⚠️\s*(Gap|Correction|Source doc correction)\s*:")


def callouts(text: str) -> list[tuple[int, str]]:
    """Every ⚠️ callout as (1-based line, full text); blockquote callouts span their "> " lines."""
    lines = text.splitlines()
    found = []
    for i, line in enumerate(lines):
        if "⚠️" not in line:
            continue
        block = [line.strip().lstrip(">").strip()]
        if line.lstrip().startswith(">"):
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith(">"):
                block.append(lines[j].strip().lstrip(">").strip())
                j += 1
        found.append((i + 1, " ".join(part for part in block if part)))
    return found


def callout_issues(text: str) -> tuple[list[str], list[str]]:
    """(errors, warnings) for ⚠️ callouts. Corrections must say plainly what to use and avoid:
    `⚠️ Correction: ✅ Use … ❌ Don't use …`, so a model can't pick the wrong value."""
    errors, warnings = [], []
    for line, callout in callouts(text):
        match = _CALLOUT_KIND.search(callout)
        kind = match.group(1) if match else None
        if kind == "Correction" and not ("✅ Use" in callout and "❌" in callout):
            errors.append(f"L{line}: correction must state '✅ Use …' and '❌ Don't use …'")
        elif kind == "Source doc correction":
            errors.append(f"L{line}: old correction format; rewrite as '⚠️ Correction: ✅ Use … ❌ Don't use …'")
        elif kind is None:
            warnings.append(f"L{line}: callout should start with '⚠️ Gap:' or '⚠️ Correction:'")
    return errors, warnings


def lint_file(path: Path, kb_dir: Path) -> list[str]:
    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    meta, body = post.metadata, post.content
    problems = [f"missing front-matter field: {f}" for f in REQUIRED_FIELDS if f not in meta]

    rel = path.relative_to(kb_dir)
    expected_platform, expected_mode = rel.parts[0], rel.stem
    if meta.get("platform") != expected_platform:
        problems.append(f"platform {meta.get('platform')!r} doesn't match folder {expected_platform!r}")
    if meta.get("config_mode") != expected_mode:
        problems.append(f"config_mode {meta.get('config_mode')!r} doesn't match file name {expected_mode!r}")
    for field in ("modules_covered", "modules_missing"):
        unknown = set(meta.get(field) or []) - MODULES
        if unknown:
            problems.append(f"{field} has unknown modules: {sorted(unknown)}")

    headings = _H2.findall(body)
    problems += [f"missing heading: ## {h}" for h in REQUIRED_HEADINGS if h not in headings]
    present = [h for h in headings if h in REQUIRED_HEADINGS]
    if present != [h for h in REQUIRED_HEADINGS if h in present]:
        problems.append("required headings are out of template order")

    unknown = sorted(set(_PLACEHOLDER.findall(body)) - PLACEHOLDERS)
    if unknown:
        problems.append(f"unknown placeholders: {unknown}")
    if "<VERSION>" in body:
        problems.append("hard-coded <VERSION>; use {{sdk_version}} with front-matter sdk_version")
    problems += callout_issues(body)[0]
    return problems


def platform_files(kb_dir: Path) -> list[Path]:
    return sorted(
        p for p in kb_dir.glob("*/*.md")
        if p.parent.name in PLATFORMS and p.stem in CONFIG_MODES
    )


def main(argv: list[str]) -> int:
    kb_dir = get_settings().knowledge_base_dir
    files = [Path(a).resolve() for a in argv] if argv else platform_files(kb_dir)
    failed = 0
    for path in files:
        problems = lint_file(path, kb_dir)
        warnings = callout_issues(frontmatter.loads(path.read_text(encoding="utf-8")).content)[1]
        status = "FAIL" if problems else "warn" if warnings else "ok"
        print(f"{status:4}  {path.relative_to(kb_dir)}")
        for problem in problems:
            print(f"      - {problem}")
        if warnings:
            print(f"      ({len(warnings)} warning(s): old-format callouts, see `kb review`)")
        failed += bool(problems)
    print(f"\n{len(files) - failed}/{len(files)} files pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
