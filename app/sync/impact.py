"""From changed pages to the things that may need an update: guides, then what is built from them."""

from pathlib import Path

from app.rules.faq import load_faq
from app.sync.models import Manifest, SyncConfig
from app.sync.store import SnapshotStore


def changed_pages(manifest: Manifest) -> list[str]:
    return sorted(slug for slug, rec in manifest.pages.items() if rec.changed_since_review)


def unmapped_pages(config: SyncConfig, manifest: Manifest) -> list[str]:
    """Mirrored pages that no guide is built from (new pages, or pages we deliberately don't use)."""
    return sorted(slug for slug, rec in manifest.pages.items() if not rec.removed and not config.guides_for_page(slug))


def impact_of(config: SyncConfig, manifest: Manifest, kb_dir: Path, slugs: list[str]) -> dict:
    """Guides touched by these pages, and the FAQ answers, step texts and requirement rows that rest on those guides."""
    guides = sorted({g for slug in slugs for g in config.guides_for_page(slug)})
    platforms = sorted({g.split("/")[0] for g in guides if not g.startswith("_shared/")})
    faq = [
        item.id
        for item in load_faq(kb_dir).items
        if any(e.file in guides for e in item.evidence)
    ]
    return {
        "guides": guides,
        "platforms": platforms,
        "step_summaries": [f"knowledge_base/step_summaries/{p}.yaml" for p in platforms],
        "requirements": [f"knowledge_base/requirements.yaml › {p}" for p in platforms],
        "faq_items": faq,
        "evals": [f"evals/deep/{p}-*.yaml" for p in platforms],
    }


def pages_by_guide(config: SyncConfig, manifest: Manifest, guide: str) -> list[str]:
    """Pages mapped to this guide that changed since review."""
    return [s for s in config.pages_for_guide(guide) if (rec := manifest.pages.get(s)) and rec.changed_since_review]


def store_for(config: SyncConfig, kb_dir: Path) -> SnapshotStore:
    return SnapshotStore(kb_dir, config.source, config.base_url)
