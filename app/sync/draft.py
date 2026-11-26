"""Optional: an AI model drafts suggested guide edits for the pages that changed. Nothing is applied.

The output is a Markdown file of suggestions for a reviewer (`DRAFT.md` next to the snapshot). It never edits a guide:
people read the diff, decide, edit the guides and run the checks. With no API key this step is simply skipped.
"""

from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel

from app.graph.messages import message_text
from app.sync.diff import page_diff
from app.sync.impact import changed_pages, impact_of, store_for
from app.sync.models import load_config

MAX_PAGE_CHARS = 12_000

PROMPT = """You maintain integration guides for Capillary's Hydra SDK. An official docs page changed after a person last \
reviewed our guides. Suggest what to update in OUR guides.

Rules: use only the page text below; copy new facts exactly (names, versions, values) as short quotes; never invent \
anything; if you can't tell what our guide says, write "check". If the change doesn't affect an integration, say so \
in one line.

Page: {title} ({slug}), updated {old} -> {new}
Our guides built from this page: {guides}
Also built from those guides: FAQ items {faq}; step texts for {platforms}

{body}

Answer in Markdown with one bullet per edit: **guide file > section**: what to change, the exact new text from the page \
(in quotes), and "SME to confirm" if the page is ambiguous or contradicts an internal source."""


def _body(store, slug: str) -> str:
    diff = page_diff(store, slug, context=3, max_lines=200)
    if diff:
        return "What changed (unified diff, reviewed -> current):\n\n" + "\n".join(diff)
    page = store.read_page(slug) or ""
    return "Current page text (no earlier copy to diff against):\n\n" + page[:MAX_PAGE_CHARS]


def draft_proposals(kb_dir: Path, model: BaseChatModel, max_pages: int = 12) -> Path | None:
    config = load_config(kb_dir)
    store = store_for(config, kb_dir)
    manifest = store.load()
    changed = changed_pages(manifest)[:max_pages]
    if not changed:
        return None
    out = [
        "# Suggested guide edits (AI draft, unreviewed)",
        "",
        "These are suggestions only. Check each against the page, edit the guides yourself, then run the tests.",
        "",
    ]
    for slug in changed:
        rec = manifest.pages[slug]
        impact = impact_of(config, manifest, kb_dir, [slug])
        prompt = PROMPT.format(
            title=rec.title or slug,
            slug=slug,
            old=rec.reviewed_updated_at or "?",
            new=rec.updated_at or "?",
            guides=", ".join(impact["guides"]) or "none",
            faq=", ".join(impact["faq_items"]) or "none",
            platforms=", ".join(impact["platforms"]) or "none",
            body=_body(store, slug),
        )
        answer = message_text(model.invoke(prompt).content)
        out += [f"## {rec.title or slug} (`{slug}`)", "", answer.strip(), ""]
    path = store.root / "DRAFT.md"
    path.write_text("\n".join(out), encoding="utf-8")
    return path
