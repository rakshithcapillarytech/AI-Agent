"""Read the docs site's `llms.txt` page index and the links inside pages."""

import re
from dataclasses import dataclass

_ENTRY = re.compile(r"^(?P<indent>\s*)- \[(?P<title>.+?)\]\((?P<url>https?://[^)\s]+?)\.md\)(?::\s*(?P<desc>.*))?$")
_DOC_LINK = re.compile(r"(?:https?://[a-z0-9.\-]+)?/docs/([A-Za-z0-9_\-]+)(?:\.md)?(?:#[^\s)\]]*)?")
_FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_UPDATED = re.compile(r"^updatedAt:\s*(\S+)", re.MULTILINE)


@dataclass(frozen=True)
class IndexEntry:
    depth: int
    title: str
    slug: str
    parent: str | None


def slug_of(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def branch(index_text: str, root_title: str) -> list[IndexEntry]:
    """The pages under the entry titled `root_title`, with their depth and parent. Empty if it isn't there."""
    lines = index_text.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if (m := _ENTRY.match(line)) and m["title"] == root_title), None
    )
    if start is None:
        return []
    root_indent = len(_ENTRY.match(lines[start])["indent"])
    entries: list[IndexEntry] = []
    stack: list[tuple[int, str]] = []  # (indent, slug)
    for line in lines[start:]:
        m = _ENTRY.match(line)
        if not m:
            if line.strip() and entries and not line.startswith(" "):
                break  # a new top-level heading ends the branch
            continue
        indent = len(m["indent"])
        if entries and indent <= root_indent:
            break
        while stack and stack[-1][0] >= indent:
            stack.pop()
        slug = slug_of(m["url"])
        entries.append(IndexEntry(depth=(indent - root_indent) // 2, title=m["title"], slug=slug, parent=stack[-1][1] if stack else None))
        stack.append((indent, slug))
    return entries


def all_slugs(index_text: str) -> set[str]:
    return {slug_of(m["url"]) for line in index_text.splitlines() if (m := _ENTRY.match(line))}


def updated_at(page_text: str) -> str | None:
    front = _FRONT.match(page_text)
    found = _UPDATED.search(front.group(1)) if front else None
    return found.group(1) if found else None


def linked_slugs(page_text: str) -> set[str]:
    """Slugs of other docs pages this page links to."""
    return {m.group(1) for m in _DOC_LINK.finditer(page_text)}
