"""Spot value-only changes in an online page, and apply them as text substitutions.

A page that just moved from `1.10.6` to `1.10.7` has changed in a way a script can follow safely. This module:
  - `derive` finds the substitution (old value -> new value) behind one anchored fact;
  - `apply_text` applies substitutions to text, only on whole values;
  - `explained` says whether a page's whole change is nothing but those substitutions (plus its `updatedAt`).
Only values that contain a digit qualify (versions, minimums). Names and prose changes are left to a person.
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

_TOKEN_CHARS = re.compile(r"[A-Za-z0-9._\-+@/]")
_UPDATED = re.compile(r"^updatedAt:.*$", re.MULTILINE)


@dataclass(frozen=True)
class Substitution:
    old: str
    new: str


def qualifies(sub: Substitution, min_length: int = 3) -> bool:
    """A value we may change without a person: no spaces, at least one digit, not trivially short."""
    return (
        sub.old != sub.new
        and len(sub.old) >= min_length
        and not re.search(r"\s", sub.old + sub.new)
        and bool(re.search(r"\d", sub.old))
        and bool(re.search(r"\d", sub.new))
    )


def _is_token(char: str) -> bool:
    return bool(_TOKEN_CHARS.fullmatch(char))


def _span(old_line: str, new_line: str, start: int, end: int) -> Substitution | None:
    ops = [op for op in SequenceMatcher(None, old_line, new_line, autojunk=False).get_opcodes() if op[0] != "equal"]
    inside = [op for op in ops if op[1] < end and (op[2] > start or op[1] == start)]
    if len(inside) != 1:
        return None
    _, i1, i2, j1, j2 = inside[0]
    while i1 > 0 and j1 > 0 and old_line[i1 - 1] == new_line[j1 - 1] and _is_token(old_line[i1 - 1]):
        i1, j1 = i1 - 1, j1 - 1
    while i2 < len(old_line) and j2 < len(new_line) and old_line[i2] == new_line[j2] and _is_token(old_line[i2]):
        i2, j2 = i2 + 1, j2 + 1
    return Substitution(old_line[i1:i2], new_line[j1:j2])


def derive(old_page: str, new_page: str, anchor_text: str) -> Substitution | None:
    """The substitution that turns `anchor_text` (on the old page) into what the new page says, if it is a clean
    one-value change on a line that was replaced in place. None when the fact is still there, or the change isn't that."""
    if anchor_text not in old_page or anchor_text in new_page:
        return None
    old_lines, new_lines = old_page.splitlines(), new_page.splitlines()
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag != "replace" or i2 - i1 != j2 - j1:
            continue
        for k in range(i2 - i1):
            position = old_lines[i1 + k].find(anchor_text)
            if position >= 0:
                return _span(old_lines[i1 + k], new_lines[j1 + k], position, position + len(anchor_text))
    return None


def _pattern(old: str) -> re.Pattern[str]:
    # a whole value: not part of a longer number, word or dotted name (so 1.10.6 doesn't match inside 1.10.60 or 11.10.6)
    return re.compile(r"(?<![\w.])" + re.escape(old) + r"(?!\w|\.\d)")


def apply_text(text: str, subs: list[Substitution]) -> str:
    for sub in subs:
        text = _pattern(sub.old).sub(sub.new, text)
    return text


def count_matches(text: str, sub: Substitution) -> int:
    return len(_pattern(sub.old).findall(text))


def explained(old_page: str, new_page: str, subs: list[Substitution]) -> bool:
    """True when applying the substitutions to the old page gives exactly the new page (ignoring `updatedAt`)."""
    if not subs:
        return False
    strip = lambda text: _UPDATED.sub("", text)
    return strip(apply_text(old_page, subs)) == strip(new_page)
