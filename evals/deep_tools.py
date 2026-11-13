"""Deep evaluation harness: blind answering by an AI assistant that only sees the generated kit.

    uv run python -m evals.deep_tools prepare   # kits + question-only files for the answering assistants
    uv run python -m evals.deep_tools grade     # check answers: required/forbidden strings; write judge tasks
    uv run python -m evals.deep_tools score     # merge judge verdicts and print the score

Work files live in evals/results/deep/ (git-ignored):
    kits/<name>.md            the kit an answering assistant gets (every module)
    questions/<name>.json     [{"id", "question"}]; no answer keys
    answers/<name>.json       {"<id>": "<answer>"}, written by the answering assistant
    judge/<name>.json         [{"id", "question", "answer", "checks": ["…"]}] for the grader
    verdicts/<name>.json      {"<id>": ["yes"|"no", …]}, written by the grader, one per check
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.kb.guide import build_guide

EVALS = Path(__file__).parent
DEEP = EVALS / "deep"
WORK = EVALS / "results" / "deep"
ALL_MODULES = ["core", "push", "inapp", "inbox_api", "inbox_ui", "visitor", "gamification", "multi_account"]


def load(name: str) -> list[dict]:
    return yaml.safe_load((DEEP / f"{name}.yaml").read_text(encoding="utf-8")) or []


def names() -> list[str]:
    return sorted(p.stem for p in DEEP.glob("*.yaml"))


def folder(sub: str) -> Path:
    path = WORK / sub
    path.mkdir(parents=True, exist_ok=True)
    return path


def prepare() -> None:
    kb = get_settings().knowledge_base_dir
    total = 0
    for name in names():
        cases = load(name)
        app = cases[0]["profile"]
        profile = IntegrationProfile(
            company="Eval Co",
            platforms=[dict(zip(("platform", "config_mode"), app.split("/")))],
            modules=ALL_MODULES,
            environment="uat",
            region="IN",
            customer_id_type="mobile",
            confirmed=True,
        )
        kit = build_guide(profile, kb)
        (folder("kits") / f"{name}.md").write_text(kit, encoding="utf-8")
        questions = [{"id": c["id"], "question": " ".join(str(c["question"]).split())} for c in cases]
        (folder("questions") / f"{name}.json").write_text(json.dumps(questions, indent=1, ensure_ascii=False), encoding="utf-8")
        total += len(cases)
        print(f"{name:26s} {len(cases):3d} questions  kit ~{len(kit) // 4000}k tokens")
    print(f"{total} questions in {len(names())} files -> {WORK}")


def grade() -> None:
    for name in names():
        path = WORK / "answers" / f"{name}.json"
        if not path.is_file():
            print(f"{name}: no answers yet")
            continue
        answers = json.loads(path.read_text(encoding="utf-8"))
        tasks, det = [], {}
        for c in load(name):
            answer = str(answers.get(c["id"], ""))
            low = answer.lower()
            expect = c.get("expect") or {}
            fails = []
            if not answer.strip():
                fails.append("no answer")
            fails += [f"missing {s!r}" for s in expect.get("contains", []) if s.lower() not in low]
            fails += [f"forbidden {s!r}" for s in expect.get("not_contains", []) if s.lower() in low]
            det[c["id"]] = fails
            if expect.get("judge"):
                tasks.append(
                    {
                        "id": c["id"],
                        "question": " ".join(str(c["question"]).split()),
                        "answer": answer,
                        "checks": [j["q"] for j in expect["judge"]],
                    }
                )
        (folder("judge") / f"{name}.json").write_text(json.dumps(tasks, indent=1, ensure_ascii=False), encoding="utf-8")
        (folder("det") / f"{name}.json").write_text(json.dumps(det, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{name:26s} answers {len(answers):3d}   judge tasks {len(tasks):3d}")


def score(detail: bool = True) -> dict:
    rows, by_cat, by_file, failures = [], defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), []
    for name in names():
        det_path, verdict_path = WORK / "det" / f"{name}.json", WORK / "verdicts" / f"{name}.json"
        if not det_path.is_file():
            continue
        det = json.loads(det_path.read_text(encoding="utf-8"))
        verdicts = json.loads(verdict_path.read_text(encoding="utf-8")) if verdict_path.is_file() else {}
        answers = json.loads((WORK / "answers" / f"{name}.json").read_text(encoding="utf-8"))
        for c in load(name):
            fails = list(det.get(c["id"], ["not graded"]))
            judges = (c.get("expect") or {}).get("judge", [])
            got = verdicts.get(c["id"])
            if judges and got is None:
                fails.append("judge verdict missing")
            elif judges:
                for j, g in zip(judges, got):
                    if str(g).strip().lower() != str(j["want"]).strip().lower():
                        fails.append(f"judge: wanted {j['want']!r} for: {j['q']}")
            ok = not fails
            cat = c.get("category", "?")
            for table, key in ((by_cat, cat), (by_file, name)):
                table[key][0] += ok
                table[key][1] += 1
            rows.append((name, c["id"], cat, ok))
            if not ok:
                failures.append({"file": name, "id": c["id"], "category": cat, "question": " ".join(str(c["question"]).split()), "fails": fails, "answer": str(answers.get(c["id"], ""))[:600]})
    passed = sum(r[3] for r in rows)
    total = len(rows)
    if detail:
        print(f"\n{'file':26s} {'pass':>9s}")
        for k, (p, t) in sorted(by_file.items()):
            print(f"{k:26s} {p:3d}/{t:<3d} {100 * p / t:5.1f}%")
        print(f"\n{'category':16s} {'pass':>9s}")
        for k, (p, t) in sorted(by_cat.items(), key=lambda kv: kv[1][0] / kv[1][1]):
            print(f"{k:16s} {p:3d}/{t:<3d} {100 * p / t:5.1f}%")
        print(f"\nOVERALL {passed}/{total} = {100 * passed / max(total, 1):.1f}%   ({len(failures)} failing)")
    (WORK / "failures.json").write_text(json.dumps(failures, indent=1, ensure_ascii=False), encoding="utf-8")
    return {"passed": passed, "total": total, "failures": failures}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"prepare": prepare, "grade": grade, "score": score}.get(cmd, lambda: sys.exit(__doc__))()
