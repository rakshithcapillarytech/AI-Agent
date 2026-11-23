"""The integration steps as a document for people: one styled web page (print it to PDF from the browser).

The AI guide (app/kb/guide.py) is Markdown written for an AI assistant. This is the same knowledge for a
developer or project manager to read, in two sizes:

- the short summary (the default, about three pages): the client's setup, a personalised "Before you start"
  checklist, minimum versions, the numbered steps for the features they chose (titles only), what to check when
  it doesn't work, and what to confirm with Capillary;
- the full version: every section of the platform guides that helps someone do the work, with all the code.

No new facts are written here: the content is the knowledge files', the checklist comes from the prerequisites
rules, the versions and gaps from requirements.yaml, and the step-to-feature map from step_modules.yaml.
"""

import html
import re
from datetime import date
from functools import lru_cache
from pathlib import Path

import frontmatter
import yaml
from markdown_it import MarkdownIt
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from app.graph.state import IntegrationProfile
from app.kb.guide import (
    CUSTOMER_ID_LABELS,
    MODE_LABELS,
    MODULE_LABELS,
    PLACEHOLDER_LEGEND,
    PLATFORM_LABELS,
    GuideNotReady,
    _demote_headings,
    _slug,
)
from app.kb.loader import files_for_profile, render_versions
from app.kb.sections import split_sections
from app.rules.prereq_engine import load_rules
from app.rules.requirements import build_prerequisites, load_requirements

# What a person needs from a platform file. Left out: Coverage (for maintainers) and API Reference.
STEP_MODULES_FILE = "step_modules.yaml"
STEP_SUMMARIES_DIR = "step_summaries"  # one yaml per platform: what to do in each numbered step
PLATFORM_SECTIONS = ["Requirements", "Prerequisites", "Steps", "Modules", "Verification", "Known Issues"]
# Shared files the reader doesn't need: the overview is for the AI assistant and for maintainers.
SKIPPED_SHARED = {"_shared/overview.md"}
# A platform file's "## Modules" has one "### <name>" block per feature.
MODULE_HEADINGS = {
    "push": "Push",
    "inapp": "In-App",
    "inbox_api": "Inbox",
    "inbox_ui": "Inbox",
    "visitor": "Visitor",
    "gamification": "Gamification",
    "multi_account": "Multi-account",
}

_FENCE = re.compile(r"^\s*(```|~~~)")
_H1 = re.compile(r"^# (.+?)\s*$")
_H2 = re.compile(r"^## (.+?)\s*$")
_H3 = re.compile(r"^### (.+?)\s*$")
_CODE_STYLE = HtmlFormatter(style="friendly", cssclass="code")


def guide_steps_filename(profile: IntegrationProfile, full: bool = False) -> str:
    platforms = "-".join(p.platform for p in profile.platforms)
    return f"hydra-integration-steps-{_slug(profile.company or 'client')}-{platforms}{'-full' if full else ''}.html"


def _split(lines: list[str], heading: re.Pattern[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Text before the first matching heading (fence-aware), then one (title, lines incl. heading) per match."""
    head: list[str] = []
    blocks: list[tuple[str, list[str]]] = []
    in_fence = False
    for line in lines:
        if _FENCE.match(line):
            in_fence = not in_fence
        match = None if in_fence else heading.match(line)
        if match:
            blocks.append((match.group(1), [line]))
        elif blocks:
            blocks[-1][1].append(line)
        else:
            head.append(line)
    return head, blocks


def _modules_section(lines: list[str], wanted: set[str]) -> list[str] | None:
    """The Modules section reduced to the features the client chose; None when none of them is in it."""
    intro, blocks = _split(lines[1:], _H3)
    kept = [b for title, b in blocks if title.strip("` ") not in MODULE_HEADINGS.values() or title.strip("` ") in wanted]
    if not kept:
        return None
    return [lines[0], *intro, *[line for block in kept for line in block]]


def _platform_markdown(text: str, modules: list[str]) -> str:
    """One platform file reduced to the sections a person needs, with the chosen features only."""
    lines = frontmatter.loads(render_versions(text)).content.strip().splitlines()
    _, h1s = _split(lines, _H1)
    title = h1s[0][1][0] if h1s else ""
    _, sections = _split(lines, _H2)
    wanted = {MODULE_HEADINGS[m] for m in modules if m in MODULE_HEADINGS}
    out = [title, ""] if title else []
    for name in PLATFORM_SECTIONS:
        for found, block in sections:
            if found != name:
                continue
            if name == "Modules":
                block = _modules_section(block, wanted)
                if block is None:
                    continue
            out += [*block, ""]
    return "\n".join(out)


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def _checklist_markdown(profile: IntegrationProfile, kb_dir: Path, compact: bool = False) -> str:
    """"Before you start": the rules that apply to this client, in three groups.

    compact: three columns (Done, Item, Details) with "can wait" marked on the item, for the short summary."""
    identifier = CUSTOMER_ID_LABELS.get(profile.customer_id_type or "", "the identifier your customers sign in with")
    groups: dict[str, list[str]] = {"capillary": [], "give": [], "setup": []}
    for rule in load_rules(kb_dir).items:
        if not rule.applies(profile):
            continue
        key = "capillary" if rule.owner == "capillary" else "give" if rule.group else "setup"
        title = _cell(rule.title.replace("{customer_id_type}", identifier))
        details = _cell(rule.short or rule.how)
        if compact:
            groups[key].append(f"| ☐ | {title}{'' if rule.blocking else ' *(can wait)*'} | {details} |")
        else:
            groups[key].append(f"| ☐ | {title} | {'Required' if rule.blocking else 'Can wait'} | {details} |")
    sections = [
        ("capillary", "What Capillary gives you", "Sent once your app is registered."),
        ("give", "What you send to Capillary", "Used to register your app. A mismatch stops the SDK from starting."),
        ("setup", "What you set up yourself", "Repository access, Firebase and CRM settings."),
    ]
    header = ["| Done | Item | Details |", "|---|---|---|"] if compact else [
        "| Done | Item | When | Details |",
        "|---|---|---|---|",
    ]
    intro = (
        "Tick these off before you write code. What you send to Capillary must match your app exactly, "
        "or the SDK can't start."
        if compact
        else "Tick these off before you write code."
    )
    out = ["## Before you start", "", intro, ""]
    for key, title, hint in sections:
        if groups[key]:
            out += [f"### {title}", "", *([] if compact else [hint, ""]), *header, *groups[key], ""]
    out += [
        (
            "> Never paste keys, tokens or service-account files into chat, email or git. "
            "Your Capillary contact will tell you how to send them securely."
        ),
        "",
    ]
    return "\n".join(out)


def _ready(profile: IntegrationProfile) -> None:
    if not profile.platforms or any(p.config_mode is None for p in profile.platforms):
        raise GuideNotReady("Choose whether each app uses Firebase before downloading the steps.")


def _setup_rows(profile: IntegrationProfile) -> list[str]:
    apps = ", ".join(f"{PLATFORM_LABELS[p.platform]} {MODE_LABELS[p.config_mode]}" for p in profile.platforms)
    rows = [
        ("Company", profile.company or "—"),
        ("Apps", apps),
        ("Features", ", ".join(MODULE_LABELS[m] for m in profile.modules) or "—"),
        ("Environment", {"uat": "Testing (UAT)", "production": "Live (Production)"}.get(profile.environment or "", "—")),
        ("Region", profile.region or "—"),
        ("Customers sign in with", CUSTOMER_ID_LABELS.get(profile.customer_id_type or "", "—")),
    ]
    return ["| Setting | Your choice |", "|---|---|", *[f"| {label} | {_cell(value)} |" for label, value in rows]]


# ── The short summary ─────────────────────────────────────────────────────────────────────────────────────


@lru_cache
def _step_modules(kb_dir: Path) -> dict[str, dict[str, dict]]:
    return yaml.safe_load((kb_dir / STEP_MODULES_FILE).read_text(encoding="utf-8")) or {}


@lru_cache
def step_summaries(kb_dir: Path) -> dict[str, dict[str, dict]]:
    """`{"android/firebase": {"5": {"do": "...", "evidence": [...]}}}` merged from knowledge_base/step_summaries/*.yaml."""
    merged: dict[str, dict[str, dict]] = {}
    for path in sorted((kb_dir / STEP_SUMMARIES_DIR).glob("*.yaml")):
        for rel, steps in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).items():
            merged.setdefault(rel, {}).update({str(k): v for k, v in steps.items()})
    return merged


def step_text(kb_dir: Path, rel: str, step_id: str) -> str:
    """The guide's own text of one numbered step (heading to the next step or section), for evidence checks."""
    text = frontmatter.loads(render_versions((kb_dir / f"{rel}.md").read_text(encoding="utf-8"))).content
    match = re.search(rf"^### {re.escape(step_id)}\. .*?(?=^### |^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(0) if match else ""


_STEP_TITLE = re.compile(r"^(G?\d+)\.\s+(.*)$")
_OPTIONAL = re.compile(r"\s*\(optional\)\s*", re.IGNORECASE)


def steps_for_summary(rel: str, kb_dir: Path, modules: list[str]) -> list[dict]:
    """A platform file's numbered steps for the chosen features: id, title, tags. Order is the guide's."""
    key = rel.removesuffix(".md")
    hidden = _step_modules(kb_dir).get(key, {})
    explained = step_summaries(kb_dir).get(key, {})
    steps = []
    for section in split_sections((kb_dir / rel).read_text(encoding="utf-8")):
        if len(section.path) != 2 or section.path[0] != "Steps":
            continue
        match = _STEP_TITLE.match(section.path[1])
        step_id, title = (match.group(1), match.group(2)) if match else ("", section.path[1])
        feature = hidden.get(step_id)
        if feature and not set(feature["modules"]) & set(modules):
            continue
        optional = bool(_OPTIONAL.search(title))
        tags = [MODULE_LABELS[m].split(" (")[0] for m in (feature or {}).get("modules", [])]
        title = _OPTIONAL.sub(" ", title).strip()
        if tags:  # "(push)" at the end repeats the tag
            title = re.sub(r"\s*\(push\)$", "", title, flags=re.IGNORECASE)
        steps.append(
            {"id": step_id, "title": title, "optional": optional, "tags": tags, "do": (explained.get(step_id) or {}).get("do")}
        )
    return steps


def _feature_blocks(rel: str, kb_dir: Path, modules: list[str]) -> list[str]:
    """Labels of the chosen features that have a block in the guide's Modules section."""
    lines = frontmatter.loads((kb_dir / rel).read_text(encoding="utf-8")).content.splitlines()
    _, sections = _split(lines, _H2)
    present = {t.strip("` ") for name, block in sections if name == "Modules" for t, _ in _split(block[1:], _H3)[1]}
    wanted = [m for m in modules if MODULE_HEADINGS.get(m) in present]
    return list(dict.fromkeys(MODULE_LABELS[m].split(" (")[0] for m in wanted))


def _section_text(kb_dir: Path, rel: str, starts_with: str) -> list[str]:
    """One `##` section of a shared file, without its heading, cut before the first callout."""
    lines = frontmatter.loads((kb_dir / rel).read_text(encoding="utf-8")).content.splitlines()
    for title, block in _split(lines, _H2)[1]:
        if title.startswith(starts_with):
            body = block[1:]
            cut = next((i for i, line in enumerate(body) if line.startswith(">")), len(body))
            return [re.sub(r"\s*\(`_shared/[^)]*\)", "", line) for line in body[:cut]]
    return []


def build_summary_markdown(profile: IntegrationProfile, kb_dir: Path, today: date | None = None) -> str:
    """The short document: setup, checklist, minimum versions, steps, what to do when stuck, what to confirm."""
    _ready(profile)
    today = today or date.today()
    many = len(profile.platforms) > 1
    modules = list(profile.modules)
    requirements = load_requirements(kb_dir)

    def label(p) -> str:
        return f"{PLATFORM_LABELS[p.platform]} {MODE_LABELS[p.config_mode]}"

    versions: list[str] = ["## Minimum versions", ""]
    steps: list[str] = [
        "## Steps",
        "",
        "Do them in this order. The code for each step is in your AI guide or the full version.",
        "",
    ]
    gaps: list[str] = []
    for p in profile.platforms:
        if many:
            versions += [f"### {label(p)}", ""]
            steps += [f"### {label(p)}", ""]
        rows = build_prerequisites(kb_dir, p.platform, p.config_mode, modules)["versions"]
        versions += ["| Requirement | Minimum |", "|---|---|", *[f"| {_cell(r['label'])} | {_cell(r['value'])} |" for r in rows], ""]
        for n, step in enumerate(steps_for_summary(f"{p.platform}/{p.config_mode}.md", kb_dir, modules), 1):
            notes = [*step["tags"], *(["Optional"] if step["optional"] else []), f"Guide step {step['id']}" if step["id"] else ""]
            steps.append(f"{n}. **{step['title']}** — *{' · '.join(t for t in notes if t)}*" + ("  " if step["do"] else ""))
            if step["do"]:
                steps.append(f"   {_cell(step['do'])}")
        steps.append("")
        blocks = _feature_blocks(f"{p.platform}/{p.config_mode}.md", kb_dir, modules)
        if blocks:
            steps += [f"Details for the features you chose ({', '.join(blocks)}) are in the guide's Modules section.", ""]
        gaps += [g for g in requirements.platforms[p.platform].gaps if g not in gaps]

    parts = [
        f"# Hydra SDK integration steps: {_cell(profile.company or 'your app')}",
        "",
        f"Prepared by the Experience+ Integration Copilot on {today.isoformat()}. A short summary for your setup only.",
        "",
        "## Your setup",
        "",
        *_setup_rows(profile),
        "",
        _checklist_markdown(profile, kb_dir, compact=True),
        *versions,
        *steps,
        "## If it doesn't work",
        "",
        *_section_text(kb_dir, "_shared/troubleshooting.md", "1. The app and Capillary's registration"),
        "When you contact Capillary, send:",
        "",
        *[line for line in _section_text(kb_dir, "_shared/troubleshooting.md", "6. What to send") if line.strip().startswith("-")],
        "",
        "## Confirm with your Capillary contact",
        "",
        "Capillary hasn't documented these. Ask instead of guessing:",
        "",
        *[f"- {g}" for g in gaps],
        "",
        (
            "> Code for every step is in your AI guide (attach it to Claude, Cursor or ChatGPT) and in the full "
            "version of this page. This summary is based on draft guides that Capillary engineers are still reviewing."
        ),
    ]
    return "\n".join(parts) + "\n"


# ── The full version ──────────────────────────────────────────────────────────────────────────────────────


def build_full_markdown(profile: IntegrationProfile, kb_dir: Path, today: date | None = None) -> str:
    """The long document: setup, checklist, placeholders, then the guides for this client with all their code."""
    _ready(profile)
    today = today or date.today()
    parts = [
        f"# Hydra SDK integration steps: {_cell(profile.company or 'your app')}",
        "",
        f"Prepared by the Experience+ Integration Copilot on {today.isoformat()}. It covers only your setup.",
        "",
        "## Your setup",
        "",
        *_setup_rows(profile),
        "",
        _checklist_markdown(profile, kb_dir),
        "## Placeholders in the code",
        "",
        "Code samples contain values in double braces. Replace each with the value from Capillary or your project.",
        "",
        "| Placeholder | Replace with |",
        "|---|---|",
        *[f"| `{name}` | {meaning} |" for name, meaning in PLACEHOLDER_LEGEND],
        "",
        (
            "> Notes marked **⚠️ Gap** are things Capillary's documents don't cover: confirm them with your "
            "Capillary contact instead of guessing. Notes marked **⚠️ Correction** replace older information: "
            "use the value marked ✅. This guide is still being reviewed by Capillary engineers."
        ),
    ]
    for rel in files_for_profile(profile):
        path = kb_dir / rel
        if not path.is_file() or rel in SKIPPED_SHARED:
            continue
        text = path.read_text(encoding="utf-8")
        if rel.startswith("_shared/"):
            body = frontmatter.loads(render_versions(text)).content.strip()
        else:
            body = _platform_markdown(text, list(profile.modules)).strip()
        parts += ["", _demote_headings(body)]
    return "\n".join(parts) + "\n"


def build_steps_markdown(profile: IntegrationProfile, kb_dir: Path, today: date | None = None, full: bool = False) -> str:
    return (build_full_markdown if full else build_summary_markdown)(profile, kb_dir, today)


def _highlight(code: str, lang: str, attrs: str) -> str:
    caption = re.search(r"file=(\S+)", attrs or "")
    try:
        lexer = get_lexer_by_name((lang or "").lower())
        body = pygments_highlight(code, lexer, _CODE_STYLE)
    except ClassNotFound:
        body = f'<div class="code"><pre>{html.escape(code)}</pre></div>'
    label = f'<div class="filename">{html.escape(caption.group(1))}</div>' if caption else ""
    return f'<div class="snippet">{label}{body}</div>'


def _fence(self, tokens, idx, options, env) -> str:
    """Render a fenced code block ourselves: highlighted, with the file name above it when the fence names one."""
    lang, _, attrs = (tokens[idx].info or "").strip().partition(" ")
    return _highlight(tokens[idx].content, lang, attrs) + "\n"


def _markdown() -> MarkdownIt:
    # Raw HTML in the source is escaped, so a company name can't inject markup.
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    md.add_render_rule("fence", _fence)
    return md


def _heading_ids(body: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Give h2/h3 ids and return the contents list as (level, id, text)."""
    seen: dict[str, int] = {}
    toc: list[tuple[int, str, str]] = []

    def add(match: re.Match[str]) -> str:
        level, inner = int(match.group(1)), match.group(2)
        text = html.unescape(re.sub(r"<[^>]+>", "", inner))
        base = _slug(text)
        seen[base] = seen.get(base, 0) + 1
        ident = base if seen[base] == 1 else f"{base}-{seen[base]}"
        toc.append((level, ident, text))
        return f'<h{level} id="{ident}">{inner}</h{level}>'

    return re.sub(r"<h([23])>(.*?)</h\1>", add, body), toc


def _callouts(body: str) -> str:
    for label, css in (("Gap", "gap"), ("Correction", "correction")):
        body = body.replace(f"<blockquote>\n<p>⚠️ {label}", f'<blockquote class="callout {css}">\n<p>⚠️ {label}')
    return body


def _toc_html(toc: list[tuple[int, str, str]]) -> str:
    """Contents: one line per top-level section (the setup, the checklist, and each guide)."""
    items = [f'<li><a href="#{ident}">{html.escape(text)}</a></li>' for level, ident, text in toc if level == 2]
    return "<ul>" + "".join(items) + "</ul>"


_CSS = """
:root { color-scheme: light; --ink:#171b24; --muted:#545d6a; --line:#dde1e9; --accent:#17784a; --soft:#f1f3f7; }
* { box-sizing: border-box; }
body { margin:0; background:#f8f9fb; color:var(--ink); font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif; }
.toolbar { position:sticky; top:0; z-index:5; display:flex; gap:12px; align-items:center; justify-content:space-between;
  padding:10px 24px; background:#fff; border-bottom:1px solid var(--line); }
.toolbar span { color:var(--muted); font-size:13px; }
.toolbar button { padding:8px 14px; border:0; border-radius:8px; background:var(--accent); color:#fff; font:inherit; font-weight:600; cursor:pointer; }
main.summary { max-width:780px; }
ol { padding-left:22px; }
ol li { margin:9px 0; }
ol li em { color:var(--muted); font-size:12.5px; }
main { max-width:880px; margin:0 auto; padding:32px 24px 80px; background:#fff; }
h1 { font-size:28px; line-height:1.25; margin:0 0 6px; }
h2 { font-size:22px; margin:40px 0 12px; padding-top:8px; border-top:2px solid var(--line); }
h3 { font-size:17px; margin:28px 0 8px; }
h4 { font-size:15px; margin:22px 0 6px; padding:6px 10px; background:var(--soft); border-left:3px solid var(--accent); border-radius:4px; }
h5 { font-size:14px; margin:16px 0 4px; }
p, li { overflow-wrap:anywhere; }
a { color:#1e6fb8; }
nav.toc { margin:20px 0 8px; padding:14px 18px; background:var(--soft); border-radius:10px; }
nav.toc strong { display:block; margin-bottom:6px; }
nav.toc ul { margin:0; padding-left:18px; columns:2; column-gap:32px; }
nav.toc li { break-inside:avoid; font-size:14px; }
table { width:100%; border-collapse:collapse; margin:12px 0; font-size:14px; }
th, td { padding:7px 10px; border:1px solid var(--line); text-align:left; vertical-align:top; overflow-wrap:break-word; }
th { background:var(--soft); }
code { font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; font-size:.9em; background:var(--soft); padding:1px 5px; border-radius:4px; }
.snippet { margin:12px 0; border:1px solid var(--line); border-radius:8px; overflow:hidden; }
.snippet .filename { padding:4px 12px; background:var(--soft); border-bottom:1px solid var(--line); font:12px ui-monospace,Menlo,monospace; color:var(--muted); }
.code { background:#fff; }
.code pre, pre { margin:0; padding:12px; font:13px/1.5 ui-monospace,"SF Mono",Menlo,Consolas,monospace; white-space:pre-wrap; overflow-wrap:anywhere; }
.code pre code { background:none; padding:0; }
blockquote { margin:14px 0; padding:8px 14px; border-left:4px solid var(--line); background:var(--soft); border-radius:4px; }
blockquote p { margin:4px 0; }
blockquote.gap { border-left-color:#e0a325; background:#fdf6e3; }
blockquote.correction { border-left-color:#1e6fb8; background:#eaf3fb; }
@page { margin:14mm; }
@media print {
  body { background:#fff; font-size:11.5pt; }
  .toolbar { display:none; }
  main { max-width:none; padding:0; }
  h2 { border-top:0; }
  main.full h2 { break-before:page; }
  main.full h1 + p + h2, main.full h2:first-of-type { break-before:auto; }
  h2, h3, h4 { break-after:avoid; }
  table, blockquote, .snippet { break-inside:avoid; }
  main.summary { font-size:10.5pt; line-height:1.45; }
  main.summary th, main.summary td { padding:3px 7px; font-size:9.5pt; }
  main.summary h2 { margin-top:20px; }
  main.summary h3 { margin:14px 0 4px; }
  main.summary ol li { margin:3px 0; }
  a { color:inherit; text-decoration:none; }
}
@media (max-width:640px) { nav.toc ul { columns:1; } main { padding:20px 16px 60px; } .toolbar span { display:none; } }
"""

_SCRIPT = """
document.getElementById("print").addEventListener("click", function () { window.print(); });
if (location.hash === "#print") { window.addEventListener("load", function () { setTimeout(function () { window.print(); }, 400); }); }
"""


def build_steps_html(profile: IntegrationProfile, kb_dir: Path, today: date | None = None, full: bool = False) -> str:
    """The whole page, self-contained (no network needed), ready to open, save, or print to PDF."""
    markdown = build_steps_markdown(profile, kb_dir, today, full)
    body, toc = _heading_ids(_callouts(_markdown().render(markdown)))
    title = f"Hydra SDK integration steps: {profile.company or 'your app'}"
    if full:  # only the long version needs a contents list
        nav = f'<nav class="toc" aria-label="Contents"><strong>Contents</strong>{_toc_html(toc)}</nav>'
        first = body.find("<h2")
        body = body[:first] + nav + body[first:] if first != -1 else body + nav
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title>"
        f"<style>{_CSS}{_CODE_STYLE.get_style_defs('.code')}</style></head><body>"
        '<div class="toolbar"><span>Tip: in the print window, choose “Save as PDF”.</span>'
        '<button id="print" type="button">Print or save as PDF</button></div>'
        f'<main class="{"full" if full else "summary"}">{body}</main><script>{_SCRIPT}</script></body></html>\n'
    )
