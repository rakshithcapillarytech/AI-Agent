import re
from datetime import date

import pytest

from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.kb.guide import GuideNotReady, _demote_headings, build_guide, guide_filename

KB_DIR = get_settings().knowledge_base_dir


def _profile(**overrides) -> IntegrationProfile:
    return IntegrationProfile.model_validate(
        {
            "company": "Demo Retail",
            "platforms": [{"platform": "flutter", "config_mode": "firebase"}],
            "modules": ["core", "push", "gamification"],
            "environment": "uat",
            "region": "IN",
            "customer_id_type": "mobile",
            **overrides,
        }
    )


def _outside_fences(markdown: str) -> list[str]:
    lines, in_fence = [], False
    for line in markdown.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        elif not in_fence:
            lines.append(line)
    return lines


def test_flutter_firebase_guide_contains_only_the_right_knowledge():
    guide = build_guide(_profile(), KB_DIR, today=date(2026, 10, 22))
    assert guide.startswith("# Hydra SDK integration guide: Demo Retail")
    assert "| Apps | Flutter with Firebase |" in guide
    assert "For the AI assistant reading this file" in guide
    assert "HydraInitializer.initialize()" in guide            # flutter/firebase.md
    assert "## Firebase setup (Firebase console" in guide     # _shared/firebase-setup.md
    assert "Account Linking Identifier" in guide              # _shared/prerequisites.md
    assert "hydra-sdk-android-maven" in guide                 # shared prerequisites table
    assert "HydraConfig.Builder" not in guide                 # android/direct.md isn't included


def test_guide_is_clean_markdown():
    guide = build_guide(_profile(), KB_DIR)
    assert "{{sdk_version}}" not in guide                     # versions are filled in
    assert "review_status:" not in guide                      # front-matter is stripped
    body = _outside_fences(guide)
    assert [line for line in body if line.startswith("# ")] == [body[0]]  # one top-level title


def test_direct_only_profile_skips_firebase_setup():
    guide = build_guide(_profile(platforms=[{"platform": "android", "config_mode": "direct"}]), KB_DIR)
    assert "HydraConfig.Builder" in guide
    assert "## Firebase setup (Firebase console" not in guide


def test_not_ready_until_every_app_has_a_config_mode():
    with pytest.raises(GuideNotReady):
        build_guide(_profile(platforms=[{"platform": "web"}]), KB_DIR)


def test_headings_in_code_fences_are_left_alone():
    text = "# Title\n```properties\n# a comment\n```\n## Section"
    assert _demote_headings(text) == "## Title\n```properties\n# a comment\n```\n### Section"


def test_filename_is_safe_and_descriptive():
    name = guide_filename(_profile(company="Demo Retail & Co."))
    assert name == "hydra-integration-guide-demo-retail-co-flutter.md"
    assert re.fullmatch(r"[a-z0-9.-]+", name)
