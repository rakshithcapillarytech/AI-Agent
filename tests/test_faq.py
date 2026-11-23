from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.rules.faq import faq_view, load_faq

KB = Path(__file__).parent.parent / "knowledge_base"


def test_every_answer_is_backed_by_the_guides():
    """Each piece of evidence must still be in its guide, so an answer can't outlive the guide text."""
    problems = []
    for item in load_faq(KB).items:
        for e in item.evidence:
            path = KB / e.file
            if not path.is_file():
                problems.append(f"{item.id}: no file {e.file}")
            elif e.text not in path.read_text(encoding="utf-8"):
                problems.append(f"{item.id}: {e.file} no longer says {e.text!r}")
    assert not problems, "faq.yaml no longer matches the guides:\n" + "\n".join(problems)


def test_platform_specific_answers_cite_that_platforms_guides():
    """An item for one platform shouldn't be backed only by another platform's file."""
    for item in load_faq(KB).items:
        if not item.platforms:
            continue
        files = {e.file.split("/")[0] for e in item.evidence}
        assert files & ({"_shared"} | set(item.platforms)), (item.id, files)


def test_answers_are_short_and_complete():
    for item in load_faq(KB).items:
        assert item.question.strip().endswith(("?", ".")), item.id
        assert 20 <= len(item.answer) <= 480, (item.id, len(item.answer))
        assert "{{" not in item.answer and "TODO" not in item.answer, item.id


def test_no_secrets_or_invented_values():
    text = " ".join(i.answer for i in load_faq(KB).items)
    for bad in ("ghp_", "AIza", "-----BEGIN", "@capillarytech.com"):
        assert bad not in text, bad


def test_every_category_is_used_and_every_platform_has_answers():
    faq = load_faq(KB)
    assert {c.id for c in faq.categories} == {i.category for i in faq.items}
    for platform in ["android", "ios", "react-native", "flutter", "web"]:
        mine = [i for i in faq.items if not i.platforms or platform in i.platforms]
        assert len(mine) >= 10, (platform, len(mine))


def test_view_lists_sources_not_evidence_text():
    view = faq_view(KB)
    item = next(i for i in view["items"] if i["id"] == "where-account-id")
    assert item["sources"] == ["_shared/push.md"]
    assert "evidence" not in item


def test_http():
    client = TestClient(app)  # no `with`: the database lifespan isn't started
    response = client.get("/faq")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == len(load_faq(KB).items)
    assert {c["id"] for c in data["categories"]} == {"basics", "keys", "push", "problems"}


def test_unknown_category_is_rejected(tmp_path):
    (tmp_path / "faq.yaml").write_text(
        "categories: [{id: a, label: A}]\nitems:\n  - {id: x, category: b, question: \"Q?\", answer: aaaaaaaaaaaaaaaaaaaaa,"
        " evidence: [{file: f, text: t}]}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown categories"):
        load_faq(tmp_path)


def test_the_faq_stays_focused():
    """Only the important questions: a long list is hard to scan."""
    assert len(load_faq(KB).items) <= 25
