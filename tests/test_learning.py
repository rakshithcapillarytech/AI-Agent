"""The learning loop: resolved threads → drafts → admin approval → searchable knowledge."""

import shutil

import frontmatter
import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.api import main
from app.config import get_settings
from app.escalation.store import InMemoryEscalationStore
from app.graph.builder import build_graph
from app.kb.search import search
from app.learning.issues import issue_filename, lint_issue, publish_issue, render_issue
from app.learning.store import DOC_GAP, ISSUE_DRAFT, InMemoryLearningStore
from tests.test_escalation import PROFILE
from tests.test_graph_smoke import ScriptedModel

DRAFT = {
    "error_signature": "Gradle 401 from maven.pkg.github.com",
    "root_cause": "The PAT is fine-grained instead of classic.",
    "fix": "Create a classic PAT with read:packages.",
    "platform": "android",
    "config_mode": "direct",
}


@pytest.fixture
def kb(tmp_path):
    (tmp_path / "android").mkdir()
    (tmp_path / "android" / "direct.md").write_text("---\nplatform: android\nsdk_version: 1.2.3\n---\n# A\n## Steps\n### 1. x\nbody\n")
    (tmp_path / "CHANGELOG.md").write_text("# Knowledge base changelog\n\n## Earlier\n- something\n")
    return tmp_path


def test_lint_accepts_a_good_draft_and_rejects_bad_ones(kb):
    assert lint_issue(DRAFT, kb) == []
    assert "fix is required." in lint_issue({**DRAFT, "fix": " "}, kb)
    assert any("secret" in e for e in lint_issue({**DRAFT, "fix": "use ghp_abcdefghijklmnopqrstuvwxyz0123"}, kb))
    assert any("email" in e for e in lint_issue({**DRAFT, "root_cause": "ask jane@acme.com"}, kb))
    assert any("platform must be" in e for e in lint_issue({**DRAFT, "platform": None}, kb))
    assert any("no knowledge file" in e for e in lint_issue({**DRAFT, "config_mode": "firebase"}, kb))
    assert any("longer than" in e for e in lint_issue({**DRAFT, "fix": "x" * 2000}, kb))


def test_publish_writes_an_approved_file_that_search_finds_first(kb):
    path = publish_issue(DRAFT, kb, "session-1")
    assert path.name == issue_filename(DRAFT) == "android-gradle-401-from-maven-pkg-github-com.md"
    meta = frontmatter.load(path).metadata
    assert meta["status"] == "approved" and meta["sdk_version"] == "1.2.3" and meta["source_session"] == "session-1"
    assert "issues/" + path.name in (kb / "CHANGELOG.md").read_text()
    assert (kb / "CHANGELOG.md").read_text().count("## Learned issues") == 1

    hits = search(kb, "gradle 401 maven.pkg.github.com", apps={("android", "direct")})
    assert hits[0].doc.is_issue and "classic PAT" in hits[0].doc.text
    assert search(kb, "gradle 401", apps={("ios", "direct")}, issues_only=True) == []
    assert lint_issue(DRAFT, kb) == ["An issue with this platform and error text already exists."]


def test_both_modes_issue_has_no_config_mode_or_version(kb):
    text = render_issue({**DRAFT, "config_mode": ""}, kb, "s")
    meta = frontmatter.loads(text).metadata
    assert "config_mode" not in meta and "sdk_version" not in meta


async def test_store_is_idempotent_per_item():
    store = InMemoryLearningStore()
    assert await store.add_if_absent(ISSUE_DRAFT, "s1", DRAFT)
    assert await store.add_if_absent(ISSUE_DRAFT, "s1", DRAFT) is None
    assert await store.add_if_absent(ISSUE_DRAFT, "s2", DRAFT)  # same text, another session
    assert len(await store.list(ISSUE_DRAFT, "pending")) == 2


@pytest.fixture
def client_kb(tmp_path):
    """A throwaway copy of the real knowledge base, so approving an issue writes nowhere that matters."""
    copy = tmp_path / "kb"
    shutil.copytree(get_settings().knowledge_base_dir, copy, ignore=shutil.ignore_patterns("source"))
    return copy


@pytest.fixture
def client(client_kb, monkeypatch):
    resolve = {"error_signature": DRAFT["error_signature"], "root_cause": DRAFT["root_cause"], "fix": DRAFT["fix"]}
    model = ScriptedModel(
        disable_streaming=True,
        messages=iter(
            [
                AIMessage(content="", tool_calls=[{"name": "resolve_issue", "args": resolve, "id": "t1"}]),
                AIMessage(content="", tool_calls=[{"name": "report_doc_gap", "args": {"question": "iOS push setup"}, "id": "t2"}]),
                AIMessage(content="Glad that worked."),
            ]
        ),
    )
    main.app.state.graph = build_graph(checkpointer=InMemorySaver(), model=model)
    main.app.state.escalations = InMemoryEscalationStore()
    main.app.state.learning = InMemoryLearningStore()
    monkeypatch.setattr(get_settings(), "knowledge_base_dir", client_kb)
    return TestClient(main.app)


def test_resolved_thread_becomes_a_draft_and_approval_publishes_it(client, client_kb):
    assert client.post("/sessions/s1/start", json={"profile": PROFILE}).status_code == 200

    (draft,) = client.get("/admin/issue-drafts").json()
    assert draft["payload"]["error_signature"] == DRAFT["error_signature"]
    assert (draft["payload"]["platform"], draft["payload"]["config_mode"]) == ("android", "direct")
    (gap,) = client.get("/admin/doc-gaps").json()
    assert gap["question"] == "iOS push setup" and gap["count"] == 1 and gap["sessions"] == 1

    # A failing gate returns the reasons and publishes nothing.
    bad = client.post(f"/admin/issue-drafts/{draft['id']}/approve", json={"platform": "windows"})
    assert bad.status_code == 422 and any("platform must be" in e for e in bad.json()["detail"])
    assert len(client.get("/admin/issue-drafts").json()) == 1
    approved = client.post(f"/admin/issue-drafts/{draft['id']}/approve", json={"fix": "Use a classic PAT with read:packages."})
    assert approved.status_code == 200, approved.text
    assert (client_kb / approved.json()["file"]).is_file()
    assert client.get("/admin/issue-drafts").json() == []
    assert client.post(f"/admin/issue-drafts/{draft['id']}/approve", json={}).status_code == 409

    # Gaps can be marked handled.
    assert client.post("/admin/doc-gaps/handle", json={"ids": gap["ids"]}).status_code == 200
    assert client.get("/admin/doc-gaps").json() == []


def test_rejecting_a_draft_publishes_nothing(client, client_kb):
    client.post("/sessions/s2/start", json={"profile": PROFILE})
    (draft,) = client.get("/admin/issue-drafts").json()
    assert client.post(f"/admin/issue-drafts/{draft['id']}/reject").status_code == 200
    assert not list((client_kb / "issues").glob("*.md"))
    assert client.post(f"/admin/issue-drafts/{draft['id']}/reject").status_code == 409


def test_syncing_twice_does_not_duplicate(client):
    client.post("/sessions/s3/start", json={"profile": PROFILE})
    import asyncio

    asyncio.run(main._sync_learning("s3"))
    assert len(client.get("/admin/issue-drafts").json()) == 1


def test_gaps_group_by_question_across_sessions():
    store = InMemoryLearningStore()
    main.app.state.learning = store
    import asyncio

    async def seed():
        await store.add_if_absent(DOC_GAP, "a", {"question": "iOS push setup", "step": None})
        await store.add_if_absent(DOC_GAP, "b", {"question": "ios  Push setup", "step": None})
        await store.add_if_absent(DOC_GAP, "a", {"question": "Min Android version", "step": None})

    asyncio.run(seed())
    groups = TestClient(main.app).get("/admin/doc-gaps").json()
    assert [(g["count"], g["sessions"]) for g in groups] == [(2, 2), (1, 1)]
