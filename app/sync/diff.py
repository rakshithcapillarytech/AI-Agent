"""What changed in a page since a human last reviewed it."""

import difflib

from app.sync.store import SnapshotStore


def page_diff(store: SnapshotStore, slug: str, context: int = 2, max_lines: int = 120) -> list[str] | None:
    """A unified diff from the reviewed version to the current one, or None when no reviewed copy is kept
    (the page was never reviewed, or hasn't changed)."""
    old, new = store.read_reviewed(slug), store.read_page(slug)
    if old is None or new is None:
        return None
    lines = list(
        difflib.unified_diff(
            old.splitlines(), new.splitlines(), fromfile=f"{slug} (reviewed)", tofile=f"{slug} (current)", n=context, lineterm=""
        )
    )
    if len(lines) > max_lines:
        lines = [*lines[:max_lines], f"... {len(lines) - max_lines} more diff lines"]
    return lines
