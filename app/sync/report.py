"""The reviewer's report: what changed online, what may be wrong in our guides, what to do next."""

from pathlib import Path

from app.sync.anchors import check_anchors, failing
from app.sync.diff import page_diff
from app.sync.impact import changed_pages, impact_of, store_for, unmapped_pages
from app.sync.models import load_config


def build_report(kb_dir: Path) -> str:
    config = load_config(kb_dir)
    store = store_for(config, kb_dir)
    manifest = store.load()
    changed = changed_pages(manifest)
    bad = failing(check_anchors(kb_dir, store))
    last = store.read_json("last-run.json") or {}
    out = [
        "# Online docs: what needs a review",
        "",
        (
            f"Source: {config.base_url} (branch “{config.root_title}”). Snapshot taken {manifest.synced_at:%Y-%m-%d %H:%M} UTC; "
            f"{len([p for p in manifest.pages.values() if not p.removed])} pages mirrored."
        ),
        "",
    ]
    if last.get("failed"):
        out += ["## Fetch problems", "", "The old snapshot was kept for these:", ""]
        out += [f"- `{slug}`: {why}" for slug, why in last["failed"].items()] + [""]
    out += ["## Summary", ""]
    out += [
        f"- Pages changed since the last review: **{len(changed)}**",
        f"- Key facts failing: **{len(bad)}**",
        f"- New pages no guide uses: **{len(unmapped_pages(config, manifest))}**",
        f"- Removed pages: **{len([p for p in manifest.pages.values() if p.removed])}**",
        "",
    ]
    if bad:
        out += ["## Key facts that no longer match", ""]
        for r in bad:
            if r.online is not True:
                out.append(f"- **{r.anchor.fact}**: the text `{r.anchor.text}` is no longer on `{r.anchor.page}`. Guides: {', '.join(r.anchor.used_in)}.")
            else:
                missing = ", ".join(g for g, ok in r.guides.items() if not ok)
                out.append(f"- **{r.anchor.fact}**: missing from {missing} (the page still says `{r.anchor.text}`).")
        out.append("")
    if changed:
        out += ["## Changed pages", ""]
        for slug in changed:
            rec = manifest.pages[slug]
            impact = impact_of(config, manifest, kb_dir, [slug])
            out += [
                f"### {rec.title or slug} (`{slug}`)",
                "",
                f"- Page updated {rec.reviewed_updated_at or '?'} → {rec.updated_at or '?'} · {rec.url.removesuffix('.md')}",
                f"- Guides built from it: {', '.join(impact['guides']) or 'none'}",
                f"- Also check: FAQ items {', '.join(impact['faq_items']) or 'none'}; {', '.join(impact['step_summaries']) or 'no step texts'}; requirements for {', '.join(impact['platforms']) or 'none'}",
                "",
            ]
            diff = page_diff(store, slug)
            if diff:
                out += ["```diff", *diff, "```", ""]
            else:
                out += ["_No earlier copy was kept to diff against; compare with the page in git history._", ""]
    unmapped = unmapped_pages(config, manifest)
    if unmapped:
        out += ["## Pages no guide is built from", "", "Decide whether a guide needs them, then add them to `sources.yaml`:", ""]
        out += [f"- `{s}`: {manifest.pages[s].title}" for s in unmapped] + [""]
    removed = sorted(s for s, p in manifest.pages.items() if p.removed)
    if removed:
        out += ["## Pages that disappeared from the site", ""] + [f"- `{s}`" for s in removed] + [""]
    out += [
        "## When you've updated the guides",
        "",
        "1. Edit the guides, then the files built from them (requirements, FAQ, step texts) and run the tests and `kb lint`.",
        "2. `python -m app.sync accept --all` (or `accept <slug>`) marks the pages as reviewed.",
        "",
    ]
    return "\n".join(out)


def write_report(kb_dir: Path) -> Path:
    config = load_config(kb_dir)
    path = store_for(config, kb_dir).root / "CHANGES.md"
    path.write_text(build_report(kb_dir), encoding="utf-8")
    return path
