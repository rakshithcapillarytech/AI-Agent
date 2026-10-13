"""Graph state and the domain models stored in it.

State values are kept as plain dicts (model_dump) so the Postgres checkpointer serialises them
without custom type registration; validate with the Pydantic models when reading.
"""

from typing import Literal

from langgraph.graph import MessagesState
from pydantic import BaseModel

Phase = Literal["discovery", "prerequisites", "integration", "verification", "done"]
Platform = Literal["android", "ios", "react-native", "flutter", "web"]
ConfigMode = Literal["firebase", "direct"]
Module = Literal[
    "core", "push", "inapp", "inbox_api", "inbox_ui", "visitor", "gamification", "multi_account"
]


class PlatformDetails(BaseModel):
    platform: Platform
    config_mode: ConfigMode | None = None
    language: str | None = None  # e.g. kotlin, java, swift-uikit, swiftui, objc, typescript
    framework_version: str | None = None
    package_manager: str | None = None  # e.g. spm, cocoapods, gradle, npm, yarn, pnpm, bun
    notes: str | None = None  # custom Application class, customised AppDelegate, CSP, sub-path…


class IntegrationProfile(BaseModel):
    company: str | None = None
    platforms: list[PlatformDetails] = []
    modules: list[Module] = []
    environment: Literal["uat", "production"] | None = None
    region: Literal["IN", "US", "ME"] | None = None
    customer_id_type: Literal["mobile", "email", "externalId", "InTouchUserId", "FCMToken"] | None = None
    contacts: list[str] = []
    go_live_date: str | None = None
    confirmed: bool = False

    def missing_required(self) -> list[str]:
        missing = []
        if not self.platforms:
            missing.append("platforms")
        missing += [
            f"config_mode for {p.platform}" for p in self.platforms if p.config_mode is None
        ]
        if not self.modules:
            missing.append("modules")
        for field in ("environment", "region", "customer_id_type"):
            if getattr(self, field) is None:
                missing.append(field)
        return missing


class PrereqItem(BaseModel):
    id: str
    title: str
    owner: Literal["client", "capillary"]
    status: Literal["pending", "provided", "verified", "not_applicable"] = "pending"
    blocking: bool = True
    value: str | None = None


class OnboardingState(MessagesState):
    phase: Phase
    profile: dict  # IntegrationProfile.model_dump()
    prerequisites: list[dict]  # PrereqItem.model_dump() each
    loaded_files: list[str]  # knowledge_base-relative paths loaded into the prompt
    plan_steps: list[str]
    current_step: int
