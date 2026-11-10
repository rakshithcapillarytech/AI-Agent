from pathlib import Path

from app.config import get_settings
from app.kb.search import search, tokens
from app.kb.sections import split_sections
from app.kb.steps import steps_for_files

KB = get_settings().knowledge_base_dir


def top(query: str, **kwargs):
    hits = search(KB, query, **kwargs)
    return hits[0].doc.citation if hits else None


def test_error_string_finds_the_known_issue():
    assert top("Could not resolve com.capillary:hydra-core 401", files=["android/direct.md"]) == (
        "android/direct.md › Known Issues"
    )


def test_camel_case_identifiers_match_their_parts():
    assert {"set", "cap", "token", "setcaptoken"} <= set(tokens("setCapToken"))
    assert "Capillary token" in (top("setCapToken", files=["android/direct.md"]) or "")


def test_search_is_limited_to_the_given_files():
    hits = search(KB, "push notification", files=["android/direct.md"])
    assert {h.doc.file for h in hits} <= {"android/direct.md"}


def test_nonsense_finds_nothing():
    assert search(KB, "zzqx wvvk") == []
    assert search(KB, "the of and") == []


def test_headings_in_code_fences_are_not_sections():
    text = "# Title\n## Steps\n### 1. Do it\n```bash\n# a comment, not a heading\n```\nafter\n"
    sections = split_sections(text)
    assert [s.path for s in sections] == [("Steps",), ("Steps", "1. Do it")]
    assert "# a comment" in sections[1].body and "after" in sections[1].body


def test_steps_come_from_the_steps_section_in_order():
    steps = steps_for_files(["_shared/overview.md", "android/direct.md", "ios/missing.md"], KB)
    assert steps[0] == "android/direct.md › 1. Store GitHub credentials locally"
    assert len(steps) == 9 and all(s.startswith("android/direct.md › ") for s in steps)


def make_kb(tmp_path: Path, status: str) -> Path:
    (tmp_path / "issues").mkdir()
    (tmp_path / "issues" / "android-gradle-401.md").write_text(
        f"---\nplatform: android\nconfig_mode: direct\nstatus: {status}\n"
        "error_signature: Gradle 401 from maven.pkg.github.com\n"
        "root_cause: PAT lacks read:packages\nfix: create a new PAT with read:packages\n---\nSeen twice.\n"
    )
    (tmp_path / "android").mkdir()
    (tmp_path / "android" / "direct.md").write_text("---\nplatform: android\n---\n# A\n## Steps\n### 1. x\nbody text\n")
    return tmp_path


def test_only_approved_issues_are_searchable_and_rank_first(tmp_path):
    approved = make_kb(_dir(tmp_path, "a"), "approved")
    hits = search(approved, "gradle 401 read:packages", apps={("android", "direct")})
    assert hits and hits[0].doc.is_issue

    draft = make_kb(_dir(tmp_path, "b"), "draft")
    assert search(draft, "gradle 401 read:packages", issues_only=True) == []


def test_issues_for_other_apps_are_hidden(tmp_path):
    kb = make_kb(_dir(tmp_path, "c"), "approved")  # the index is cached per directory
    assert search(kb, "gradle 401", apps={("ios", "direct")}, issues_only=True) == []
    assert search(kb, "gradle 401", apps={("android", "firebase")}, issues_only=True) == []
    assert search(kb, "gradle 401", apps={("android", "direct")}, issues_only=True)


def _dir(tmp_path: Path, name: str) -> Path:
    (tmp_path / name).mkdir()
    return tmp_path / name
