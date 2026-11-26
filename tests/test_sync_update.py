"""The automatic update: value-only changes in the online docs flow into the guides; everything else waits for a person."""

import subprocess
from pathlib import Path

import pytest
import yaml

from app.sync.apply import apply_plan, plan_changes
from app.sync.client import Fetched, FetchError
from app.sync.gate import GateResult
from app.sync.impact import changed_pages, store_for
from app.sync.models import SyncConfig, load_config
from app.sync.propose import ProposalError, propose
from app.sync.report import write_report
from app.sync.run import run_sync
from app.sync.status import sync_status
from app.sync.values import Substitution, apply_text, derive, explained, qualifies

BASE = "https://docs.example.test"
INDEX = """# Docs

## Developer
- [SDKs](https://docs.example.test/docs/sdks.md)
  - [Android SDK](https://docs.example.test/docs/android-sdk.md)
    - [Install SDK](https://docs.example.test/docs/installing-sdk.md)
    - [Extra](https://docs.example.test/docs/extra.md)
  - [Web SDK](https://docs.example.test/docs/web-sdk.md)
    - [Web start](https://docs.example.test/docs/web-start.md)
"""


def page(body: str, updated: str = "2026-11-12") -> str:
    return f"---\nupdatedAt: {updated}T09:00:00.000Z\n---\n\n# Page\n\n{body}\n"


class Site:
    def __init__(self, pages: dict[str, str], index: str = INDEX) -> None:
        self.pages, self.index, self.down = dict(pages), index, False

    def get(self, url: str) -> Fetched:
        if self.down:
            raise FetchError("site is down")
        slug = url.rsplit("/", 1)[-1].removesuffix(".md")
        if url.endswith("/llms.txt"):
            return Fetched(200, self.index)
        return Fetched(200, self.pages[slug]) if slug in self.pages else Fetched(404, "")


PAGES = {
    "sdks": page("Overview"),
    "android-sdk": page("Android"),
    "installing-sdk": page("Add `com.example:hydra-core:1.0.0` to Gradle.\nVersion: 1.0.0 (not 11.0.0 or 1.0.01)"),
    "web-sdk": page("Web"),
    "web-start": page("**SDK version:** `1.0.0`"),
    "extra": page("This page also says 1.0.0 but no key fact is anchored to it."),
}
CONFIG = {
    "source": "docs",
    "base_url": BASE,
    "root_title": "SDKs",
    "guides": {"android/direct.md": ["installing-sdk", "extra"], "web/direct.md": ["web-start"]},
    "auto_update": {"roots": ["kb", "evals"], "exclude": ["kb/source", "kb/anchors.yaml", "evals/results"]},
}


# ── the value engine ──────────────────────────────────────────────────────────────────────────────


def test_a_version_change_is_found_and_applied_on_whole_values_only():
    old = page("Use `com.example:hydra-core:1.10.6`, 1.10.60 and 11.10.6.\nVersion `1.10.6`.")
    new = page("Use `com.example:hydra-core:1.10.7`, 1.10.60 and 11.10.6.\nVersion `1.10.7`.", updated="2026-12-01")
    sub = derive(old, new, "com.example:hydra-core:1.10.6")
    assert sub == Substitution("1.10.6", "1.10.7") and qualifies(sub)
    assert apply_text(old, [sub]).count("1.10.7") == 2 and "1.10.60" in apply_text(old, [sub]) and "11.10.6" in apply_text(old, [sub])
    assert explained(old, new, [sub])
    assert not explained(old, new.replace("Version", "Versions"), [sub])  # any other change means a person must look
    assert not explained(old, new, [])


def test_names_and_prose_never_qualify_for_automatic_updates():
    assert not qualifies(Substitution("com.capillary", "com.capillarytech"))  # no digit
    assert not qualifies(Substitution("1", "2"))  # too short to be safe (3 characters minimum)
    assert not qualifies(Substitution("see below", "see above"))
    assert qualifies(Substitution("1.9.22-beta02", "1.10.6"))
    assert derive(page("a"), page("b"), "a") is None and derive(page("x 1.0.0"), page("x 1.0.0"), "1.0.0") is None


def test_a_change_that_is_not_an_in_place_replacement_is_not_derived():
    old = page("Use 1.0.0 now.")
    assert derive(old, page("Use 2.0.0 now.\nand another line"), "1.0.0") is None  # a line was added too


# ── planning and applying ─────────────────────────────────────────────────────────────────────────


def make_repo(tmp_path: Path, extra_anchor: bool = True) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    kb = repo / "kb"
    (kb / "android").mkdir(parents=True)
    (kb / "web").mkdir()
    (kb / "step_summaries").mkdir()
    (repo / "evals" / "deep").mkdir(parents=True)
    (kb / "android" / "direct.md").write_text("---\nsdk_version: 1.0.0\n---\nUse com.example:hydra-core:{{sdk_version}} (1.0.0).\n11.0.0 stays.\n", encoding="utf-8")
    (kb / "web" / "direct.md").write_text("---\nsdk_version: 1.0.0\n---\nWeb 1.0.0\n", encoding="utf-8")
    (kb / "step_summaries" / "android.yaml").write_text('android/direct:\n  "3":\n    do: "Add version 1.0.0."\n', encoding="utf-8")
    (kb / "faq.yaml").write_text(
        "categories: [{id: a, label: A}]\nitems:\n  - id: q\n    category: a\n    question: \"Q?\"\n    answer: Use 1.0.0 everywhere.\n    evidence: [{file: android/direct.md, text: sdk}]\n",
        encoding="utf-8",
    )
    (repo / "evals" / "golden.yaml").write_text("contains: ['1.0.0']\n", encoding="utf-8")
    (repo / "evals" / "deep" / "android-direct.yaml").write_text("contains: ['1.0.0']\n", encoding="utf-8")
    anchors = [{"id": "android-version", "fact": "Android 1.0.0", "page": "installing-sdk", "text": "com.example:hydra-core:1.0.0", "guide_text": "sdk_version: 1.0.0", "used_in": ["android/direct.md"]}]
    if extra_anchor:
        anchors.append({"id": "web-version", "fact": "Web 1.0.0", "page": "web-start", "text": "`1.0.0`", "guide_text": "sdk_version: 1.0.0", "used_in": ["web/direct.md"]})
    (kb / "anchors.yaml").write_text(yaml.safe_dump({"anchors": anchors}, sort_keys=False), encoding="utf-8")
    (kb / "sources.yaml").write_text(yaml.safe_dump(CONFIG), encoding="utf-8")
    (repo / ".gitignore").write_text("kb/source/*/last-run.json\n", encoding="utf-8")  # as in the real repository
    return repo, kb


def baseline(kb: Path, site: Site):
    config = load_config(kb)
    store = store_for(config, kb)
    run_sync(config, store, site)
    manifest = store.load()
    store.accept(manifest)
    store.save(manifest)
    write_report(kb)  # the real repository has committed this report too
    return config, store


def bump(site: Site, slug: str, old: str, new: str, extra: str = "") -> None:
    site.pages[slug] = page(site.pages[slug].split("# Page\n\n", 1)[1].replace(old, new) + extra, updated="2026-12-01")


def test_a_value_bump_everywhere_updates_every_file_that_carries_it(tmp_path):
    repo, kb = make_repo(tmp_path)
    site = Site(PAGES)
    config, store = baseline(kb, site)
    bump(site, "installing-sdk", "1.0.0 (not", "2.0.0 (not")
    site.pages["installing-sdk"] = page("Add `com.example:hydra-core:2.0.0` to Gradle.\nVersion: 2.0.0 (not 11.0.0 or 1.0.01)", "2026-12-01")
    site.pages["web-start"] = page("**SDK version:** `2.0.0`", "2026-12-01")
    run_sync(config, store, site)
    plan = plan_changes(kb, config, store, store.load())
    assert sorted(c.slug for c in plan.eligible) == ["installing-sdk", "web-start"] and plan.needs_person == {}

    edits = {e.path: e.replacements for e in apply_plan(repo, kb, config, plan)}
    assert "sdk_version: 2.0.0" in (kb / "android" / "direct.md").read_text() and "11.0.0 stays" in (kb / "android" / "direct.md").read_text()
    assert "2.0.0" in (kb / "web" / "direct.md").read_text()
    for shared in [kb / "faq.yaml", repo / "evals" / "golden.yaml", kb / "step_summaries" / "android.yaml", repo / "evals" / "deep" / "android-direct.yaml"]:
        assert "2.0.0" in shared.read_text() and "1.0.0" not in shared.read_text(), shared
    anchors = (kb / "anchors.yaml").read_text()
    assert "com.example:hydra-core:2.0.0" in anchors and "1.0.0" not in anchors.replace("11.0.0", "")
    assert {"kb/android/direct.md", "kb/faq.yaml", "kb/anchors.yaml", "evals/golden.yaml"} <= set(edits)


def test_a_value_that_only_one_platform_changed_is_not_applied_to_the_other(tmp_path):
    repo, kb = make_repo(tmp_path)
    site = Site(PAGES)
    config, store = baseline(kb, site)
    site.pages["installing-sdk"] = page("Add `com.example:hydra-core:2.0.0` to Gradle.\nVersion: 2.0.0 (not 11.0.0 or 1.0.01)", "2026-12-01")
    run_sync(config, store, site)  # the web page still says 1.0.0
    plan = plan_changes(kb, config, store, store.load())
    assert [c.slug for c in plan.eligible] == ["installing-sdk"]
    apply_plan(repo, kb, config, plan)
    assert "sdk_version: 2.0.0" in (kb / "android" / "direct.md").read_text()
    assert "sdk_version: 1.0.0" in (kb / "web" / "direct.md").read_text()  # untouched
    assert "1.0.0" in (kb / "faq.yaml").read_text()  # shared files wait for a person: the checks will say so
    assert "2.0.0" in (kb / "step_summaries" / "android.yaml").read_text() and "2.0.0" in (repo / "evals" / "deep" / "android-direct.yaml").read_text()
    anchors = (kb / "anchors.yaml").read_text()
    assert "com.example:hydra-core:2.0.0" in anchors and "`1.0.0`" in anchors  # only the changed fact moved


def test_a_page_without_its_own_key_fact_rides_on_a_value_found_elsewhere(tmp_path):
    _, kb = make_repo(tmp_path)
    site = Site(PAGES)
    config, store = baseline(kb, site)
    all_bumped(site)
    site.pages["extra"] = page("This page also says 2.0.0 but no key fact is anchored to it.", "2026-12-01")
    run_sync(config, store, site)
    plan = plan_changes(kb, config, store, store.load())
    assert sorted(c.slug for c in plan.eligible) == ["extra", "installing-sdk", "web-start"] and plan.needs_person == {}
    # the same, but this page also changed in another way: it must wait for a person
    site.pages["extra"] = page("This page also says 2.0.0 and gained a new rule.", "2026-12-02")
    run_sync(config, store, site)
    plan = plan_changes(kb, config, store, store.load())
    assert list(plan.needs_person) == ["extra"] and sorted(c.slug for c in plan.eligible) == ["installing-sdk", "web-start"]


def test_other_changes_on_the_page_keep_it_for_a_person(tmp_path):
    repo, kb = make_repo(tmp_path)
    site = Site(PAGES)
    config, store = baseline(kb, site)
    site.pages["installing-sdk"] = page("Add `com.example:hydra-core:2.0.0` to Gradle.\nVersion: 2.0.0 (not 11.0.0 or 1.0.01)\nA new step: also do this.", "2026-12-01")
    site.pages["web-start"] = page("**SDK version:** `1.0.0` (a note was added)", "2026-12-01")
    run_sync(config, store, site)
    plan = plan_changes(kb, config, store, store.load())
    assert plan.eligible == [] and set(plan.needs_person) == {"installing-sdk", "web-start"}
    assert all("version-like" in why for why in plan.needs_person.values())
    assert apply_plan(repo, kb, config, plan) == []


# ── the whole flow on a real git repository ───────────────────────────────────────────────────────


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


@pytest.fixture
def repo_with_baseline(tmp_path):
    repo, kb = make_repo(tmp_path)
    site = Site(PAGES)
    baseline(kb, site)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.test")
    git(repo, "config", "user.name", "Test")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "baseline")
    return repo, kb, site


def all_bumped(site: Site) -> None:
    site.pages["installing-sdk"] = page("Add `com.example:hydra-core:2.0.0` to Gradle.\nVersion: 2.0.0 (not 11.0.0 or 1.0.01)", "2026-12-01")
    site.pages["web-start"] = page("**SDK version:** `2.0.0`", "2026-12-01")


ok_gate = lambda root: [GateResult("tests", True, "")]
bad_gate = lambda root: [GateResult("tests", False, "1 failed")]


def test_update_merges_a_value_bump_that_passes_the_checks(repo_with_baseline):
    repo, kb, site = repo_with_baseline
    all_bumped(site)
    result = propose(repo, kb, merge=True, gate_fn=ok_gate, fetcher=site)
    assert result.status == "merged" and result.needs_person == {} and result.branch is None
    assert [a["slug"] for a in result.applied] == ["installing-sdk", "web-start"] and "1.0.0 -> 2.0.0" in result.applied[0]["values"]
    assert "sdk_version: 2.0.0" in (kb / "android" / "direct.md").read_text()
    assert git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip() == "main" and "docs-sync" not in git(repo, "branch")
    assert changed_pages(store_for(load_config(kb), kb).load()) == []  # reviewed: nothing left to look at
    assert sync_status(kb)["changed"] == [] and (kb / "source" / "docs" / "last-proposal.json").is_file()
    assert "update values in the guides" in git(repo, "log", "--format=%s")


def test_the_checks_see_the_final_state_with_the_pages_already_reviewed(repo_with_baseline):
    repo, kb, site = repo_with_baseline
    all_bumped(site)
    seen = {}

    def spy(root):
        seen["flagged"] = [c["slug"] for c in sync_status(kb)["changed"]]
        seen["guide"] = (kb / "android" / "direct.md").read_text()
        return [GateResult("tests", True, "")]

    propose(repo, kb, merge=False, gate_fn=spy, fetcher=site)
    assert seen["flagged"] == [] and "sdk_version: 2.0.0" in seen["guide"]  # what clients would get after the merge


def test_a_failing_check_keeps_the_guides_as_they_were_and_flags_the_pages(repo_with_baseline):
    repo, kb, site = repo_with_baseline
    all_bumped(site)
    result = propose(repo, kb, merge=True, gate_fn=bad_gate, fetcher=site)
    assert result.status == "merged"  # only the snapshot and the warnings; the guides were not touched
    assert result.applied == [] and set(result.needs_person) == {"installing-sdk", "web-start"}
    assert "sdk_version: 1.0.0" in (kb / "android" / "direct.md").read_text()
    assert sorted(c["slug"] for c in sync_status(kb)["changed"]) == ["installing-sdk", "web-start"]  # still flagged
    assert any(b.strip().endswith("-values") for b in git(repo, "branch").splitlines())  # the attempt is kept for a person
    assert git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip() == "main"


def test_without_merge_nothing_reaches_the_current_branch(repo_with_baseline):
    repo, kb, site = repo_with_baseline
    before = git(repo, "rev-parse", "HEAD")
    all_bumped(site)
    result = propose(repo, kb, merge=False, gate_fn=ok_gate, fetcher=site)
    assert result.status == "ready" and result.branch and result.branch.endswith("-values")
    assert git(repo, "rev-parse", "HEAD") == before and "sdk_version: 1.0.0" in (kb / "android" / "direct.md").read_text()
    assert "sdk_version: 2.0.0" in git(repo, "show", f"{result.branch}:kb/android/direct.md")


def test_prose_changes_are_flagged_and_drafted_not_applied(repo_with_baseline):
    repo, kb, site = repo_with_baseline
    all_bumped(site)
    site.pages["web-start"] = page("**SDK version:** `2.0.0`\nA brand new section.", "2026-12-01")
    drafted = []
    result = propose(repo, kb, merge=True, gate_fn=ok_gate, fetcher=site, drafter=lambda k: drafted.append(k))
    assert list(result.needs_person) == ["web-start"] and drafted == [kb]  # a drafter was asked about what a person must handle
    assert "sdk_version: 1.0.0" in (kb / "web" / "direct.md").read_text()  # not auto-applied
    assert [c["slug"] for c in sync_status(kb)["changed"]] == ["web-start"]  # the android page was accepted, this one waits


def test_nothing_changed_and_failures_leave_no_trace(repo_with_baseline):
    repo, kb, site = repo_with_baseline
    result = propose(repo, kb, merge=True, gate_fn=ok_gate, fetcher=site)
    assert result.status == "nothing" and "docs-sync" not in git(repo, "branch")
    site.down = True
    assert propose(repo, kb, gate_fn=ok_gate, fetcher=site).status == "fetch-failed"
    assert "docs-sync" not in git(repo, "branch") and not git(repo, "status", "--porcelain").strip()


def test_it_refuses_to_start_on_uncommitted_work(repo_with_baseline, tmp_path):
    repo, kb, site = repo_with_baseline
    (kb / "faq.yaml").write_text("changed by a person", encoding="utf-8")
    with pytest.raises(ProposalError, match="uncommitted"):
        propose(repo, kb, gate_fn=ok_gate, fetcher=site)
    with pytest.raises(ProposalError, match="not a git repository"):
        propose(tmp_path, kb, gate_fn=ok_gate, fetcher=site)


def test_the_real_checks_run_the_four_gates(monkeypatch, tmp_path):
    from app.sync import gate

    calls = []

    class Done:
        returncode, stdout, stderr = 0, "ok", ""

    monkeypatch.setattr(gate.subprocess, "run", lambda cmd, **kw: calls.append(cmd) or Done())
    results = gate.run_gate(tmp_path)
    assert gate.passed(results) and len(results) == 4 and any("pytest" in c for c in calls[0]) and "check" in calls[3]
    Done.returncode = 1
    assert not gate.passed(gate.run_gate(tmp_path))
    assert not gate.passed([])  # no checks is not a pass


def test_the_default_config_knows_what_may_be_edited():
    cfg = SyncConfig.model_validate({"source": "s", "base_url": "u", "root_title": "r"})
    assert "knowledge_base/anchors.yaml" in cfg.auto_update.exclude and cfg.auto_update.min_value_length == 3
