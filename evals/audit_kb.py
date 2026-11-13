"""Deterministic audit of the knowledge base and the kits built from it (no model calls).

    uv run python -m evals.audit_kb            # all checks
    uv run python -m evals.audit_kb --verbose  # also list every finding

Each check returns findings; an ERROR is a real defect, a WARN needs a human look. Exit code 1 on any ERROR.
"""

import itertools
import json
import re
import sys
from pathlib import Path

import frontmatter
import yaml

from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.kb.guide import build_guide
from app.kb.loader import files_for_profile
from app.rules.prereq_engine import build_checklist, load_rules

KB = get_settings().knowledge_base_dir
ROOT = KB.parent
PLATFORMS = ["android", "ios", "react-native", "flutter", "web"]
MODES = ["firebase", "direct"]
PLATFORM_FILES = [f"{p}/{m}.md" for p in PLATFORMS for m in MODES]
SHARED = sorted(p.relative_to(KB).as_posix() for p in (KB / "_shared").glob("*.md"))
ALL_FILES = PLATFORM_FILES + SHARED
ALL_MODULES = ["core", "push", "inapp", "inbox_api", "inbox_ui", "visitor", "gamification", "multi_account"]

# Things that must not appear in any knowledge file: secrets and internal leaks.
LEAK_PATTERNS = {
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_\-]{15,}\.[A-Za-z0-9_\-]{15,}\."),
    "FCM token": re.compile(r"\b[A-Za-z0-9_\-]{20,}:APA91b[A-Za-z0-9_\-]{20,}"),
    "AWS key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Basic auth header": re.compile(r"Authorization:\s*Basic\s+[A-Za-z0-9+/=]{16,}", re.I),
    "capillary email": re.compile(r"[\w.+-]+@capillarytech\.com", re.I),
    "internal wiki host": re.compile(r"atlassian\.net|sharepoint\.com|hotswap", re.I),
    "internal ticket": re.compile(r"\bCAP-\d{4,}\b"),
    "wk_live key": re.compile(r"\bwk_live_[A-Za-z0-9]+"),
}
# APIs/tools of one OS that should not show up in a file for the other OS.
FOREIGN = {
    "android": [(re.compile(r"\bCocoaPods\b|\bPodfile\b|\bXcode\b|\.xcodeproj|\bSwiftUI\b"), "iOS tooling")],
    "ios": [(re.compile(r"\bGradle\b|build\.gradle|AndroidManifest|\bLogcat\b"), "Android tooling")],
    "web": [
        (re.compile(r"\bCocoaPods\b|\bPodfile\b|\bXcode\b|build\.gradle|AndroidManifest"), "mobile tooling"),
    ],
}

Finding = tuple[str, str, str]  # (level, where, message)


def read(rel: str) -> str:
    return (KB / rel).read_text(encoding="utf-8")


def body(rel: str) -> str:
    return frontmatter.loads(read(rel)).content


def fence_spans(text: str):
    """(info, content, start_line) for every fenced block."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        m = re.match(r"^\s*(```+|~~~+)\s*(.*)$", lines[i])
        if m:
            fence, info, j = m.group(1), m.group(2).strip(), i + 1
            buf = []
            while j < len(lines) and not lines[j].lstrip().startswith(fence[:3]):
                buf.append(lines[j])
                j += 1
            out.append((info, "\n".join(buf), i + 1, j < len(lines)))
            i = j + 1
        else:
            i += 1
    return out


def check_fences() -> list[Finding]:
    f = []
    for rel in ALL_FILES:
        for info, _, line, closed in fence_spans(body(rel)):
            if not closed:
                f.append(("ERROR", rel, f"code fence opened at body line {line} is never closed"))
    return f


def check_embedded_data() -> list[Finding]:
    """json / yaml blocks must parse once placeholders are filled in."""
    f = []
    for rel in ALL_FILES:
        for info, code, line, _ in fence_spans(body(rel)):
            lang = info.split()[0].lower() if info else ""
            if lang not in ("json", "yaml", "yml"):
                continue
            text = re.sub(r"\{\{[^}]+\}\}", "x", code)
            text = re.sub(r"<[A-Z_]+>", "x", text)
            try:
                (json.loads if lang == "json" else yaml.safe_load)(text)
            except Exception as e:  # noqa: BLE001
                f.append(("WARN", rel, f"{lang} block at body line {line} doesn't parse: {str(e)[:70]}"))
    return f


def step_numbers(rel: str) -> set[str]:
    sec = re.search(r"\n## Steps\n(.*?)(?=\n## )", "\n" + body(rel), re.S)
    return set(re.findall(r"^### (G?\d+)\.", sec.group(1), re.M)) if sec else set()


def check_steps_and_refs() -> list[Finding]:
    f = []
    for rel in PLATFORM_FILES:
        text = body(rel)
        have = step_numbers(rel)
        nums = [int(n) for n in have if n.isdigit()]
        if nums and sorted(nums) != list(range(1, max(nums) + 1)):
            f.append(("ERROR", rel, f"step numbers aren't 1..N without gaps or repeats: {sorted(nums)}"))
        heads = re.findall(r"^### (G?\d+)\.", text, re.M)
        dupes = {h for h in heads if heads.count(h) > 1}
        if dupes:
            f.append(("ERROR", rel, f"duplicate step headings: {sorted(dupes)}"))
        # references like (step 12), step G2, steps 8 and 10, steps 3–4
        for m in re.finditer(r"\bsteps?\s+(G?\d+)(?:\s*(?:and|,|–|-|to)\s*(G?\d+))?", text):
            for n in filter(None, m.groups()):
                if n not in have:
                    ctx = text[max(0, m.start() - 40): m.end() + 20].replace("\n", " ")
                    f.append(("WARN", rel, f"refers to step {n} but there's no such step: …{ctx}…"))
    return f


def check_cross_references() -> list[Finding]:
    f = []
    known = {p for p in ALL_FILES}
    for rel in ALL_FILES + ["prerequisites.yaml"]:
        text = read(rel)
        for m in re.finditer(r"`((?:_shared/[\w\-]+|(?:android|ios|react-native|flutter|web)/(?:firebase|direct))(?:\.md)?)`", text):
            path = m.group(1) if m.group(1).endswith(".md") else m.group(1) + ".md"
            if path not in known:
                f.append(("ERROR", rel, f"refers to `{m.group(1)}`, which doesn't exist"))
        for m in re.finditer(r"`(_shared/[\w\-]+\.md) › ([^`]+?)`", text):
            path, heading = m.groups()
            if path in known and heading.strip().lower() not in "\n".join(re.findall(r"^#{2,4} (.+)$", body(path), re.M)).lower():
                f.append(("WARN", rel, f"refers to heading '{heading}' not found in {path}"))
    return f


def check_leaks() -> list[Finding]:
    f = []
    for rel in ALL_FILES + ["prerequisites.yaml"]:
        text = read(rel)
        for name, pat in LEAK_PATTERNS.items():
            for m in pat.finditer(text):
                f.append(("ERROR", rel, f"{name}: …{text[max(0, m.start() - 20): m.end() + 10]!r}"))
    return f


def check_contamination() -> list[Finding]:
    f = []
    for rel in PLATFORM_FILES:
        platform = rel.split("/")[0]
        for pat, label in FOREIGN.get(platform, []):
            for m in pat.finditer(body(rel)):
                line = body(rel)[: m.start()].count("\n")
                f.append(("WARN", rel, f"{label} mentioned in a {platform} file ({m.group(0)}), body line {line}"))
    return f


def check_leftovers() -> list[Finding]:
    f = []
    for rel in ALL_FILES:
        for i, line in enumerate(body(rel).splitlines(), 1):
            if re.search(r"\b(TODO|FIXME|XXX|lorem ipsum)\b", line) and "// TODO" not in line and "TODO:" not in line and "# TODO" not in line:
                f.append(("WARN", rel, f"leftover marker on body line {i}: {line.strip()[:80]}"))
            if "None" in line and "sdk_version" in line:
                f.append(("ERROR", rel, f"'None' in an sdk_version line {i}"))
            if re.search(r"[“”‘’]", line) and re.match(r"^\s{0,3}(let|val|var|const|import|\w+\()", line.strip()):
                f.append(("WARN", rel, f"curly quotes in what looks like code, body line {i}"))
    return f


def check_front_matter() -> list[Finding]:
    f = []
    for rel in PLATFORM_FILES:
        meta = frontmatter.loads(read(rel)).metadata
        covered, missing = set(meta.get("modules_covered") or []), set(meta.get("modules_missing") or [])
        if covered & missing:
            f.append(("ERROR", rel, f"modules both covered and missing: {sorted(covered & missing)}"))
        if (covered | missing) - set(ALL_MODULES):
            f.append(("ERROR", rel, f"unknown modules {(covered | missing) - set(ALL_MODULES)}"))
        if not covered | missing >= {"core"} and "core" not in covered | missing:
            f.append(("WARN", rel, "core is neither covered nor missing"))
        text = body(rel)
        if meta.get("sdk_version") in (None, "null") and "{{sdk_version}}" in re.sub(r"(?m)^>.*$", "", text):
            f.append(("ERROR", rel, "uses {{sdk_version}} in code but sdk_version is null (it would render unfilled)"))
        # every "covered" module should have real content: not only a Gap under its heading
        for mod, heading in {"push": "Push", "inapp": "In-App", "inbox_api": "Inbox", "visitor": "Visitor", "gamification": "Gamification"}.items():
            m = re.search(rf"\n### {heading}\n(.*?)(?=\n### |\n## )", "\n" + text, re.S)
            if mod in covered and m and len(re.sub(r"(?m)^>.*$", "", m.group(1)).strip()) < 40:
                f.append(("WARN", rel, f"'{mod}' is listed as covered but ### {heading} has almost no content"))
            if mod in missing and m and len(re.sub(r"(?m)^>.*$", "", m.group(1)).strip()) > 400:
                f.append(("WARN", rel, f"'{mod}' is listed as missing but ### {heading} has real content"))
    return f


def profile(apps: list[str], modules: list[str]) -> IntegrationProfile:
    return IntegrationProfile(
        company="Audit Co",
        platforms=[dict(zip(("platform", "config_mode"), a.split("/"))) for a in apps],
        modules=modules,
        environment="uat",
        region="IN",
        customer_id_type="mobile",
        confirmed=True,
    )


def check_kits() -> list[Finding]:
    """Build a kit for every platform × mode × module combination of interest, and inspect it."""
    f, sizes = [], {}
    module_sets = [["core"], ["core", "push"], ["core", "gamification"], ALL_MODULES]
    for rel in PLATFORM_FILES:
        app = rel[:-3]
        for modules in module_sets:
            where = f"kit {app} {'+'.join(modules) if len(modules) < 8 else 'all-modules'}"
            try:
                kit = build_guide(profile([app], modules), KB)
            except Exception as e:  # noqa: BLE001
                f.append(("ERROR", where, f"kit failed to build: {e}"))
                continue
            sizes[where] = len(kit) // 4
            if re.search(r"\{\{(?!placeholders|account_id|base_url|ssl_public_key|org_id|gamification_key|gamification_region|gamification_base_url|banner_id|embed_id|loyalty_id|application_id|bundle_id)[^}]+\}\}", kit):
                f.append(("ERROR", where, "kit contains an unknown {{placeholder}}"))
            if "{{sdk_version}}" in re.sub(r"(?m)^>.*$", "", kit):
                f.append(("WARN", where, "{{sdk_version}} left unfilled outside callouts"))
            if re.search(r"\bsdk_version: ?None|version None|:None\b", kit):
                f.append(("ERROR", where, "'None' rendered as a version"))
            expected_push = "push" in modules and any(rel.startswith(p) for p in ("android/firebase", "ios/", "react-native/", "flutter/"))
            if ("Push notifications on mobile" in kit) != expected_push:
                f.append(("ERROR", where, f"_shared/push.md {'missing' if expected_push else 'included'} unexpectedly"))
            if "Troubleshooting (all platforms)" not in kit:
                f.append(("ERROR", where, "troubleshooting file missing from the kit"))
            for other in PLATFORMS:
                label = {"android": "# Android", "ios": "# iOS", "react-native": "# React Native", "flutter": "# Flutter", "web": "# Web"}[other]
                if other != rel.split("/")[0] and re.search(rf"^#{{1,3}} {re.escape(label[2:])} \(", kit, re.M):
                    f.append(("ERROR", where, f"kit contains the {other} platform file"))
            if len(kit) // 4 > 60000:
                f.append(("WARN", where, f"kit is {len(kit)//4} tokens"))
    # multi-platform combos
    for apps in (["android/firebase", "ios/firebase"], ["react-native/direct", "flutter/direct"], [f"{p}/{m}" for p, m in zip(PLATFORMS, ["firebase", "direct", "firebase", "direct", "firebase"])]):
        try:
            kit = build_guide(profile(apps, ALL_MODULES), KB)
            sizes["kit " + "+".join(apps)] = len(kit) // 4
            for a in apps:
                if f"# {a.split('/')[0]}" and a.split("/")[0] != "web" and "Troubleshooting" not in kit:
                    f.append(("ERROR", "kit " + "+".join(apps), "troubleshooting missing"))
        except Exception as e:  # noqa: BLE001
            f.append(("ERROR", "kit " + "+".join(apps), f"failed: {e}"))
    return f, sizes


def check_rules() -> list[Finding]:
    f = []
    rules = load_rules(KB)
    for rule in rules.items:
        path, _, heading = rule.source.partition(" › ")
        if not (KB / path).is_file():
            f.append(("ERROR", f"rule {rule.id}", f"source file {path} doesn't exist"))
        elif heading and heading.strip().lower() not in "\n".join(re.findall(r"^#{2,4} (.+)$", body(path), re.M)).lower():
            f.append(("WARN", f"rule {rule.id}", f"source heading '{heading}' not found in {path}"))
    for rel in PLATFORM_FILES:
        app = rel[:-3]
        for modules in (["core"], ["core", "push", "gamification"], ALL_MODULES):
            items = build_checklist(profile([app], modules), rules)
            if not items:
                f.append(("ERROR", f"checklist {app}", "no checklist items"))
            if len({i.id for i in items}) != len(items):
                f.append(("ERROR", f"checklist {app}", "duplicate item ids"))
            if not any(i.owner == "capillary" for i in items):
                f.append(("ERROR", f"checklist {app}", "no Capillary-provided items"))
            if not app.startswith("web/") and not any(i.owner == "client" for i in items):
                f.append(("ERROR", f"checklist {app}", "no client items for a mobile app"))
    return f


def check_evals() -> list[Finding]:
    """Every golden/deep eval must be answerable from the kit it targets."""
    f = []
    for path in sorted((ROOT / "evals").glob("*.yaml")) + sorted((ROOT / "evals" / "deep").glob("*.yaml")):
        cases = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for case in cases:
            where = f"{path.name}:{case['id']}"
            plat, _, mode = case["profile"].partition("/")
            kit = build_guide(profile([case["profile"]], ["core", "push", "gamification"]), KB)
            kit_l = kit.lower()
            for s in (case.get("expect") or {}).get("contains", []):
                if s.lower() not in kit_l:
                    f.append(("ERROR", where, f"required string {s!r} isn't in the kit for {case['profile']}"))
            for s in (case.get("expect") or {}).get("not_contains", []):
                if s.lower() in kit_l and "don't use" not in kit_l:
                    f.append(("WARN", where, f"forbidden string {s!r} appears in the kit (check it's only in a ❌ callout)"))
            src = str(case.get("source", ""))
            m = re.match(r"([\w\-/]+\.md)", src)
            if m and not (KB / m.group(1)).is_file():
                f.append(("ERROR", where, f"source file {m.group(1)} doesn't exist"))
    return f


CHECKS = [
    ("code fences closed", check_fences),
    ("json/yaml blocks parse", check_embedded_data),
    ("step numbering and references", check_steps_and_refs),
    ("cross-references to files/headings", check_cross_references),
    ("secrets and internal leaks", check_leaks),
    ("cross-platform contamination", check_contamination),
    ("leftover markers, 'None', curly quotes", check_leftovers),
    ("front matter vs content", check_front_matter),
    ("prerequisite rules and checklists", check_rules),
    ("evals answerable from their kit", check_evals),
]


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv
    errors = warns = 0
    for name, fn in CHECKS:
        found = fn()
        e = [x for x in found if x[0] == "ERROR"]
        w = [x for x in found if x[0] == "WARN"]
        errors, warns = errors + len(e), warns + len(w)
        print(f"{'FAIL' if e else 'warn' if w else 'ok  '}  {name}: {len(e)} error(s), {len(w)} warning(s)")
        for level, where, msg in (found if verbose or e else found[:6]):
            print(f"      {level} {where}: {msg}")
        if not verbose and len(w) > 6 and not e:
            print(f"      … {len(w) - 6} more (use --verbose)")
    found, sizes = check_kits()
    e = [x for x in found if x[0] == "ERROR"]
    w = [x for x in found if x[0] == "WARN"]
    errors, warns = errors + len(e), warns + len(w)
    print(f"{'FAIL' if e else 'warn' if w else 'ok  '}  kits ({len(sizes)} combinations built): {len(e)} error(s), {len(w)} warning(s)")
    for level, where, msg in found[:20]:
        print(f"      {level} {where}: {msg}")
    big = sorted(sizes.items(), key=lambda kv: -kv[1])[:4]
    print("      largest kits: " + "; ".join(f"{k.replace('kit ', '')} ~{v // 1000}k tokens" for k, v in big))
    print(f"\n{errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
