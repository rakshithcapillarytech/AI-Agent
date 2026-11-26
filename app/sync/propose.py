"""Turn a change in the online docs into a ready update, on git branches. Never pushes.

    1. branch from where you are, fetch the docs, commit the new snapshot and report            (branch docs-sync/<time>)
    2. for pages whose whole change is a version-like value: write the new value into the guides and everything built from
       them, run the gate (tests, template lint, audit, key facts)                                (branch ...-values)
    3. gate passed -> mark those pages reviewed and commit; gate failed -> keep the attempt on its branch for a person
    4. optionally merge (fast-forward only) so the app serves the updated guides at once; pages with other changes stay
       flagged for a person, with an optional AI draft of suggested edits next to them

Without --merge nothing reaches your branch: you get the branches to inspect. The tree must be clean when you start.
"""

import subprocess
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.sync.apply import FileEdit, apply_plan, plan_changes
from app.sync.client import Fetcher
from app.sync.gate import GateResult, passed, run_gate
from app.sync.impact import store_for
from app.sync.models import load_config
from app.sync.report import write_report
from app.sync.service import run_and_report


class ProposalError(Exception):
    """The update couldn't be prepared (not a git repository, uncommitted changes, a git command failed)."""


@dataclass
class Proposal:
    status: str  # nothing | fetch-failed | merged | ready | needs-person
    detail: str = ""
    branch: str | None = None
    applied: list[dict] = field(default_factory=list)
    needs_person: dict[str, str] = field(default_factory=dict)
    edits: list[FileEdit] = field(default_factory=list)
    gate: list[GateResult] = field(default_factory=list)
    merged: bool = False
    created_at: str = ""


def _git(root: Path, *args: str, check: bool = True) -> str:
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if check and done.returncode:
        raise ProposalError(f"git {' '.join(args)}: {(done.stderr or done.stdout).strip()}")
    return done.stdout


def _commit(root: Path, message: str) -> bool:
    _git(root, "add", "-A")
    if not _git(root, "status", "--porcelain").strip():
        return False
    _git(root, "commit", "-q", "-m", message)
    return True


def propose(
    repo_root: Path,
    kb_dir: Path,
    *,
    fetch: bool = True,
    merge: bool = False,
    gate_fn: Callable[[Path], list[GateResult]] = run_gate,
    fetcher: Fetcher | None = None,
    drafter: Callable[[Path], Path | None] | None = None,
    now: datetime | None = None,
) -> Proposal:
    if not (repo_root / ".git").exists():
        raise ProposalError("not a git repository")
    if _git(repo_root, "status", "--porcelain", "--untracked-files=no").strip():
        raise ProposalError("there are uncommitted changes; commit or stash them first")
    original = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%d-%H%M%S")
    branch = f"docs-sync/{stamp}"
    proposal = Proposal(status="nothing", branch=branch, created_at=stamp)
    _git(repo_root, "checkout", "-q", "-b", branch)

    def abandon(status: str, detail: str) -> Proposal:
        _git(repo_root, "checkout", "-q", "-f", original)
        _git(repo_root, "branch", "-q", "-D", branch, check=False)
        proposal.status, proposal.detail, proposal.branch = status, detail, None
        return proposal

    try:
        if fetch:
            result = run_and_report(kb_dir, fetcher)
            if not result.index_ok:
                return abandon("fetch-failed", "; ".join(f"{k}: {v}" for k, v in result.failed.items()))
        if not _git(repo_root, "status", "--porcelain").strip():
            return abandon("nothing", "the online docs match the snapshot")

        config = load_config(kb_dir)
        store = store_for(config, kb_dir)
        manifest = store.load()
        plan = plan_changes(kb_dir, config, store, manifest)
        _commit(repo_root, "Docs sync: update the snapshot of Capillary's online docs")
        target = branch
        proposal.needs_person = dict(plan.needs_person)

        if plan.eligible:
            values_branch = f"{branch}-values"
            _git(repo_root, "checkout", "-q", "-b", values_branch)
            proposal.edits = apply_plan(repo_root, kb_dir, config, plan)
            proposal.gate = gate_fn(repo_root)
            proposal.applied = [
                {"slug": c.slug, "values": [f"{s.old} -> {s.new}" for s in c.subs], "facts": c.anchor_ids} for c in plan.eligible
            ]
            summary = "; ".join(v for a in proposal.applied for v in a["values"])
            if passed(proposal.gate):
                manifest = store.load()
                store.accept(manifest, [c.slug for c in plan.eligible])
                store.save(manifest)
                write_report(kb_dir)
                _commit(repo_root, f"Docs sync: update values in the guides ({summary})")
                target = values_branch
            else:
                _commit(repo_root, f"Docs sync: attempted value update, the checks failed ({summary})")
                _git(repo_root, "checkout", "-q", branch)  # the attempt stays on its own branch for a person
                proposal.detail = "the checks failed on the value update; it is kept on branch " + values_branch
                proposal.applied = []
                proposal.needs_person.update({c.slug: "value update failed the checks" for c in plan.eligible})

        _git(repo_root, "checkout", "-q", target)
        if drafter and proposal.needs_person:
            drafter(kb_dir)
        proposal.merged = merge
        proposal.status = "merged" if merge else ("needs-person" if proposal.needs_person else "ready")
        proposal.branch = target
        store.write_json("last-proposal.json", {**asdict(proposal), "edits": [asdict(e) for e in proposal.edits], "gate": [asdict(g) for g in proposal.gate]})
        _commit(repo_root, f"Docs sync: record the result ({proposal.status})")

        _git(repo_root, "checkout", "-q", original)
        if merge:
            _git(repo_root, "merge", "-q", "--ff-only", target)
            _git(repo_root, "branch", "-q", "-D", branch, check=False)
            if target != branch:  # the value branch is merged; a failed attempt's branch is kept for a person
                _git(repo_root, "branch", "-q", "-D", target, check=False)
            proposal.branch = None
        return proposal
    except Exception:
        _git(repo_root, "checkout", "-q", "-f", original, check=False)
        raise
