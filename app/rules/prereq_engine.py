"""Deterministic prerequisites: profile → checklist, from knowledge_base/prerequisites.yaml.

The LLM never decides what a client needs; it presents this checklist and records progress on it
(app/tools/prereqs.py). The checklist is rebuilt whenever the profile changes, keeping the status
of items that still apply (PLAN.md §4 ②).
"""

import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from app.graph.state import IntegrationProfile, Module, PrereqItem

RULES_FILE = "prerequisites.yaml"

# Format checks for values the client states. Deliberately loose: they catch pasting the wrong
# thing (a URL, a key, half a fingerprint), not every edge case of the platform rules.
FORMATS = {
    # Android: at least two dot-separated segments, each starting with a letter.
    "android_application_id": re.compile(r"[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+"),
    # iOS: reverse-DNS of letters, digits, hyphens and dots.
    "ios_bundle_id": re.compile(r"[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+"),
    # 32 bytes as colon-separated hex pairs, as printed by the signing report.
    "sha256_fingerprint": re.compile(r"[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){31}"),
}
FORMAT_HINTS = {
    "android_application_id": "a package name such as com.example.app",
    "ios_bundle_id": "a bundle ID such as com.example.app",
    "sha256_fingerprint": "32 colon-separated hex pairs, e.g. AB:CD:…, from the signing report",
}

Format = Literal["android_application_id", "ios_bundle_id", "sha256_fingerprint"]


class Condition(BaseModel):
    """Matches when every given key matches (see the header of prerequisites.yaml)."""

    platforms: list[str] | None = None  # "android" (any mode) or "android/direct"
    modules: list[Module] | None = None

    def matches(self, profile: IntegrationProfile) -> bool:
        if self.platforms is not None:
            apps = {p.platform for p in profile.platforms} | {
                f"{p.platform}/{p.config_mode}" for p in profile.platforms if p.config_mode
            }
            if not apps & set(self.platforms):
                return False
        return self.modules is None or bool(set(profile.modules) & set(self.modules))


class PrereqRule(BaseModel):
    id: str
    title: str
    owner: Literal["client", "capillary"]
    blocking: bool
    how: str
    source: str
    value: bool = False
    format: Format | None = None
    when: list[Condition] = Field(default_factory=list)

    def applies(self, profile: IntegrationProfile) -> bool:
        return not self.when or any(c.matches(profile) for c in self.when)


class RuleSet(BaseModel):
    items: list[PrereqRule]

    def by_id(self) -> dict[str, PrereqRule]:
        return {rule.id: rule for rule in self.items}


@lru_cache
def load_rules(kb_dir: Path) -> RuleSet:
    data = yaml.safe_load((kb_dir / RULES_FILE).read_text(encoding="utf-8"))
    rules = RuleSet.model_validate(data)
    ids = [rule.id for rule in rules.items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate ids in {RULES_FILE}")
    return rules


def build_checklist(
    profile: IntegrationProfile, rules: RuleSet, existing: list[PrereqItem] | None = None
) -> list[PrereqItem]:
    """The checklist for this profile. Items already in `existing` keep their status and value."""
    previous = {item.id: item for item in existing or []}
    checklist = []
    for rule in rules.items:
        if not rule.applies(profile):
            continue
        item = PrereqItem(
            id=rule.id,
            title=rule.title.replace("{customer_id_type}", profile.customer_id_type or "your identifier"),
            owner=rule.owner,
            blocking=rule.blocking,
            how=rule.how,
            source=rule.source,
        )
        if old := previous.get(rule.id):
            item.status, item.value = old.status, old.value
        checklist.append(item)
    return checklist


def check_value(rule: PrereqRule, value: str) -> str | None:
    """An error message if `value` can't be recorded for this rule, else None."""
    if not rule.value:
        return f"'{rule.id}' doesn't take a value. Record only its status; never store keys or tokens."
    if rule.format and not FORMATS[rule.format].fullmatch(value):
        return f"'{value}' doesn't look like {FORMAT_HINTS[rule.format]}. Ask the client to check it."
    return None
