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
        "_shared/troubleshooting.md",
    ]


def test_firebase_setup_only_when_a_platform_uses_firebase():
    profile = IntegrationProfile(platforms=[{"platform": "android", "config_mode": "direct"}])
    files = files_for_profile(profile)
    assert "_shared/firebase-setup.md" not in files
    assert "android/firebase.md" not in files


def test_platform_without_config_mode_loads_no_platform_file():
    profile = IntegrationProfile(platforms=[{"platform": "ios"}])
    assert files_for_profile(profile) == [
        "_shared/overview.md",
        "_shared/prerequisites.md",
        "_shared/troubleshooting.md",
    ]


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


def _push_profile(*apps: str, modules=("core", "push")):
    platforms = [dict(zip(("platform", "config_mode"), a.split("/"))) for a in apps]
    return IntegrationProfile(platforms=platforms, modules=list(modules))


def test_push_file_loads_for_push_on_a_mobile_app():
    files = files_for_profile(_push_profile("flutter/firebase"))
    assert files.index("_shared/push.md") > files.index("_shared/firebase-setup.md")
    assert files.index("_shared/push.md") < files.index("flutter/firebase.md")
    assert "_shared/push.md" in files_for_profile(_push_profile("ios/direct"))


def test_push_file_is_skipped_without_the_push_module_or_a_push_capable_app():
    assert "_shared/push.md" not in files_for_profile(_push_profile("flutter/firebase", modules=("core",)))
    assert "_shared/push.md" not in files_for_profile(_push_profile("android/direct"))  # no push in this mode
    assert "_shared/push.md" not in files_for_profile(_push_profile("web/firebase"))  # web push isn't covered


def test_firebase_setup_for_flutter_direct_and_web_direct_with_push():
    assert "_shared/firebase-setup.md" in files_for_profile(_push_profile("flutter/direct", modules=("core",)))
    assert "_shared/firebase-setup.md" in files_for_profile(_push_profile("web/direct"))
    assert "_shared/firebase-setup.md" not in files_for_profile(_push_profile("web/direct", modules=("core",)))
