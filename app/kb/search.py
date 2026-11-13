"""Keyword search over the knowledge base (an authoring and review tool, PLAN.md §2.3).

Pure Python and in memory: the whole corpus is ~35k tokens, so there is no index to maintain.
It indexes every platform and shared file by section, plus approved issue files, which rank
first. Scoring is TF-IDF over words (camelCase identifiers also split into their parts) with a
bonus for heading hits and for the exact phrase. A `BaseRetriever` wrapper for vector search
(stage C) can sit beside it later.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import frontmatter

from app.kb.sections import split_sections

SKIP_DIRS = {"_template", "source", "inbox"}
SKIP_FILES = {"README.md", "CHANGELOG.md", "REVIEW.md"}
STOPWORDS = frozenset(
    ["a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "in", "on", "for", "and", "or", "it", "its", "my", "we", "our", "i", "you", "how", "do", "does", "can", "what", "why", "with", "this", "that", "at", "as", "by", "from", "not", "no"]
)
ISSUE_BOOST = 1.5
HEADING_WEIGHT = 3.0
PHRASE_BONUS = 10.0
SNIPPET_CHARS = 700


def tokens(text: str) -> list[str]:
    """Lower-case words; a camelCase word is also split ('setCapToken' → set, cap, token)."""
    out = []
    for word in re.findall(r"[A-Za-z0-9]+", text):
        lower = word.lower()
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|[0-9]+", word)
        out.append(lower)
        if len(parts) > 1:
            out.extend(p.lower() for p in parts)
    return [t for t in out if t not in STOPWORDS and len(t) > 1]


@dataclass(frozen=True)
class Doc:
    file: str
    heading: str
    text: str
    platform: str | None
    config_mode: str | None
    is_issue: bool
    counts: Counter
    heading_tokens: frozenset

    @property
    def citation(self) -> str:
        return f"{self.file} › {self.heading}" if self.heading else self.file


@dataclass(frozen=True)
class Hit:
    doc: Doc
    score: float

    def render(self) -> str:
        text = self.doc.text.strip()
        snippet = text[:SNIPPET_CHARS] + ("…" if len(text) > SNIPPET_CHARS else "")
        return f"- {self.doc.citation}\n  {snippet}"


def _make_doc(file, heading, text, meta, is_issue) -> Doc:
    return Doc(
        file=file,
        heading=heading,
        text=text,
        platform=meta.get("platform"),
        config_mode=meta.get("config_mode"),
        is_issue=is_issue,
        counts=Counter(tokens(f"{heading}\n{text}")),
        heading_tokens=frozenset(tokens(heading)),
    )


class Index:
    def __init__(self, docs: list[Doc]):
        self.docs = docs
        df = Counter(t for d in docs for t in d.counts)
        n = len(docs) or 1
        self._idf = {t: math.log(1 + n / c) for t, c in df.items()}

    def search(self, query: str, *, docs: list[Doc] | None = None, k: int = 4) -> list[Hit]:
        wanted = list(dict.fromkeys(tokens(query)))
        if not wanted:
            return []
        phrase = " ".join(query.lower().split())
        hits = []
        for doc in self.docs if docs is None else docs:
            matched = [t for t in wanted if t in doc.counts]
            exact = len(phrase) > 8 and phrase in " ".join(doc.text.lower().split())
            if not exact and len(matched) < max(1, math.ceil(0.4 * len(wanted))):
                continue
            score = sum(
                self._idf[t] * (1 + math.log(doc.counts[t]))
                + (HEADING_WEIGHT * self._idf[t] if t in doc.heading_tokens else 0)
                for t in matched
            )
            score += PHRASE_BONUS if exact else 0
            hits.append(Hit(doc, score * (ISSUE_BOOST if doc.is_issue else 1)))
        return sorted(hits, key=lambda h: -h.score)[:k]


@lru_cache
def _build(kb_dir: Path) -> Index:
    docs: list[Doc] = []
    for path in sorted(kb_dir.rglob("*.md")):
        rel = path.relative_to(kb_dir)
        if rel.parts[0] in SKIP_DIRS or path.name in SKIP_FILES:
            continue
        post = frontmatter.load(path)
        if rel.parts[0] == "issues":
            if post.metadata.get("status") != "approved":
                continue  # drafts wait for SME approval before the agent can use them
            meta = post.metadata
            heading = str(meta.get("error_signature") or path.stem)
            parts = [meta.get("root_cause"), meta.get("fix"), post.content]
            docs.append(_make_doc(rel.as_posix(), heading, "\n".join(str(p) for p in parts if p), meta, True))
            continue
        for section in split_sections(post.content):
            if section.body:
                docs.append(_make_doc(rel.as_posix(), section.heading, section.body, post.metadata, False))
    return Index(docs)


def clear_index() -> None:
    """Forget the cached index, e.g. after an issue file is published."""
    _build.cache_clear()


def load_index(kb_dir: Path) -> Index:
    return _build(kb_dir)


def search(
    kb_dir: Path,
    query: str,
    *,
    files: list[str] | None = None,
    apps: set[tuple[str, str | None]] | None = None,
    issues_only: bool = False,
    k: int = 4,
) -> list[Hit]:
    """Search the knowledge.

    files: restrict documentation to these knowledge files (None: every file).
    apps:  (platform, config_mode) pairs; restricts issues to the client's own apps.
    """
    index = load_index(kb_dir)

    def allowed(doc: Doc) -> bool:
        if doc.is_issue:
            return apps is None or any(
                doc.platform == p and doc.config_mode in (None, m) for p, m in apps
            )
        return not issues_only and (files is None or doc.file in files)

    return index.search(query, docs=[d for d in index.docs if allowed(d)], k=k)
