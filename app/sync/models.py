"""Data shapes for the docs sync: its configuration, the snapshot manifest and a run's result."""

from datetime import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

SOURCES_FILE = "sources.yaml"
SNAPSHOT_SUBDIR = "source"  # knowledge_base/source/<source name>/


class FollowConfig(BaseModel):
    slug_patterns: list[str] = Field(default_factory=list)
    max_extra_pages: int = 40


class FetchConfig(BaseModel):
    delay_seconds: float = 0.8
    timeout_seconds: float = 30
    max_retries: int = 4
    user_agent: str = "capillary-hydra-copilot-docs-sync/1.0"


class AutoUpdateConfig(BaseModel):
    """What an automatic value update may touch. Paths are relative to the repository root."""

    roots: list[str] = Field(default_factory=lambda: ["knowledge_base", "evals"])
    extensions: list[str] = Field(default_factory=lambda: [".md", ".yaml"])
    exclude: list[str] = Field(
        default_factory=lambda: [
            "knowledge_base/source",
            "knowledge_base/audits",
            "knowledge_base/CHANGELOG.md",
            "knowledge_base/REVIEW.md",
            "knowledge_base/README.md",
            "knowledge_base/anchors.yaml",
            "evals/results",
        ]
    )
    min_value_length: int = 3


class SyncConfig(BaseModel):
    source: str
    base_url: str
    index_path: str = "/llms.txt"
    root_title: str
    follow: FollowConfig = Field(default_factory=FollowConfig)
    fetch: FetchConfig = Field(default_factory=FetchConfig)
    auto_update: AutoUpdateConfig = Field(default_factory=AutoUpdateConfig)
    guides: dict[str, list[str]] = Field(default_factory=dict)

    def pages_for_guide(self, guide: str) -> list[str]:
        return self.guides.get(guide, [])

    def guides_for_page(self, slug: str) -> list[str]:
        return [g for g, slugs in self.guides.items() if slug in slugs]


def load_config(kb_dir: Path) -> SyncConfig:
    return SyncConfig.model_validate(yaml.safe_load((kb_dir / SOURCES_FILE).read_text(encoding="utf-8")))


class PageRecord(BaseModel):
    """One mirrored page. `reviewed_sha256` is the version a human last accepted."""

    slug: str
    url: str
    title: str = ""
    parent: str | None = None
    found_via: str = "index"  # "index", or "link:<slug>" for pages the index leaves out
    updated_at: str | None = None  # the page's own `updatedAt`
    sha256: str
    size: int
    fetched_at: datetime
    reviewed_sha256: str | None = None
    reviewed_updated_at: str | None = None
    removed: bool = False  # no longer in the index and not linked from any page

    @property
    def changed_since_review(self) -> bool:
        return self.reviewed_sha256 is not None and self.reviewed_sha256 != self.sha256 and not self.removed


class Manifest(BaseModel):
    source: str
    base_url: str
    synced_at: datetime | None = None
    pages: dict[str, PageRecord] = Field(default_factory=dict)


class SyncResult(BaseModel):
    started_at: datetime
    finished_at: datetime | None = None
    fetched: int = 0
    unchanged: int = 0
    added: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    followed: list[str] = Field(default_factory=list)  # pages found through links, not the index
    failed: dict[str, str] = Field(default_factory=dict)  # slug -> reason; the old snapshot is kept
    index_ok: bool = True

    @property
    def ok(self) -> bool:
        return self.index_ok and not self.failed
