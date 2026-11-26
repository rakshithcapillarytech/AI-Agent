"""The checks an automatic update must pass before it can go live: the tests, the guide template, the knowledge-base audit
and the key facts. If any fails, the update is not merged and a person looks at it."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GateResult:
    name: str
    ok: bool
    detail: str = ""


CHECKS: list[tuple[str, list[str]]] = [
    ("tests", ["-m", "pytest", "-q", "-x"]),
    ("guide template (kb lint)", ["-m", "app.kb.lint"]),
    ("knowledge-base audit", ["-m", "evals.audit_kb"]),
    ("key facts", ["-m", "app.sync", "check"]),
]


def run_gate(repo_root: Path, timeout: int = 900) -> list[GateResult]:
    results = []
    for name, args in CHECKS:
        try:
            done = subprocess.run([sys.executable, *args], cwd=repo_root, capture_output=True, text=True, timeout=timeout, check=False)
            tail = "\n".join((done.stdout + done.stderr).strip().splitlines()[-6:])
            results.append(GateResult(name, done.returncode == 0, tail))
        except subprocess.TimeoutExpired:
            results.append(GateResult(name, False, f"timed out after {timeout}s"))
    return results


def passed(results: list[GateResult]) -> bool:
    return bool(results) and all(r.ok for r in results)
