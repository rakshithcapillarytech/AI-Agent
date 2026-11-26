import asyncio
from itertools import product
from pathlib import Path

import frontmatter
from fastapi.testclient import TestClient

from app.api.main import app, prerequisites
from app.rules.requirements import build_prerequisites, load_requirements

KB = Path(__file__).parent.parent / "knowledge_base"
PLATFORMS = ["android", "ios", "react-native", "flutter", "web"]
MODES = ["firebase", "direct"]
ALL_MODULES = ["push", "inapp", "inbox_api", "inbox_ui", "visitor", "gamification", "multi_account"]


def ids(rows):
    return {r["id"] for r in rows}


def test_every_requirement_is_written_in_the_guides():
    """Each `check` string must still be in the guide of every mode the item covers (no drift)."""
    problems = []
    for platform, reqs in load_requirements(KB).platforms.items():
        for item in [*reqs.versions, *reqs.computer]:
            assert item.check or item.general, f"{platform}: '{item.label}' needs a check or general: true"
            for mode in item.modes or MODES:
                text = (KB / platform / f"{mode}.md").read_text(encoding="utf-8")
                if item.check and item.check not in text:
                    problems.append(f"{platform}/{mode}: '{item.label}' → {item.check!r}")
        for gap in reqs.gaps:
            assert gap.endswith("."), gap
    assert not problems, "requirements.yaml no longer matches the guides:\n" + "\n".join(problems)


def test_every_platform_and_mode_builds():
    for platform, mode in product(PLATFORMS, MODES):
        view = build_prerequisites(KB, platform, mode, ALL_MODULES)
        assert view["versions"], (platform, mode)
        assert view["computer"], (platform, mode)
        assert view["gaps"], (platform, mode)
        assert "core" in view["modules"]


def test_capillary_keys_follow_the_platform_and_modules():
    android = build_prerequisites(KB, "android", "direct", [])
    assert {"account_id", "base_url", "ssl_public_key", "org_id"} <= ids(android["from_capillary"])
    assert "gamification_key" not in ids(android["from_capillary"])

    with_games = build_prerequisites(KB, "android", "direct", ["gamification"])
    assert {"gamification_key", "gamification_region", "gamification_base_url_native"} <= ids(with_games["from_capillary"])

    web = build_prerequisites(KB, "web", "direct", [])
    assert "ssl_public_key" not in ids(web["from_capillary"])  # mobile only


def test_required_versus_optional_and_what_they_are_needed_for():
    view = build_prerequisites(KB, "flutter", "firebase", ["gamification"])
    rows = {r["id"]: r for r in view["from_capillary"]}
    assert rows["account_id"]["required"] is True and rows["account_id"]["needed_for"] == []
    assert rows["gamification_key"]["needed_for"] == ["gamification"]
    assert rows["gamification_base_url"]["required"] is True  # Flutter: required with key and region
    native = {r["id"]: r for r in build_prerequisites(KB, "android", "direct", ["gamification"])["from_capillary"]}
    assert native["gamification_base_url_native"]["required"] is False and "gamification_base_url" not in native


def test_what_the_client_sends_capillary():
    rn = build_prerequisites(KB, "react-native", "direct", [])
    assert {"android_application_id", "ios_bundle_id", "android_sha256"} <= ids(rn["give_capillary"])
    assert "push_firebase_project" not in ids(rn["give_capillary"])
    pushed = build_prerequisites(KB, "react-native", "direct", ["push"])
    assert "push_firebase_project" in ids(pushed["give_capillary"])
    # accounts and access the client sets up themselves are a separate group
    assert "android_repo_access" in ids(build_prerequisites(KB, "android", "direct", [])["setup"])
    assert "android_repo_access" in ids(build_prerequisites(KB, "android", "firebase", [])["setup"])
    assert "ios_repo_access" not in ids(build_prerequisites(KB, "ios", "direct", [])["setup"])  # public repository


def test_titles_have_no_unfilled_placeholders():
    for platform, mode in product(PLATFORMS, MODES):
        view = build_prerequisites(KB, platform, mode, ALL_MODULES)
        for row in [*view["from_capillary"], *view["give_capillary"], *view["setup"]]:
            assert "{" not in row["title"], row


def test_versions_come_from_the_guides():
    android = build_prerequisites(KB, "android", "direct", [])
    values = {r["label"]: r["value"] for r in android["versions"]}
    assert values["Hydra SDK version"].startswith(str(frontmatter.load(KB / "android" / "direct.md").metadata["sdk_version"]))
    assert values["Minimum Android version (minSdk)"] == "21 or above"
    # mode-specific items
    assert "Gradle settings" in values
    assert "Gradle version catalog" not in values
    firebase = {r["label"] for r in build_prerequisites(KB, "android", "firebase", [])["versions"]}
    assert "Gradle version catalog" in firebase and "Gradle settings" not in firebase

    rn = {r["label"]: r["value"] for r in build_prerequisites(KB, "react-native", "firebase", [])["versions"]}
    assert rn["React Native"] == "0.77.0 or later" and rn["Node.js"] == "18.0.0 or later"


def test_push_only_items_appear_only_with_push():
    without = {r["label"] for r in build_prerequisites(KB, "web", "firebase", [])["versions"]}
    with_push = {r["label"] for r in build_prerequisites(KB, "web", "firebase", ["push"])["versions"]}
    assert "Firebase JS SDK (push)" not in without and "Firebase JS SDK (push)" in with_push
    # the browser minimums are listed on the push page but may apply to the whole SDK, so they always show
    assert {"Chrome", "Firefox", "Safari", "Edge, Chromium"} <= without


def test_computer_specs_are_not_invented():
    view = build_prerequisites(KB, "ios", "direct", [])
    assert "RAM" in view["computer_gap"] and "published" in view["computer_gap"]
    assert any(r["general"] for r in view["computer"])  # the macOS note is flagged as general knowledge


def test_endpoint_returns_the_same_view():
    got = asyncio.run(prerequisites(platform="ios", mode="direct", modules=["push"]))
    assert got == build_prerequisites(KB, "ios", "direct", ["push"])


def test_http_validates_the_choices():
    client = TestClient(app)  # no `with`, so the database lifespan isn't started
    ok = client.get("/prerequisites", params={"platform": "web", "mode": "direct", "modules": ["push", "gamification"]})
    assert ok.status_code == 200 and ok.json()["platform"] == "web"
    assert client.get("/prerequisites", params={"platform": "windows-phone"}).status_code == 422
    assert client.get("/prerequisites", params={"platform": "web", "modules": ["nope"]}).status_code == 422


def test_descriptions_stay_short():
    """The tab shows one-liners: every rule has a `short` text, and nothing on the page runs long."""
    from app.rules.prereq_engine import load_rules

    for rule in load_rules(KB).items:
        assert rule.short and len(rule.short) <= 130, (rule.id, len(rule.short or ""))
    for platform, mode in product(PLATFORMS, MODES):
        view = build_prerequisites(KB, platform, mode, ALL_MODULES)
        for row in [*view["versions"], *view["computer"]]:
            assert len(row["value"]) <= 90, (platform, row["label"], len(row["value"]))
            assert len(row["note"] or "") <= 60
        assert all(len(g) <= 130 for g in view["gaps"])
