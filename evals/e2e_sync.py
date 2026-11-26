"""End-to-end test of the online docs sync and the automatic update.

    uv run python -m evals.e2e_sync            # all scenarios against a local fake of the docs site
    uv run python -m evals.e2e_sync --live     # also one run against the real docs site (about 80 seconds)
    uv run python -m evals.e2e_sync --quick    # skip the tests and audit gates (faster, weaker)

Each scenario works on a throwaway clone of this repository's HEAD (commit your changes first), pointed at a local web
server that serves the real mirrored pages and can be changed, slowed down or switched off. The real pipeline runs: the
real HTTP client, the real CLI, the real checks (tests, template lint, audit, key facts) as the gate, and the real API.
Nothing here touches your working tree, the real docs site (except `--live`, read-only) or git remotes.
"""

import argparse
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.config import ROOT
from app.sync.client import HttpFetcher
from app.sync.gate import GateResult, run_gate
from app.sync.models import load_config
from app.sync.propose import ProposalError, propose
from app.sync.service import run_and_report
from app.sync.status import sync_status
from app.sync.values import Substitution, apply_text

UPDATED = re.compile(r"^updatedAt:.*$", re.MULTILINE)
SNAPSHOT = Path("knowledge_base/source/capillary-docs")


# ── a fake docs site you can change, slow down or switch off ──────────────────────────────────────


class DocsServer:
    def __init__(self) -> None:
        self.pages: dict[str, str] = {}
        self.index = ""
        self.down = False
        self.throttle = 0  # answer the next N page requests with HTTP 429
        self.broken: set[str] = set()  # slugs that always answer HTTP 503
        self.hits: list[str] = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                outer.hits.append(self.path)
                if outer.down:
                    return self._send(503, "down", {"Retry-After": "0"})
                slug = self.path.rsplit("/", 1)[-1].removesuffix(".md")
                if self.path == "/llms.txt":
                    return self._send(200, outer.index)
                if slug in outer.broken:
                    return self._send(503, "broken", {"Retry-After": "0"})
                if outer.throttle > 0:
                    outer.throttle -= 1
                    return self._send(429, "slow down", {"Retry-After": "0"})
                if slug in outer.pages and self.path.startswith("/docs/"):
                    return self._send(200, outer.pages[slug])
                return self._send(404, "not found")

            def _send(self, status: int, body: str, headers: dict[str, str] | None = None) -> None:
                data = body.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                for key, value in (headers or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args) -> None:  # keep the output quiet
                pass

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self._server.server_address[1]}"
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def load_from(self, clone: Path) -> None:
        pages = clone / SNAPSHOT / "pages"
        self.pages = {p.stem: p.read_text(encoding="utf-8") for p in pages.glob("*.md")}
        branch = (clone / SNAPSHOT / "index.txt").read_text(encoding="utf-8")
        self.index = "# Docs\n\n## Developer\n" + branch
        self.down, self.throttle, self.broken, self.hits = False, 0, set(), []

    def edit(self, slug: str, change) -> None:
        """Change a page the way the docs team would: new text, and a new `updatedAt`."""
        text = change(self.pages[slug])
        self.pages[slug] = UPDATED.sub("updatedAt: 2026-12-03T10:00:00.000Z", text, count=1)

    def close(self) -> None:
        self._server.shutdown()


# ── scaffolding ───────────────────────────────────────────────────────────────────────────────────


@dataclass
class Result:
    scenario: str
    checks: list[tuple[bool, str]] = field(default_factory=list)
    seconds: float = 0.0
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and all(ok for ok, _ in self.checks)


class Scenario:
    def __init__(self, name: str) -> None:
        self.result = Result(name)

    def check(self, label: str, condition: bool, detail: str = "") -> None:
        self.result.checks.append((bool(condition), label + (f"  [{detail}]" if detail and not condition else "")))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def sdk_version(clone: Path, guide: str) -> str:
    match = re.search(r"^sdk_version:\s*(\S+)", (clone / "knowledge_base" / guide).read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else "?"


def make_clone(work: Path, name: str, server: DocsServer | None) -> Path:
    """A throwaway copy of HEAD, pointed at the local server (or left alone when `server` is None)."""
    dest = work / name
    git(ROOT, "clone", "-q", str(ROOT), str(dest))
    git(dest, "config", "user.email", "e2e@example.test")
    git(dest, "config", "user.name", "e2e")
    if (ROOT / ".env").is_file():
        shutil.copy(ROOT / ".env", dest / ".env")  # the API needs its settings; .env is git-ignored
    if server is not None:
        server.load_from(dest)
        sources = dest / "knowledge_base" / "sources.yaml"
        text = sources.read_text(encoding="utf-8")
        text = text.replace("base_url: https://docs.capillarytech.com", f"base_url: {server.url}")
        text = re.sub(r"delay_seconds: [\d.]+", "delay_seconds: 0", text)
        sources.write_text(text, encoding="utf-8")
        run_and_report(dest / "knowledge_base")  # the first fetch rewrites the page URLs; keep the reviewed baseline
        git(dest, "add", "-A")
        git(dest, "commit", "-q", "-m", "e2e: point at the local docs server")
    return dest


def version_pages(server: DocsServer) -> list[str]:
    return sorted(s for s, t in server.pages.items() if re.search(r"(?<![\w.])1\.10\.6(?!\w|\.\d)", t))


def bump(server: DocsServer, slugs: list[str]) -> None:
    for slug in slugs:
        server.edit(slug, lambda t: apply_text(t, [Substitution("1.10.6", "1.10.7")]))


def kit(clone: Path, platform: str = "android", mode: str = "firebase") -> str:
    code = (
        "import sys; sys.path.insert(0, '.')\n"
        "from app.config import get_settings\nfrom app.graph.state import IntegrationProfile\nfrom app.kb.guide import build_guide\n"
        f"p = IntegrationProfile.model_validate({{'company': 'E2E', 'platforms': [{{'platform': '{platform}', 'config_mode': '{mode}'}}],"
        "'modules': ['core'], 'environment': 'uat', 'region': 'IN', 'customer_id_type': 'mobile', 'confirmed': True})\n"
        "print(build_guide(p, get_settings().knowledge_base_dir))\n"
    )
    return subprocess.run([sys.executable, "-c", code], cwd=clone, capture_output=True, text=True, check=True).stdout


def kb_status(clone: Path) -> dict:
    return sync_status(clone / "knowledge_base")


def gate_for(quick: bool):
    if not quick:
        return run_gate

    def light(root: Path) -> list[GateResult]:
        out = []
        for name, args in [("key facts", ["-m", "app.sync", "check"]), ("template", ["-m", "app.kb.lint"])]:
            done = subprocess.run([sys.executable, *args], cwd=root, capture_output=True, text=True, check=False)
            out.append(GateResult(name, done.returncode == 0, ""))
        return out

    return light


# ── scenarios ─────────────────────────────────────────────────────────────────────────────────────


def s1_full_bump_through_the_cli(work: Path, server: DocsServer, quick: bool) -> Scenario:
    """Capillary bumps the SDK version on every page that states it. The real CLI updates the guides by itself."""
    s = Scenario("1. Version bump on every page, through the real CLI (merges by itself)")
    clone = make_clone(work, "s1", server)
    pages = version_pages(server)
    bump(server, pages)
    s.check("the bump touches pages on every platform", len(pages) >= 8, f"{len(pages)} pages")
    cmd = [sys.executable, "-m", "app.sync", "update"]
    done = subprocess.run(cmd, cwd=clone, capture_output=True, text=True, check=False, timeout=900)
    s.check("`app.sync update` exits 0 and says merged", done.returncode == 0 and done.stdout.startswith("merged"), done.stdout[:300] + done.stderr[-300:])
    s.check("every page that moved was recognised as value-only", done.stdout.count("  updated ") == len(pages), f"{done.stdout.count('  updated ')} of {len(pages)}")
    s.check("all four checks ran and passed", done.stdout.count("check ok") == 4 and "FAILED" not in done.stdout, done.stdout[-400:])
    for guide in ("android/direct.md", "android/firebase.md", "ios/direct.md", "ios/firebase.md", "web/direct.md", "web/firebase.md"):
        s.check(f"{guide} now says 1.10.7", sdk_version(clone, guide) == "1.10.7", sdk_version(clone, guide))
    text = kit(clone)
    s.check("a kit built afterwards carries the new version only", "1.10.7" in text and "1.10.6" not in text)
    s.check("the kit says it was checked against the online docs and shows no stale warning", "Checked against Capillary's online developer docs" in text and "changed after this guide" not in text)
    st = kb_status(clone)
    s.check("nothing is left to review and every key fact holds", st["changed"] == [] and st["anchors"]["failing"] == [], str(st["anchors"]["failing"]))
    s.check("the clone is on main with no leftover branches and a clean tree", git(clone, "rev-parse", "--abbrev-ref", "HEAD").strip() == "main" and "docs-sync" not in git(clone, "branch") and not git(clone, "status", "--porcelain").strip())
    s.check("the result is recorded", (clone / SNAPSHOT / "last-proposal.json").is_file() and json.loads((clone / SNAPSHOT / "last-proposal.json").read_text())["status"] == "merged")
    again = subprocess.run(cmd, cwd=clone, capture_output=True, text=True, check=False, timeout=300)
    s.check("running it again changes nothing", again.returncode == 0 and again.stdout.startswith("nothing"), again.stdout[:200])
    return s


def s2_partial_bump(work: Path, server: DocsServer, quick: bool) -> Scenario:
    """Only the Android pages move to the new version; iOS and Web still say the old one."""
    s = Scenario("2. Version bump on the Android pages only (other platforms must not change)")
    clone = make_clone(work, "s2", server)
    android = set(load_config(clone / "knowledge_base").guides["android/direct.md"])
    pages = [p for p in version_pages(server) if p in android]
    bump(server, pages)
    result = propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick))
    s.check("merged", result.status == "merged", f"{result.status}: {result.detail} {[(g.name, g.ok) for g in result.gate]}")
    s.check("only the Android pages were updated", {a["slug"] for a in result.applied} == set(pages), str([a["slug"] for a in result.applied]))
    s.check("Android guides moved to 1.10.7", sdk_version(clone, "android/direct.md") == "1.10.7" and sdk_version(clone, "android/firebase.md") == "1.10.7")
    s.check("iOS and Web guides were left on 1.10.6", sdk_version(clone, "ios/direct.md") == "1.10.6" and sdk_version(clone, "web/direct.md") == "1.10.6")
    s.check("the checks passed", result.gate and all(g.ok for g in result.gate), str([(g.name, g.detail[-200:]) for g in result.gate if not g.ok]))
    st = kb_status(clone)
    s.check("nothing left to review, every key fact holds", st["changed"] == [] and st["anchors"]["failing"] == [], str(st["anchors"]["failing"]))
    return s


def s3_mixed_change_blocks_the_update(work: Path, server: DocsServer, quick: bool) -> Scenario:
    """The version moves everywhere, but one page also gains new text. A person must look; nothing unsafe goes live."""
    s = Scenario("3. Version bump plus a new paragraph on one page (guides must stay as they were)")
    clone = make_clone(work, "s3", server)
    bump(server, version_pages(server))
    server.edit("installing-sdk", lambda t: t + "\n\n## 5. A new mandatory step\n\nRun `gradle verifyHydra` before building.\n")
    result = propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick))
    s.check("the mixed page is left for a person", "installing-sdk" in result.needs_person, str(result.needs_person))
    s.check("the checks refused the half-update", result.applied == [] and any(not g.ok for g in result.gate), str([(g.name, g.ok) for g in result.gate]))
    s.check("the guides still say 1.10.6 (nothing was published)", sdk_version(clone, "android/direct.md") == "1.10.6" and sdk_version(clone, "web/direct.md") == "1.10.6")
    st = kb_status(clone)
    s.check("the changed pages are flagged for review", "installing-sdk" in [c["slug"] for c in st["changed"]], str([c["slug"] for c in st["changed"]]))
    text = kit(clone)
    s.check("clients' kits warn that source pages changed after review", "changed after this guide was last reviewed" in text and "`installing-sdk`" in text)
    s.check("the attempt is kept on its own branch for a person", any(b.strip().endswith("-values") for b in git(clone, "branch").splitlines()))
    s.check("main is on main and clean", git(clone, "rev-parse", "--abbrev-ref", "HEAD").strip() == "main" and not git(clone, "status", "--porcelain").strip())
    return s


def s4_prose_change(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("4. A prose change on a page (flagged, shown as a diff, guides untouched)")
    clone = make_clone(work, "s4", server)
    server.edit("push-notification", lambda t: t.replace("The Capillary backend needs", "Capillary's backend requires", 1))
    drafted: list[Path] = []
    result = propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick), drafter=drafted.append)
    s.check("nothing was applied automatically", result.applied == [] and "push-notification" in result.needs_person, str(result.needs_person))
    s.check("an AI drafter would be asked about it", drafted == [clone / "knowledge_base"])
    st = kb_status(clone)
    page = next((c for c in st["changed"] if c["slug"] == "push-notification"), None)
    s.check("the page is listed for review with the guides it feeds", bool(page) and "android/firebase.md" in page["guides"], str(page))
    s.check("a diff is available", bool(page) and page["has_diff"])
    report = (clone / SNAPSHOT / "CHANGES.md").read_text(encoding="utf-8")
    s.check("the report shows the change", "requires" in report and "push-notification" in report)
    s.check("the Android kit warns", "`push-notification`" in kit(clone))
    s.check("the web kit does not (not one of its pages)", "changed after this guide" not in kit(clone, "web", "direct"))
    return s


def s5_renamed_package(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("5. The package name changes online (names are never auto-applied; the key fact fails loudly)")
    clone = make_clone(work, "s5", server)
    server.edit("installing-sdk", lambda t: t.replace("com.capillarytech:hydra-", "com.example.hydra:hydra-"))
    result = propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick))
    s.check("not applied automatically", result.applied == [] and "installing-sdk" in result.needs_person, str(result.needs_person))
    st = kb_status(clone)
    failing = [a["id"] for a in st["anchors"]["failing"]]
    s.check("the Maven-group key fact is reported as no longer on the online page", "android-maven-group" in failing, str(failing))
    s.check("the guides still carry the old group (a person decides)", "com.capillarytech:hydra-core" in (clone / "knowledge_base/android/direct.md").read_text())
    check = subprocess.run([sys.executable, "-m", "app.sync", "check"], cwd=clone, capture_output=True, text=True, check=False)
    s.check("`app.sync check` exits 1 (usable in CI)", check.returncode == 1 and "android-maven-group" in check.stdout, check.stdout[-300:])
    return s


def s6_pages_added_and_removed(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("6. A page disappears from the index and a new one appears")
    clone = make_clone(work, "s6", server)
    dropped = "web-sdk-troubleshooting"
    server.index = "\n".join(line for line in server.index.splitlines() if f"/{dropped}.md" not in line) + "\n"
    new_line = "    - [A brand new feature](https://docs.capillarytech.com/docs/android-brand-new-feature.md)\n"
    server.index = server.index.replace("  - [iOS SDK]", new_line + "  - [iOS SDK]", 1)
    del server.pages[dropped]  # gone for real: other pages still link to it, so the link now leads nowhere
    server.pages["android-brand-new-feature"] = "---\nupdatedAt: 2026-12-03T10:00:00.000Z\n---\n\n# A brand new feature\n\nUse `hydra.newFeature()`.\n"
    result = run_and_report(clone / "knowledge_base")
    s.check("the sync sees one new and one removed page", result.added == ["android-brand-new-feature"] and result.removed == [dropped], f"added={result.added} removed={result.removed}")
    st = kb_status(clone)
    s.check("the removed page is flagged, not deleted", dropped in st["removed"] and (clone / SNAPSHOT / "pages" / f"{dropped}.md").is_file())
    s.check("the new page is listed as one no guide uses", "android-brand-new-feature" in st["unmapped"], str(st["unmapped"]))
    s.check("the report says so", "android-brand-new-feature" in (clone / SNAPSHOT / "CHANGES.md").read_text())
    return s


def s7_outages_and_rate_limits(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("7. The site is down, rate-limits us, or one page keeps failing")
    clone = make_clone(work, "s7", server)
    before = (clone / SNAPSHOT / "manifest.json").read_text()
    server.down = True
    result = propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick))
    s.check("a dead site is reported as fetch-failed", result.status == "fetch-failed", result.status)
    s.check("and leaves no branch, no change, a clean tree", "docs-sync" not in git(clone, "branch") and not git(clone, "status", "--porcelain").strip() and (clone / SNAPSHOT / "manifest.json").read_text() == before)

    server.down, server.hits = False, []
    server.throttle = 4  # HTTP 429 on the next four requests; the real client must back off and retry
    run = run_and_report(clone / "knowledge_base")
    s.check("HTTP 429 is retried until it works", run.ok and run.fetched >= 59, f"fetched={run.fetched} failed={run.failed}")
    s.check("the throttled requests were really repeated", len(server.hits) >= 59 + 4, f"{len(server.hits)} requests")

    server.hits, server.broken = [], {"flutter-sdk-install"}
    server.edit("flutter-sdk-install", lambda t: t + "\nnew text\n")
    run = run_and_report(clone / "knowledge_base")
    s.check("a page that keeps failing is reported by name", list(run.failed) == ["flutter-sdk-install"], str(run.failed))
    s.check("its old snapshot is kept and everything else was still fetched", "new text" not in (clone / SNAPSHOT / "pages" / "flutter-sdk-install.md").read_text() and run.fetched >= 58)
    return s


def s8_guards(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("8. It refuses to run on uncommitted work or outside a git repository")
    clone = make_clone(work, "s8", server)
    (clone / "knowledge_base" / "faq.yaml").write_text((clone / "knowledge_base" / "faq.yaml").read_text() + "\n# edited by a person\n")
    try:
        propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick))
        s.check("a dirty tree is refused", False)
    except ProposalError as error:
        s.check("a dirty tree is refused", "uncommitted" in str(error), str(error))
    s.check("and nothing was started", "docs-sync" not in git(clone, "branch"))
    try:
        propose(work, clone / "knowledge_base", gate_fn=gate_for(quick))
        s.check("a folder that is not a repository is refused", False)
    except ProposalError as error:
        s.check("a folder that is not a repository is refused", "not a git repository" in str(error))
    return s


def _wait_for(url: str, seconds: float = 40) -> bool:
    end = time.time() + seconds
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except OSError:
            time.sleep(0.5)
    return False


def _call(method: str, url: str, body: dict | None = None) -> tuple[int, dict | list | str]:
    data = json.dumps(body).encode() if body is not None else (b"" if method == "POST" else None)
    request = urllib.request.Request(url, data=data, method=method, headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else ""
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def s9_the_running_api(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("9. The running API and admin flow (status, sync button, diff, mark reviewed)")
    clone = make_clone(work, "s9", server)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.api.main:app", "--port", str(port)], cwd=clone, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    base = f"http://127.0.0.1:{port}"
    try:
        up = _wait_for(base + "/health")
        s.check("the API starts in the clone", up)
        if not up:
            s.result.error = "the API did not start (is Postgres running?)"
            return s
        code, status = _call("GET", base + "/sources/status")
        s.check("public status: synced, nothing to review, all key facts hold", code == 200 and status["synced"] and status["pages_to_review"] == 0 and status["facts_failing"] == 0, str(status))
        server.edit("push-notification", lambda t: t.replace("The Capillary backend needs", "Capillary's backend requires", 1))
        code, result = _call("POST", base + "/admin/sources/sync")
        s.check("the 'check the online docs now' button fetches and finds the change", code == 200 and result["changed"] == ["push-notification"], str(result))
        code, admin = _call("GET", base + "/admin/sources")
        change = (admin.get("changed") or [{}])[0] if isinstance(admin, dict) else {}
        s.check("the admin tab lists the page with a diff and the guides it feeds", change.get("slug") == "push-notification" and any("requires" in line for line in change.get("diff") or []) and "_shared/push.md" in change.get("guides", []), str(change)[:300])
        code, status = _call("GET", base + "/sources/status")
        s.check("the public status now shows one page to review", status["pages_to_review"] == 1, str(status))
        code, _ = _call("GET", base + "/prerequisites?platform=android&mode=firebase")
        s.check("the Prerequisites and FAQ endpoints keep working", code == 200 and _call("GET", base + "/faq")[0] == 200)
        code, _ = _call("POST", base + "/admin/sources/accept", {})
        s.check("accepting with no pages is rejected", code == 422)
        code, accepted = _call("POST", base + "/admin/sources/accept", {"slugs": ["push-notification"]})
        s.check("mark reviewed clears it", code == 200 and accepted == {"accepted": ["push-notification"]} and _call("GET", base + "/sources/status")[1]["pages_to_review"] == 0, str(accepted))
        codes = []
        threads = [threading.Thread(target=lambda: codes.append(_call("POST", base + "/admin/sources/sync")[0])) for _ in range(2)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        s.check("two sync clicks at once never error (the second is refused or runs after)", set(codes) <= {200, 409}, str(codes))
    finally:
        proc.terminate()
        proc.wait(timeout=15)
    return s


def s0_live_site(work: Path, server: DocsServer, quick: bool) -> Scenario:
    s = Scenario("0. The real docs site, read-only (nothing should differ from the snapshot)")
    clone = make_clone(work, "s0", None)
    started = time.time()
    result = propose(clone, clone / "knowledge_base", merge=True, gate_fn=gate_for(quick), fetcher=HttpFetcher(load_config(clone / "knowledge_base").fetch))
    s.check("the live fetch worked", result.status in ("nothing", "merged"), f"{result.status}: {result.detail}")
    s.check("the live site matches the snapshot (or shows exactly what changed)", result.status == "nothing", f"status={result.status} needs_person={result.needs_person} applied={result.applied}")
    s.check("it was polite: no failures from rate limits", "fetch-failed" not in result.status)
    s.result.seconds = time.time() - started
    return s


SCENARIOS = [s1_full_bump_through_the_cli, s2_partial_bump, s3_mixed_change_blocks_the_update, s4_prose_change, s5_renamed_package, s6_pages_added_and_removed, s7_outages_and_rate_limits, s8_guards, s9_the_running_api]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--live", action="store_true", help="also run once against the real docs site")
    parser.add_argument("--quick", action="store_true", help="skip the tests and audit gates")
    parser.add_argument("--only", help="run only scenarios whose name contains this text")
    args = parser.parse_args()

    if git(ROOT, "status", "--porcelain", "--untracked-files=no").strip():
        print("note: the clones use the committed code (HEAD); you have uncommitted changes that are not tested\n")
    work = Path(tempfile.mkdtemp(prefix="e2e-sync-"))
    server = DocsServer()
    todo = [s0_live_site] if args.live else []
    todo = [*todo, *SCENARIOS]
    results: list[Result] = []
    try:
        for scenario in todo:
            started = time.time()
            if args.only and args.only.lower() not in (scenario.__doc__ or scenario.__name__).lower() and args.only not in scenario.__name__:
                continue
            print(f"… {scenario.__name__}", flush=True)
            try:
                result = scenario(work, server, args.quick).result
            except Exception as error:  # noqa: BLE001  # a crashed scenario is a failed scenario
                result = Result(scenario.__name__, error=f"{type(error).__name__}: {error}")
            result.seconds = result.seconds or time.time() - started
            results.append(result)
            print(f"   {'PASS' if result.ok else 'FAIL'}  {result.scenario}  ({result.seconds:.0f}s)")
            for ok, label in result.checks:
                print(f"     {'ok  ' if ok else 'FAIL'} {label}")
            if result.error:
                print(f"     ERROR {result.error}")
    finally:
        server.close()
        shutil.rmtree(work, ignore_errors=True)
    failed = [r for r in results if not r.ok]
    total = sum(len(r.checks) for r in results)
    bad = sum(1 for r in results for ok, _ in r.checks if not ok)
    print(f"\n{len(results) - len(failed)}/{len(results)} scenarios passed, {total - bad}/{total} checks")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
