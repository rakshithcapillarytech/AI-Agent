from app.graph.state import IntegrationProfile
from app.kb.loader import files_for_profile, read_files


def test_files_follow_platform_and_config_mode():
    profile = IntegrationProfile(
        platforms=[
            {"platform": "flutter", "config_mode": "firebase"},
            {"platform": "web", "config_mode": "direct"},
        ]
    )
    assert files_for_profile(profile) == [
        "_shared/overview.md",
        "_shared/prerequisites.md",
        "_shared/firebase-setup.md",
        "flutter/firebase.md",
        "web/direct.md",
    ]


def test_firebase_setup_only_when_a_platform_uses_firebase():
    profile = IntegrationProfile(platforms=[{"platform": "android", "config_mode": "direct"}])
    files = files_for_profile(profile)
    assert "_shared/firebase-setup.md" not in files
    assert "android/firebase.md" not in files


def test_platform_without_config_mode_loads_no_platform_file():
    profile = IntegrationProfile(platforms=[{"platform": "ios"}])
    assert files_for_profile(profile) == ["_shared/overview.md", "_shared/prerequisites.md"]


def test_sdk_version_comes_from_front_matter(tmp_path):
    (tmp_path / "android").mkdir()
    (tmp_path / "android" / "direct.md").write_text(
        "---\nsdk_version: 1.2.3\n---\nimplementation(\"com.capillary:hydra-core:{{sdk_version}}\")"
    )
    text = read_files(["android/direct.md"], tmp_path)
    assert 'hydra-core:1.2.3"' in text
    assert "{{sdk_version}}" not in text


def test_read_files_delimits_and_flags_missing(tmp_path):
    (tmp_path / "android").mkdir()
    (tmp_path / "android" / "direct.md").write_text("# Android direct")
    text = read_files(["android/direct.md", "ios/direct.md"], tmp_path)
    assert '<file path="android/direct.md">\n# Android direct\n</file>' in text
    assert '<file path="ios/direct.md" status="missing">' in text
