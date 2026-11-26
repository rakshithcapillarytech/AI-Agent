import json
import shutil
from datetime import UTC, datetime

import httpx
import pytest
import yaml
from fastapi.testclient import TestClient

from app.api import main as api
from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.kb.guide import build_guide
from app.sync.anchors import check_anchors, failing
from app.sync.client import Fetched, FetchError, HttpFetcher
from app.sync.diff import page_diff
from app.sync.index import branch, linked_slugs, slug_of, updated_at
from app.sync.models import FetchConfig, SyncConfig, load_config
from app.sync.report import build_report
from app.sync.run import run_sync
from app.sync.service import run_and_report
from app.sync.status import source_notice, sync_status
from app.sync.store import SnapshotStore

REAL_KB = get_settings().knowledge_base_dir
BASE = "https://docs.example.test"

INDEX = """# Docs

## Getting started
- [Intro](https://docs.example.test/docs/intro.md)

## Developer
- [SDKs](https://docs.example.test/docs/sdks.md)
  - [Android SDK](https://docs.example.test/docs/android-sdk.md)
    - [Install SDK](https://docs.example.test/docs/installing-sdk.md): How to install.
    - [Initialise SDK](https://docs.example.test/docs/sdk-initialisation.md)
  - [Web SDK](https://docs.example.test/docs/web-sdk.md)
- [Other things](https://docs.example.test/docs/other.md)
"""


def page(title: str, body: str = "", updated: str = "2026-11-12") -> str:
    return f"---\nupdatedAt: {updated}T09:00:00.000Z\n---\n\n# {title}\n\n{body}\n"


class FakeSite:
    """Stands in for the docs website: url -> (status, text). Records every request."""

    def __init__(self, pages: dict[str, str], index: str = INDEX) -> None:
        self.index = index
        self.pages = dict(pages)
        self.requests: list[str] = []
        self.broken: dict[str, str] = {}

    def get(self, url: str) -> Fetched:
        self.requests.append(url)
        slug = url.rsplit("/", 1)[-1].removesuffix(".md")
        if slug in self.broken:
            raise FetchError(self.broken[slug])
        if url.endswith("/llms.txt"):
            return Fetched(200, self.index)
        if slug in self.pages:
            return Fetched(200, self.pages[slug])
        return Fetched(404, "")


def config(**overrides) -> SyncConfig:
    base = {
        "source": "test-docs",
        "base_url": BASE,
        "root_title": "SDKs",
        "follow": {"slug_patterns": ["in-app"], "max_extra_pages": 3},
        "guides": {"android/direct.md": ["installing-sdk", "sdk-initialisation"], "web/direct.md": ["web-sdk"]},
    }
    return SyncConfig.model_validate({**base, **overrides})


PAGES = {
    "sdks": page("SDKs", "See [in-app](https://docs.example.test/docs/in-app-messaging) and [other](/docs/other)."),
    "android-sdk": page("Android SDK"),
    "installing-sdk": page("Install", "Use com.example:hydra-core:1.0.0"),
    "sdk-initialisation": page("Init"),
    "web-sdk": page("Web"),
    "in-app-messaging": page("In-app", "hidden from the index"),
}


@pytest.fixture
def store(tmp_path):
    return SnapshotStore(tmp_path, "test-docs", BASE)


# ── reading the site ──────────────────────────────────────────────────────────────────────────────


def test_the_index_branch_keeps_depth_and_parents():
    entries = branch(INDEX, "SDKs")
    assert [e.slug for e in entries] == ["sdks", "android-sdk", "installing-sdk", "sdk-initialisation", "web-sdk"]
    by = {e.slug: e for e in entries}
    assert by["sdks"].parent is None and by["android-sdk"].parent == "sdks"
    assert by["installing-sdk"].parent == "android-sdk" and by["installing-sdk"].depth == 2
    assert "other" not in by and "intro" not in by  # outside the branch
    assert branch(INDEX, "Nope") == []


def test_links_and_dates():
    text = page("T", "[a](https://docs.example.test/docs/foo-bar#x) [b](/docs/baz.md) [c](https://elsewhere.test/x)")
    assert linked_slugs(text) == {"foo-bar", "baz"}
    assert updated_at(text) == "2026-11-12T09:00:00.000Z"
    assert updated_at("no front matter") is None
    assert slug_of("https://docs.example.test/docs/installing-sdk") == "installing-sdk"


# ── polite fetching ───────────────────────────────────────────────────────────────────────────────


def fetcher_for(handler, retries: int = 2):
    sleeps: list[float] = []
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return HttpFetcher(FetchConfig(delay_seconds=0, max_retries=retries), client=client, sleep=sleeps.append), sleeps


def test_rate_limits_are_retried_with_the_servers_wait():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(429, headers={"retry-after": "7"}) if len(calls) < 3 else httpx.Response(200, text="ok")

    fetcher, sleeps = fetcher_for(handler)
    assert fetcher.get(BASE + "/x").text == "ok" and len(calls) == 3
    assert sleeps == [7.0, 7.0]


def test_a_page_that_keeps_failing_raises_and_a_404_does_not():
    fetcher, _ = fetcher_for(lambda r: httpx.Response(503), retries=1)
    with pytest.raises(FetchError, match="503"):
        fetcher.get(BASE + "/x")
    fetcher, _ = fetcher_for(lambda r: httpx.Response(404, text="nope"))
    assert fetcher.get(BASE + "/x").status == 404


def test_network_errors_become_fetch_errors():
    def handler(request):
        raise httpx.ConnectError("down")

    fetcher, _ = fetcher_for(handler, retries=1)
    with pytest.raises(FetchError, match="ConnectError"):
        fetcher.get(BASE + "/x")


# ── a sync run ────────────────────────────────────────────────────────────────────────────────────


def test_first_run_mirrors_the_branch_and_finds_hidden_pages(store):
    site = FakeSite(PAGES)
    result = run_sync(config(), store, site)
    manifest = store.load()
    assert sorted(manifest.pages) == ["android-sdk", "in-app-messaging", "installing-sdk", "sdk-initialisation", "sdks", "web-sdk"]
    assert manifest.pages["in-app-messaging"].found_via == "link:sdks"  # the index leaves it out; a page links to it
    assert "other" not in manifest.pages  # linked, but its name doesn't match a follow pattern
    assert sorted(result.added) == sorted(manifest.pages) and result.followed == ["in-app-messaging"]
    assert result.ok and all(store.read_page(s) for s in manifest.pages)
    assert manifest.pages["installing-sdk"].updated_at == "2026-11-12T09:00:00.000Z"
    assert all(p.reviewed_sha256 is None for p in manifest.pages.values())  # a run never marks pages as reviewed


def test_second_run_finds_nothing_new_and_a_change_is_detected(store):
    site = FakeSite(PAGES)
    run_sync(config(), store, site)
    first = store.load()
    again = run_sync(config(), store, site)
    assert again.unchanged == 6 and not again.changed and not again.added
    site.pages["installing-sdk"] = page("Install", "Use com.example:hydra-core:2.0.0", updated="2026-12-01")
    third = run_sync(config(), store, site)
    assert third.changed == ["installing-sdk"]
    now = store.load().pages["installing-sdk"]
    assert now.sha256 != first.pages["installing-sdk"].sha256 and now.updated_at.startswith("2026-12-01")
    assert "2.0.0" in store.read_page("installing-sdk")


def test_review_baseline_keeps_the_reviewed_copy_for_diffing(store):
    site = FakeSite(PAGES)
    run_sync(config(), store, site)
    manifest = store.load()
    store.accept(manifest)
    store.save(manifest)
    assert not any(p.changed_since_review for p in store.load().pages.values())

    site.pages["installing-sdk"] = page("Install", "Use com.example:hydra-core:2.0.0", updated="2026-12-01")
    run_sync(config(), store, site)
    record = store.load().pages["installing-sdk"]
    assert record.changed_since_review and record.reviewed_updated_at.startswith("2026-11-12")
    assert "1.0.0" in store.read_reviewed("installing-sdk")  # the version a person reviewed is kept
    diff = "\n".join(page_diff(store, "installing-sdk"))
    assert "-Use com.example:hydra-core:1.0.0" in diff and "+Use com.example:hydra-core:2.0.0" in diff

    # a second change before anyone reviewed keeps diffing against the REVIEWED version, not the one in between
    site.pages["installing-sdk"] = page("Install", "Use com.example:hydra-core:3.0.0", updated="2026-12-05")
    run_sync(config(), store, site)
    assert "1.0.0" in store.read_reviewed("installing-sdk")

    manifest = store.load()
    assert store.accept(manifest, ["installing-sdk"]) == ["installing-sdk"]
    store.save(manifest)
    assert store.read_reviewed("installing-sdk") is None and not store.load().pages["installing-sdk"].changed_since_review


def test_a_failing_page_keeps_its_old_snapshot(store):
    site = FakeSite(PAGES)
    run_sync(config(), store, site)
    site.pages["installing-sdk"] = page("Install", "changed")
    site.broken["installing-sdk"] = "HTTP 429 after 5 tries"
    site.pages["web-sdk"] = "<html>not markdown</html>"
    result = run_sync(config(), store, site)
    assert result.failed == {"installing-sdk": "HTTP 429 after 5 tries", "web-sdk": "not a Markdown page"}
    assert not result.ok and "1.0.0" in store.read_page("installing-sdk")


def test_if_the_index_is_unreadable_nothing_changes(store):
    run_sync(config(), store, FakeSite(PAGES))
    before = store.manifest_path.read_text()
    result = run_sync(config(), store, FakeSite(PAGES, index="# Docs\n\n- [Intro](https://docs.example.test/docs/intro.md)\n"))
    assert not result.index_ok and "(index)" in result.failed
    assert store.manifest_path.read_text() == before


def test_pages_that_disappear_are_flagged_not_deleted(store):
    site = FakeSite(PAGES)
    run_sync(config(), store, site)
    site.index = INDEX.replace("  - [Web SDK](https://docs.example.test/docs/web-sdk.md)\n", "")
    result = run_sync(config(), store, site)
    assert result.removed == ["web-sdk"]
    manifest = store.load()
    assert manifest.pages["web-sdk"].removed and store.read_page("web-sdk")  # still on disk for diffing
    assert not manifest.pages["web-sdk"].changed_since_review


def test_following_links_is_capped(store):
    links = " ".join(f"[x](/docs/in-app-{i})" for i in range(10))
    site = FakeSite({**PAGES, "sdks": page("SDKs", links), **{f"in-app-{i}": page(f"I{i}") for i in range(10)}})
    result = run_sync(config(), store, site)
    assert len(result.followed) == 3 and len([p for p in store.load().pages if p.startswith("in-app-")]) == 3


# ── reviewer-facing pieces on a small kb ──────────────────────────────────────────────────────────


@pytest.fixture
def small_kb(tmp_path):
    kb = tmp_path / "kb"
    (kb / "android").mkdir(parents=True)
    (kb / "android" / "direct.md").write_text("sdk_version: 1.0.0\nuse com.example:hydra-core\n", encoding="utf-8")
    (kb / "sources.yaml").write_text(yaml.safe_dump(config().model_dump(mode="json")), encoding="utf-8")
    (kb / "anchors.yaml").write_text(
        yaml.safe_dump(
            {
                "anchors": [
                    {"id": "group", "fact": "Maven group", "page": "installing-sdk", "text": "com.example:hydra-core", "used_in": ["android/direct.md"]},
                    {"id": "version", "fact": "SDK version", "page": "installing-sdk", "text": "1.0.0", "guide_text": "sdk_version: 1.0.0", "used_in": ["android/direct.md"]},
                ]
            }
        ),
        encoding="utf-8",
    )
    (kb / "faq.yaml").write_text(
        "categories: [{id: a, label: A}]\nitems:\n  - id: q\n    category: a\n    question: \"Q?\"\n    answer: aaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "    evidence: [{file: android/direct.md, text: sdk}]\n",
        encoding="utf-8",
    )
    return kb


def test_anchors_catch_a_fact_that_changed_online_or_drifted_in_a_guide(small_kb):
    site = FakeSite(PAGES)
    cfg = load_config(small_kb)
    store = SnapshotStore(small_kb, cfg.source, cfg.base_url)
    run_sync(cfg, store, site)
    assert failing(check_anchors(small_kb, store)) == []

    site.pages["installing-sdk"] = page("Install", "Use com.example:hydra-core:2.0.0")
    run_sync(cfg, store, site)
    bad = {r.anchor.id: r for r in failing(check_anchors(small_kb, store))}
    assert list(bad) == ["version"] and bad["version"].online is False  # "1.0.0" is gone from the page

    (small_kb / "android" / "direct.md").write_text("nothing here", encoding="utf-8")
    bad = {r.anchor.id: r for r in failing(check_anchors(small_kb, store))}
    assert set(bad) == {"group", "version"} and bad["group"].online is True and not bad["group"].guides["android/direct.md"]


def test_status_report_and_notice_describe_what_needs_review(small_kb):
    site = FakeSite(PAGES)
    cfg = load_config(small_kb)
    store = SnapshotStore(small_kb, cfg.source, cfg.base_url)
    assert sync_status(small_kb)["synced"] is False and source_notice(small_kb, ["android/direct.md"]) == []
    run_and_report(small_kb, fetcher=site)
    manifest = store.load()
    store.accept(manifest)
    store.save(manifest)
    status = sync_status(small_kb)
    assert status["synced"] and status["changed"] == [] and status["anchors"]["total"] == 2
    assert source_notice(small_kb, ["android/direct.md"])[0].startswith("Checked against Capillary's online developer docs on ")

    site.pages["installing-sdk"] = page("Install", "Use com.example:hydra-core:2.0.0", updated="2026-12-01")
    run_and_report(small_kb, fetcher=site)
    status = sync_status(small_kb)
    assert [c["slug"] for c in status["changed"]] == ["installing-sdk"] and status["changed"][0]["has_diff"]
    assert status["stale_guides"] == {"android/direct.md": ["installing-sdk"]}
    assert [a["id"] for a in status["anchors"]["failing"]] == ["version"]
    warning = source_notice(small_kb, ["android/direct.md"])
    assert "`installing-sdk`" in warning[1] and source_notice(small_kb, ["web/direct.md"])[1:] == []  # only the guides built from it

    text = build_report(small_kb)
    for part in ["## Changed pages", "installing-sdk", "+Use com.example:hydra-core:2.0.0", "## Key facts that no longer match", "android/direct.md", "faq"]:
        assert part in text.replace("FAQ items q", "faq")
    assert (store.root / "CHANGES.md").is_file()


def test_a_missing_or_broken_snapshot_never_breaks_a_guide(tmp_path):
    assert source_notice(tmp_path, ["android/direct.md"]) == []
    (tmp_path / "sources.yaml").write_text("not: [valid", encoding="utf-8")
    assert source_notice(tmp_path, ["android/direct.md"]) == [] and sync_status(tmp_path)["synced"] is False


# ── the real repo: the committed snapshot, anchors and guides agree ───────────────────────────────


def test_the_committed_snapshot_backs_the_guides():
    cfg = load_config(REAL_KB)
    store = SnapshotStore(REAL_KB, cfg.source, cfg.base_url)
    manifest = store.load()
    assert len(manifest.pages) >= 59 and manifest.synced_at
    mapped = {s for slugs in cfg.guides.values() for s in slugs}
    assert not mapped - set(manifest.pages), f"sources.yaml names pages that aren't mirrored: {sorted(mapped - set(manifest.pages))}"
    for guide in cfg.guides:
        assert (REAL_KB / guide).is_file(), guide
    for rel in [f"{p}/{m}.md" for p in ["android", "ios", "react-native", "flutter", "web"] for m in ["direct", "firebase"]]:
        assert rel in cfg.guides, f"{rel} has no source pages in sources.yaml"
    assert all(store.read_page(slug) for slug in manifest.pages)


def test_every_key_fact_is_still_on_the_page_and_in_the_guides():
    cfg = load_config(REAL_KB)
    results = check_anchors(REAL_KB, SnapshotStore(REAL_KB, cfg.source, cfg.base_url))
    assert len(results) >= 40
    bad = [f"{r.anchor.id} ({'page' if r.online is not True else ', '.join(g for g, ok in r.guides.items() if not ok)})" for r in failing(results)]
    assert not bad, "Key facts out of step: " + "; ".join(bad)


def test_every_anchor_names_a_mirrored_page_and_existing_guides():
    cfg = load_config(REAL_KB)
    manifest = SnapshotStore(REAL_KB, cfg.source, cfg.base_url).load()
    from app.sync.anchors import load_anchors

    for anchor in load_anchors(REAL_KB):
        assert anchor.page in manifest.pages, anchor.id
        assert all((REAL_KB / g).is_file() for g in anchor.used_in), anchor.id


# ── the kit carries the freshness line ────────────────────────────────────────────────────────────


def profile(platform="android", mode="direct"):
    return IntegrationProfile.model_validate(
        {
            "company": "Demo",
            "platforms": [{"platform": platform, "config_mode": mode}],
            "modules": ["core"],
            "environment": "uat",
            "region": "IN",
            "customer_id_type": "mobile",
        }
    )


def test_the_guide_says_when_it_was_checked_and_warns_about_changed_pages(tmp_path):
    kb = tmp_path / "kb"
    shutil.copytree(REAL_KB, kb, ignore=shutil.ignore_patterns("audits"))
    guide = build_guide(profile(), kb)
    assert "Checked against Capillary's online developer docs on" in guide and "changed after this guide was last reviewed" not in guide

    manifest_path = kb / "source" / "capillary-docs" / "manifest.json"
    data = json.loads(manifest_path.read_text())
    data["pages"]["xiaomi-push-notification"]["sha256"] = "0" * 64  # as if the page changed online after review
    manifest_path.write_text(json.dumps(data))
    android = build_guide(profile(), kb)
    assert "These online pages changed after this guide was last reviewed" in android and "`xiaomi-push-notification`" in android
    assert "changed after this guide was last reviewed" not in build_guide(profile("web", "direct"), kb)  # an Android-only page

    data["pages"]["installing-sdk"]["sha256"] = "0" * 64  # also used by the shared prerequisites guide, so every kit says so
    manifest_path.write_text(json.dumps(data))
    assert "`installing-sdk`" in build_guide(profile("web", "direct"), kb)


# ── API ───────────────────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def client(tmp_path, monkeypatch):
    kb = tmp_path / "kb"
    shutil.copytree(REAL_KB, kb, ignore=shutil.ignore_patterns("audits"))
    settings = get_settings().model_copy(update={"knowledge_base_dir": kb})
    monkeypatch.setattr(api, "get_settings", lambda: settings)
    return TestClient(api.app), kb  # no `with`: the database lifespan isn't started


def test_public_status_is_small_and_safe(client):
    http, _ = client
    data = http.get("/sources/status").json()
    assert data["synced"] is True and data["pages_to_review"] == 0 and data["facts_failing"] == 0
    assert set(data) == {"synced", "synced_at", "pages", "source", "base_url", "pages_to_review", "facts_failing"}


def test_admin_lists_changes_with_diffs_and_accepts_them(client, monkeypatch):
    http, kb = client
    cfg = load_config(kb)
    store = SnapshotStore(kb, cfg.source, cfg.base_url)
    # simulate "a page changed after review": keep the reviewed text, change the current page and its hash
    manifest = store.load()
    slug = "installing-sdk"
    original = store.read_page(slug)
    (store.reviewed_dir).mkdir(parents=True, exist_ok=True)
    (store.reviewed_dir / f"{slug}.md").write_text(original, encoding="utf-8")
    changed = original.replace("1.10.6", "1.10.7", 1)
    store.page_path(slug).write_text(changed, encoding="utf-8")
    manifest.pages[slug].sha256 = "f" * 64
    store.save(manifest)

    data = http.get("/admin/sources").json()
    assert [p["slug"] for p in data["changed"]] == [slug]
    assert any(line.startswith("+") and "1.10.7" in line for line in data["changed"][0]["diff"])
    assert "android/direct.md" in data["changed"][0]["guides"]
    assert http.get("/sources/status").json()["pages_to_review"] == 1

    assert http.post("/admin/sources/accept", json={}).status_code == 422
    assert http.post("/admin/sources/accept", json={"slugs": [slug]}).json() == {"accepted": [slug]}
    assert http.get("/sources/status").json()["pages_to_review"] == 0 and store.read_reviewed(slug) is None


def test_admin_sync_runs_in_the_background_and_refuses_overlap(client, monkeypatch):
    http, _ = client

    class Result:
        ok, changed, added, failed = True, ["a"], [], {}

    async def fake_run(_kb):
        return Result()

    monkeypatch.setattr(api, "run_in_background", fake_run)
    assert http.post("/admin/sources/sync").json() == {"ok": True, "changed": ["a"], "added": [], "failed": {}}

    async def busy(_kb):
        return None

    monkeypatch.setattr(api, "run_in_background", busy)
    assert http.post("/admin/sources/sync").status_code == 409


def test_a_sync_can_run_from_a_script_end_to_end(tmp_path):
    """run_and_report builds a snapshot and a report from scratch, with no network."""
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "sources.yaml").write_text(yaml.safe_dump(config().model_dump(mode="json")), encoding="utf-8")
    result = run_and_report(kb, fetcher=FakeSite(PAGES))
    assert result.ok and (kb / "source" / "test-docs" / "CHANGES.md").read_text().startswith("# Online docs")
    assert datetime.now(UTC) >= result.started_at


# ── optional AI drafts ────────────────────────────────────────────────────────────────────────────


def test_ai_drafts_are_suggestions_only_and_skipped_when_nothing_changed(small_kb):
    from langchain_core.language_models.fake_chat_models import FakeListChatModel

    from app.sync.draft import draft_proposals

    site = FakeSite(PAGES)
    cfg = load_config(small_kb)
    store = SnapshotStore(small_kb, cfg.source, cfg.base_url)
    run_sync(cfg, store, site)
    manifest = store.load()
    store.accept(manifest)
    store.save(manifest)
    model = FakeListChatModel(responses=["- **android/direct.md > Steps**: change to `2.0.0`"])
    assert draft_proposals(small_kb, model) is None  # nothing changed, no model call, no file

    site.pages["installing-sdk"] = page("Install", "Use com.example:hydra-core:2.0.0", updated="2026-12-01")
    run_sync(cfg, store, site)
    guide_before = (small_kb / "android" / "direct.md").read_text()
    path = draft_proposals(small_kb, model)
    text = path.read_text()
    assert path.name == "DRAFT.md" and "AI draft, unreviewed" in text and "installing-sdk" in text and "change to `2.0.0`" in text
    assert (small_kb / "android" / "direct.md").read_text() == guide_before  # drafts never edit a guide
