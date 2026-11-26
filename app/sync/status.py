"""What the app can say about how fresh its knowledge is. Everything here is read-only and never raises."""

from pathlib import Path

from app.sync.anchors import check_anchors, failing
from app.sync.impact import changed_pages, pages_by_guide, store_for, unmapped_pages
from app.sync.models import SOURCES_FILE, load_config


def sync_status(kb_dir: Path) -> dict:
    """Overview for the admin screen and the portal footer."""
    try:
        if not (kb_dir / SOURCES_FILE).is_file():
            return {"synced": False, "reason": "no sources.yaml"}
        config = load_config(kb_dir)
        store = store_for(config, kb_dir)
        manifest = store.load()
        if not manifest.pages:
            return {"synced": False, "reason": "no snapshot yet; run `python -m app.sync run`"}
        results = check_anchors(kb_dir, store)
        bad = failing(results)
        changed = changed_pages(manifest)
        return {
            "synced": True,
            "source": config.source,
            "base_url": config.base_url,
            "synced_at": manifest.synced_at.isoformat() if manifest.synced_at else None,
            "pages": len([p for p in manifest.pages.values() if not p.removed]),
            "changed": [
                {
                    "slug": s,
                    "title": manifest.pages[s].title,
                    "url": manifest.pages[s].url.removesuffix(".md"),
                    "updated_at": manifest.pages[s].updated_at,
                    "reviewed_updated_at": manifest.pages[s].reviewed_updated_at,
                    "guides": config.guides_for_page(s),
                    "has_diff": store.read_reviewed(s) is not None,
                }
                for s in changed
            ],
            "removed": sorted(s for s, p in manifest.pages.items() if p.removed),
            "unmapped": unmapped_pages(config, manifest),
            "stale_guides": {g: pages for g in config.guides if (pages := pages_by_guide(config, manifest, g))},
            "anchors": {
                "total": len(results),
                "failing": [
                    {
                        "id": r.anchor.id,
                        "fact": r.anchor.fact,
                        "page": r.anchor.page,
                        "problem": "no longer on the online page" if r.online is not True else "missing from "
                        + ", ".join(g for g, ok in r.guides.items() if not ok),
                    }
                    for r in bad
                ],
            },
            "last_run": store.read_json("last-run.json"),
        }
    except Exception as error:  # noqa: BLE001  # status must never break a page
        return {"synced": False, "reason": f"{type(error).__name__}: {error}"}


def source_notice(kb_dir: Path, guide_files: list[str]) -> list[str]:
    """Lines for the top of a client's guide: when the guides were last checked against Capillary's online docs, and a
    warning if a page they are built from has changed since a person reviewed it. Empty when there is no snapshot."""
    try:
        if not (kb_dir / SOURCES_FILE).is_file():
            return []
        config = load_config(kb_dir)
        manifest = store_for(config, kb_dir).load()
        if not manifest.pages or not manifest.synced_at:
            return []
        stale = sorted({s for g in guide_files for s in pages_by_guide(config, manifest, g)})
        lines = [f"Checked against Capillary's online developer docs on {manifest.synced_at.date().isoformat()}."]
        if stale:
            names = ", ".join(f"`{s}`" for s in stale)
            lines.append(
                f"> ⚠️ These online pages changed after this guide was last reviewed, so some details may be out of date: {names}. "
                "Confirm anything important with your Capillary contact."
            )
        return lines
    except Exception:  # noqa: BLE001  # a freshness note must never break a guide download
        return []
