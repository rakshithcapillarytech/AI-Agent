"""Split a knowledge Markdown file into sections by heading (fence-aware).

Shared by keyword search and the integration-step planner so both see the same structure.
"""

import re
from dataclasses import dataclass

_HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Section:
    path: tuple[str, ...]  # headings below the file title, e.g. ("Steps", "3. Add the SDK")
    body: str

    @property
    def heading(self) -> str:
        return " › ".join(self.path)


def split_sections(text: str) -> list[Section]:
    """One Section per heading, holding the text up to the next heading of any level.

    The first `# Title` heading is the file title and isn't part of any path.
    """
    sections: list[Section] = []
    stack: list[tuple[int, str]] = []
    body: list[str] = []
    in_fence = False
    current: tuple[str, ...] | None = None

    def flush():
        if current is not None:
            sections.append(Section(current, "\n".join(body).strip()))

    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
        match = None if in_fence else _HEADING.match(line)
        if match:
            flush()
            level, title = len(match.group(1)), match.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            current = tuple(t for lv, t in stack if lv > 1)
            body = []
            if not current:  # the file title
                current = None
        else:
            body.append(line)
    flush()
    return sections
