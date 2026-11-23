"""What a client needs before starting, for the portal's Prerequisites tab.

Unlike the checklist in a session (app/rules/prereq_engine.py, tied to one client's profile), this is a
reference view: pick a platform, a config mode and the modules, and get the keys Capillary sends, what the
client sends Capillary, accounts and access to set up, minimum versions, and the computer tools needed.
It reuses the rules in `prerequisites.yaml`; versions come from `requirements.yaml`. No LLM, no secrets.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from app.graph.state import ConfigMode, IntegrationProfile, Module, Platform, PlatformDetails
from app.rules.prereq_engine import PrereqRule, load_rules

REQUIREMENTS_FILE = "requirements.yaml"
CUSTOMER_ID = "the identifier your customers sign in with"


class ReqItem(BaseModel):
    label: str
    value: str
    note: str | None = None
    modes: list[ConfigMode] | None = None
    modules: list[Module] | None = None
    check: str | None = None  # text that must appear in the guide (tests/test_requirements.py)
    general: bool = False  # common platform knowledge, not stated in Capillary's docs


class PlatformRequirements(BaseModel):
    versions: list[ReqItem] = Field(default_factory=list)
    computer: list[ReqItem] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class Requirements(BaseModel):
    platforms: dict[Platform, PlatformRequirements]
    computer_gap: str


@lru_cache
def load_requirements(kb_dir: Path) -> Requirements:
    return Requirements.model_validate(yaml.safe_load((kb_dir / REQUIREMENTS_FILE).read_text(encoding="utf-8")))


def front_matter_value(kb_dir: Path, platform: str, mode: str, key: str) -> str | None:
    """A top-level value from a platform guide's front matter, e.g. `sdk_version`."""
    text = (kb_dir / platform / f"{mode}.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    value = (yaml.safe_load(parts[1]) or {}).get(key)
    return None if value is None else str(value)


def _applies(item: ReqItem, mode: str, modules: set[str]) -> bool:
    return (item.modes is None or mode in item.modes) and (item.modules is None or bool(modules & set(item.modules)))


def _version_row(item: ReqItem, sdk_version: str | None) -> dict:
    value = item.value.replace("{sdk_version}", sdk_version or "the version your Capillary contact gives you")
    return {"label": item.label, "value": value, "note": item.note, "general": item.general}


def _needed_for(rule: PrereqRule, profile: IntegrationProfile) -> list[str]:
    """The modules that make a rule necessary, or [] when it applies whatever modules are chosen."""
    matching = [c for c in rule.when if c.matches(profile)]
    if not matching or any(c.modules is None for c in matching):
        return []
    return sorted({m for c in matching for m in (c.modules or []) if m in profile.modules})


def _prereq_row(rule: PrereqRule, profile: IntegrationProfile) -> dict:
    return {
        "id": rule.id,
        "title": rule.title.replace("{customer_id_type}", CUSTOMER_ID),
        "how": rule.short or rule.how,
        "required": rule.blocking,
        "needed_for": _needed_for(rule, profile),
        "source": rule.source,
    }


Section = Literal["from_capillary", "give_capillary", "setup"]


def build_prerequisites(
    kb_dir: Path, platform: Platform, mode: ConfigMode, modules: list[Module]
) -> dict:
    """Everything the Prerequisites tab shows for one platform, config mode and set of modules."""
    modules = list(dict.fromkeys(["core", *modules]))
    profile = IntegrationProfile(platforms=[PlatformDetails(platform=platform, config_mode=mode)], modules=modules)
    sections: dict[Section, list[dict]] = {"from_capillary": [], "give_capillary": [], "setup": []}
    for rule in load_rules(kb_dir).items:
        if not rule.applies(profile):
            continue
        key: Section = "from_capillary" if rule.owner == "capillary" else "give_capillary" if rule.group else "setup"
        sections[key].append(_prereq_row(rule, profile))

    reqs = load_requirements(kb_dir).platforms[platform]
    sdk_version = front_matter_value(kb_dir, platform, mode, "sdk_version")
    chosen = set(modules)
    return {
        "platform": platform,
        "config_mode": mode,
        "modules": modules,
        **sections,
        "versions": [_version_row(i, sdk_version) for i in reqs.versions if _applies(i, mode, chosen)],
        "computer": [_version_row(i, sdk_version) for i in reqs.computer if _applies(i, mode, chosen)],
        "computer_gap": load_requirements(kb_dir).computer_gap,
        "gaps": reqs.gaps,
    }
