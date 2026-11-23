"""Every numbered step in every platform guide has a short "what to do" that the guide backs up.

`knowledge_base/step_summaries/<platform>.yaml` holds, per guide and step number, `do` (one or two plain
sentences for a person) and `evidence` (exact text that must appear in that step of the guide).
"""

import re

import pytest

from app.config import get_settings
from app.kb.humanguide import step_summaries, step_text
from app.kb.sections import split_sections

KB = get_settings().knowledge_base_dir
GUIDES = sorted(f"{p}/{m}" for p in ["android", "ios", "react-native", "flutter", "web"] for m in ["direct", "firebase"])
_ID = re.compile(r"^(G?\d+)\.")


def steps_of(rel: str) -> list[str]:
    ids = []
    for s in split_sections((KB / f"{rel}.md").read_text(encoding="utf-8")):
        if len(s.path) == 2 and s.path[0] == "Steps" and (m := _ID.match(s.path[1])):
            ids.append(m.group(1))
    return ids


@pytest.mark.parametrize("rel", GUIDES)
def test_every_step_is_explained_and_backed_by_the_guide(rel):
    summaries = step_summaries(KB).get(rel, {})
    steps = steps_of(rel)
    assert steps, rel
    assert set(summaries) == set(steps), f"{rel}: missing {sorted(set(steps) - set(summaries))}, unknown {sorted(set(summaries) - set(steps))}"
    problems = []
    for step_id in steps:
        entry = summaries[step_id]
        text = step_text(KB, rel, step_id)
        doing = entry.get("do", "")
        if not (30 <= len(doing) <= 300):
            problems.append(f"{rel} step {step_id}: 'do' is {len(doing)} characters (want 30 to 300)")
        if not doing.rstrip().endswith((".", ")", "`")):
            problems.append(f"{rel} step {step_id}: 'do' should end like a sentence")
        if "{{" in doing or "_shared/" in doing or ".md" in doing or "TODO" in doing:
            problems.append(f"{rel} step {step_id}: 'do' has a placeholder, file path or TODO")
        if not entry.get("evidence"):
            problems.append(f"{rel} step {step_id}: no evidence")
        for ev in entry.get("evidence", []):
            if ev not in text:
                problems.append(f"{rel} step {step_id}: the guide's step doesn't contain {ev!r}")
    assert not problems, "\n".join(problems)
