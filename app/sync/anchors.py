"""Key facts, checked against the online pages and against our guides.

knowledge_base/anchors.yaml lists facts that would break an integration if they changed (a version, a package name, a
repository, a minimum, a method option). Each names the online page and the exact text that states it, and the guides
that rely on it. `check_anchors` reports two kinds of failure:
  - online: the text is no longer on the page, so Capillary changed it and the guides may now be wrong;
  - guide: a guide no longer carries the fact, so the guide drifted from what the page says.
"""

from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
import yaml
from pydantic import BaseModel

from app.sync.store import SnapshotStore

ANCHORS_FILE = "anchors.yaml"


class Anchor(BaseModel):
    id: str
    fact: str
    page: str  # slug of the online page that states it
    text: str  # exact text that must appear on that page
    used_in: list[str]  # guide files that must carry the fact
    guide_text: str | None = None  # what the guides contain, when it differs from the page's wording


class Anchors(BaseModel):
    anchors: list[Anchor]


@dataclass
class AnchorResult:
    anchor: Anchor
    online: bool | None  # None = the page isn't in the snapshot
    guides: dict[str, bool] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.online is True and all(self.guides.values())


def load_anchors(kb_dir: Path) -> list[Anchor]:
    path = kb_dir / ANCHORS_FILE
    if not path.is_file():
        return []
    anchors = Anchors.model_validate(yaml.safe_load(path.read_text(encoding="utf-8"))).anchors
    ids = [a.id for a in anchors]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate ids in {ANCHORS_FILE}")
    return anchors


def _guide_text(kb_dir: Path, rel: str) -> str:
    path = kb_dir / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def check_anchors(kb_dir: Path, store: SnapshotStore) -> list[AnchorResult]:
    results = []
    for anchor in load_anchors(kb_dir):
        page = store.read_page(anchor.page)
        online = None if page is None else anchor.text in page
        guides = {rel: (anchor.guide_text or anchor.text) in _guide_text(kb_dir, rel) for rel in anchor.used_in}
        results.append(AnchorResult(anchor, online, guides))
    return results


def failing(results: list[AnchorResult]) -> list[AnchorResult]:
    return [r for r in results if not r.ok]


def guide_front_matter_version(kb_dir: Path, rel: str) -> str | None:
    """The `sdk_version` a guide declares (handy for reports)."""
    path = kb_dir / rel
    if not path.is_file():
        return None
    value = frontmatter.loads(path.read_text(encoding="utf-8")).metadata.get("sdk_version")
    return None if value is None else str(value)
