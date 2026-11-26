"""Plan and apply automatic value updates.

A changed page is *eligible* only if (1) we kept the version a person reviewed, (2) an anchored fact on it moved to a new
value that qualifies (a version-like number), and (3) applying exactly those substitutions to the reviewed page gives the
new page: nothing else on the page changed. Every other change is left to a person.

Where a substitution is applied:
  - if no anchor on a page that did NOT change still carries the old value, the value moved everywhere: all files under the
    configured roots (guides, FAQ, requirements, step texts, evals);
  - otherwise only the guides built from the changed page, their platform's step texts and eval questions, so another
    platform that still uses the old value is not touched. The gate then decides whether that is enough.
anchors.yaml is edited fact by fact.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from app.sync.anchors import Anchor, load_anchors
from app.sync.impact import changed_pages
from app.sync.models import Manifest, SyncConfig
from app.sync.store import SnapshotStore
from app.sync.values import Substitution, apply_text, count_matches, derive, explained, qualifies


@dataclass
class PageChange:
    slug: str
    subs: list[Substitution]
    anchor_ids: list[str]
    guides: list[str]


@dataclass
class Plan:
    eligible: list[PageChange] = field(default_factory=list)
    needs_person: dict[str, str] = field(default_factory=dict)  # slug -> why a person has to look


@dataclass
class FileEdit:
    path: str  # relative to the repository root
    replacements: int


def plan_changes(kb_dir: Path, config: SyncConfig, store: SnapshotStore, manifest: Manifest) -> Plan:
    plan = Plan()
    anchors = load_anchors(kb_dir)
    minimum = config.auto_update.min_value_length
    pages: dict[str, tuple[str, str]] = {}
    own: dict[str, tuple[list[Substitution], list[str]]] = {}
    for slug in changed_pages(manifest):
        old, new = store.read_reviewed(slug), store.read_page(slug)
        if old is None or new is None:
            plan.needs_person[slug] = "no reviewed copy was kept to compare with"
            continue
        pages[slug] = (old, new)
        subs: list[Substitution] = []
        ids: list[str] = []
        for anchor in (a for a in anchors if a.page == slug):
            sub = derive(old, new, anchor.text)
            if sub and qualifies(sub, minimum):
                ids.append(anchor.id)
                if sub not in subs:
                    subs.append(sub)
        own[slug] = (subs, ids)
    # a value found on one page (say a new SDK version) also explains pages that mention it without an anchored fact
    known = [s for subs, _ in own.values() for s in subs]
    known = list(dict.fromkeys(known))
    for slug, (old, new) in pages.items():
        subs, ids = own[slug]
        shared = [s for s in known if count_matches(old, s)]
        chosen = next((c for c in (subs, shared) if c and explained(old, new, c)), None)
        if chosen is None:
            plan.needs_person[slug] = "no key fact simply moved to a new version-like value (or the page changed in other ways)"
        else:
            plan.eligible.append(PageChange(slug, chosen, ids, config.guides_for_page(slug)))
    return plan


def _is_global(sub: Substitution, plan: Plan, anchors: list[Anchor]) -> bool:
    """Has this value moved everywhere? True when no anchor outside the eligible pages still carries the old value."""
    moved = {c.slug for c in plan.eligible}
    return not any(sub.old in (a.text + " " + (a.guide_text or "")) for a in anchors if a.page not in moved)


def _allowed(repo_root: Path, path: Path, config: SyncConfig) -> bool:
    rel = path.relative_to(repo_root).as_posix()
    cfg = config.auto_update
    return path.suffix in cfg.extensions and not any(rel == e or rel.startswith(e.rstrip("/") + "/") for e in cfg.exclude)


def _global_files(repo_root: Path, config: SyncConfig) -> list[Path]:
    files = []
    for root in config.auto_update.roots:
        base = repo_root / root
        if base.is_dir():
            files += [p for p in sorted(base.rglob("*")) if p.is_file() and _allowed(repo_root, p, config)]
    return files


def _scoped_files(repo_root: Path, kb_dir: Path, change: PageChange, anchors: list[Anchor], config: SyncConfig) -> list[Path]:
    guides = set(change.guides) | {g for a in anchors if a.id in change.anchor_ids for g in a.used_in}
    platforms = {g.split("/")[0] for g in guides if not g.startswith("_shared/")}
    candidates = [kb_dir / g for g in sorted(guides)]
    candidates += [kb_dir / "step_summaries" / f"{p}.yaml" for p in sorted(platforms)]
    for p in sorted(platforms):
        candidates += sorted((repo_root / "evals" / "deep").glob(f"{p}-*.yaml"))
    return [c for c in candidates if c.is_file() and _allowed(repo_root, c, config)]


def _edit_anchors(kb_dir: Path, plan: Plan) -> int:
    path = kb_dir / "anchors.yaml"
    if not path.is_file():
        return 0
    by_page = {c.slug: c.subs for c in plan.eligible}
    parts = re.split(r"(?m)^(?=\s*- id: )", path.read_text(encoding="utf-8"))
    changed = 0
    for n, block in enumerate(parts):
        page = re.search(r"(?m)^\s*page: (\S+)", block)
        if re.match(r"\s*- id: ", block) and page and page.group(1) in by_page:
            new = apply_text(block, by_page[page.group(1)])
            changed += new != block
            parts[n] = new
    path.write_text("".join(parts), encoding="utf-8")
    return changed


def apply_plan(repo_root: Path, kb_dir: Path, config: SyncConfig, plan: Plan) -> list[FileEdit]:
    """Write the substitutions into the files. Returns what changed."""
    anchors = load_anchors(kb_dir)
    totals: dict[Path, int] = {}
    everywhere = _global_files(repo_root, config)
    for change in plan.eligible:
        scoped = _scoped_files(repo_root, kb_dir, change, anchors, config)
        for sub in change.subs:
            for path in everywhere if _is_global(sub, plan, anchors) else scoped:
                text = path.read_text(encoding="utf-8")
                hits = count_matches(text, sub)
                if hits:
                    path.write_text(apply_text(text, [sub]), encoding="utf-8")
                    totals[path] = totals.get(path, 0) + hits
    edits = [FileEdit(p.relative_to(repo_root).as_posix(), n) for p, n in sorted(totals.items())]
    if (n := _edit_anchors(kb_dir, plan)):
        edits.append(FileEdit((kb_dir / "anchors.yaml").relative_to(repo_root).as_posix(), n))
    return edits
