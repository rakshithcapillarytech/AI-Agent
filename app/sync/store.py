"""The on-disk snapshot of the online docs: knowledge_base/source/<source>/.

    manifest.json     one record per page (url, hash, page's own updatedAt, what a human last reviewed)
    pages/<slug>.md   the page as fetched
    reviewed/<slug>.md  the version a human last accepted, kept only for pages that changed since (so reviewers can diff)
    CHANGES.md        the latest report for reviewers (written by `python -m app.sync run`)
    last-run.json     the latest run's result
"""

import hashlib
import json
from pathlib import Path

from app.sync.models import SNAPSHOT_SUBDIR, Manifest, PageRecord


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SnapshotStore:
    def __init__(self, kb_dir: Path, source: str, base_url: str = "") -> None:
        self.root = kb_dir / SNAPSHOT_SUBDIR / source
        self.source, self.base_url = source, base_url
        self.pages_dir = self.root / "pages"
        self.reviewed_dir = self.root / "reviewed"
        self.manifest_path = self.root / "manifest.json"

    # ── manifest ──────────────────────────────────────────────────────────────────────────────
    def load(self) -> Manifest:
        if not self.manifest_path.is_file():
            return Manifest(source=self.source, base_url=self.base_url)
        return Manifest.model_validate_json(self.manifest_path.read_text(encoding="utf-8"))

    def save(self, manifest: Manifest) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        ordered = Manifest(**{**manifest.model_dump(), "pages": dict(sorted(manifest.pages.items()))})
        self.manifest_path.write_text(ordered.model_dump_json(indent=1) + "\n", encoding="utf-8")

    # ── page text ─────────────────────────────────────────────────────────────────────────────
    def page_path(self, slug: str) -> Path:
        return self.pages_dir / f"{slug}.md"

    def read_page(self, slug: str) -> str | None:
        path = self.page_path(slug)
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def read_reviewed(self, slug: str) -> str | None:
        path = self.reviewed_dir / f"{slug}.md"
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def write_page(self, record: PageRecord, text: str, previous: PageRecord | None) -> None:
        """Store a page. If a reviewed version is about to be overwritten, keep a copy of it for diffing."""
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        old = self.read_page(record.slug)
        if old is not None and previous and previous.reviewed_sha256 == previous.sha256 and previous.sha256 != record.sha256:
            self.reviewed_dir.mkdir(parents=True, exist_ok=True)
            (self.reviewed_dir / f"{record.slug}.md").write_text(old, encoding="utf-8")
        self.page_path(record.slug).write_text(text, encoding="utf-8")

    def accept(self, manifest: Manifest, slugs: list[str] | None = None) -> list[str]:
        """Mark pages as reviewed (their current version becomes the baseline). Returns the slugs accepted."""
        done = []
        for slug, record in manifest.pages.items():
            if slugs is not None and slug not in slugs:
                continue
            if record.reviewed_sha256 != record.sha256 or record.reviewed_updated_at != record.updated_at:
                record.reviewed_sha256, record.reviewed_updated_at = record.sha256, record.updated_at
                done.append(slug)
            (self.reviewed_dir / f"{slug}.md").unlink(missing_ok=True)
        return done

    def write_json(self, name: str, data: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / name).write_text(json.dumps(data, indent=1, default=str) + "\n", encoding="utf-8")

    def read_json(self, name: str) -> dict | None:
        path = self.root / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
