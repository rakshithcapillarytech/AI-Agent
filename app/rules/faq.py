"""The FAQ tab's questions and answers, from knowledge_base/faq.yaml.

Each answer restates what the guides say and carries `evidence` (a file and a piece of text in it) so tests
can catch an answer that no longer matches its guide. No LLM, no client data.
"""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from app.graph.state import Platform

FAQ_FILE = "faq.yaml"


class Evidence(BaseModel):
    file: str
    text: str


class Category(BaseModel):
    id: str
    label: str


class FaqItem(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    platforms: list[Platform] | None = None  # None = every platform
    evidence: list[Evidence] = Field(min_length=1)


class Faq(BaseModel):
    categories: list[Category]
    items: list[FaqItem]


@lru_cache
def load_faq(kb_dir: Path) -> Faq:
    faq = Faq.model_validate(yaml.safe_load((kb_dir / FAQ_FILE).read_text(encoding="utf-8")))
    ids = [item.id for item in faq.items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate ids in {FAQ_FILE}")
    known = {c.id for c in faq.categories}
    unknown = {item.category for item in faq.items} - known
    if unknown:
        raise ValueError(f"{FAQ_FILE}: unknown categories {sorted(unknown)}")
    return faq


def faq_view(kb_dir: Path) -> dict:
    """What the portal shows: categories and items, with the guides they come from (not the evidence text)."""
    faq = load_faq(kb_dir)
    return {
        "categories": [c.model_dump() for c in faq.categories],
        "items": [
            {
                **item.model_dump(exclude={"evidence"}),
                "sources": list(dict.fromkeys(e.file for e in item.evidence)),
            }
            for item in faq.items
        ],
    }
