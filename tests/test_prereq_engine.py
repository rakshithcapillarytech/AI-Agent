import pytest

from app.config import get_settings
from app.graph.state import IntegrationProfile, PrereqItem
from app.rules.prereq_engine import build_checklist, check_value, load_rules

KB = get_settings().knowledge_base_dir
RULES = load_rules(KB)
APPS = {"android", "ios", "react-native", "flutter", "web"}


def profile(*apps: str, modules=("core",), customer_id_type="mobile") -> IntegrationProfile:
    platforms = [dict(zip(("platform", "config_mode"), app.split("/"))) for app in apps]
    return IntegrationProfile(
        platforms=platforms, modules=list(modules), customer_id_type=customer_id_type
    )


def ids(p: IntegrationProfile) -> set[str]:
    return {item.id for item in build_checklist(p, RULES)}


def test_every_rule_traces_to_an_existing_knowledge_file():
    for rule in RULES.items:
        path = rule.source.split(" › ")[0]
        assert (KB / path).is_file(), f"{rule.id}: source {path} not found"


def test_every_platform_condition_is_a_real_platform_and_mode():
    for rule in RULES.items:
        for condition in rule.when:
            for target in condition.platforms or []:
                platform, _, mode = target.partition("/")
                assert platform in APPS, f"{rule.id}: {target}"
                assert mode in ("", "firebase", "direct"), f"{rule.id}: {target}"


def test_android_direct_with_gamification():
    got = ids(profile("android/direct", modules=["core", "gamification"]))
    assert {"android_application_id", "android_repo_access", "org_id", "ssl_public_key"} <= got
    assert {"gamification_key", "gamification_region", "cap_token"} <= got
    assert not {"ios_bundle_id", "android_sha256", "firebase_project", "google_services_json"} & got


def test_flutter_firebase_needs_both_config_files_and_signature():
    got = ids(profile("flutter/firebase", modules=["core", "push"]))
    assert {"android_application_id", "ios_bundle_id", "android_sha256"} <= got
    assert {"firebase_project", "google_services_json", "google_service_info_plist"} <= got
    assert "org_id" not in got  # Flutter: visitor flow only
    assert "gamification_key" not in got
    assert "org_id" in ids(profile("flutter/firebase", modules=["core", "visitor"]))


def test_firebase_is_base_setup_on_flutter_and_push_only_on_web_direct():
    # Flutter: Firebase registration and the config files are base setup in every mode.
    assert {"firebase_project", "google_services_json", "google_service_info_plist"} <= ids(
        profile("flutter/direct")
    )
    assert "firebase_project" not in ids(profile("web/direct"))
    web_push = ids(profile("web/direct", modules=["core", "push"]))
    assert {"firebase_project", "web_firebase_config", "web_vapid_key"} <= web_push


def test_web_direct_core_has_no_client_items_and_no_mobile_values():
    checklist = build_checklist(profile("web/direct"), RULES)
    assert [i.id for i in checklist if i.owner == "client"] == []
    assert {"account_id", "base_url", "org_id"} <= {i.id for i in checklist}
    assert "ssl_public_key" not in {i.id for i in checklist}


def test_org_id_follows_the_shared_prerequisites_table():
    assert "org_id" in ids(profile("ios/direct"))
    assert "org_id" in ids(profile("ios/firebase"))  # gamification passes orgID in both modes (to be confirmed)
    assert "org_id" not in ids(profile("react-native/firebase"))
    assert "org_id" in ids(profile("react-native/firebase", modules=["core", "visitor"]))


def test_customer_id_type_fills_the_crm_title():
    checklist = build_checklist(profile("ios/direct", customer_id_type="email"), RULES)
    crm = next(i for i in checklist if i.id == "crm_account_linking")
    assert crm.title.endswith("to email")


def test_rebuild_keeps_progress_and_drops_items_that_no_longer_apply():
    before = build_checklist(profile("android/direct"), RULES)
    for item in before:
        if item.id == "android_application_id":
            item.status, item.value = "provided", "com.demo.retail"
    before.append(PrereqItem(id="obsolete", title="Gone", owner="client"))

    after = build_checklist(profile("android/direct", "ios/direct"), RULES, existing=before)
    by_id = {i.id: i for i in after}
    assert by_id["android_application_id"].status == "provided"
    assert by_id["android_application_id"].value == "com.demo.retail"
    assert by_id["ios_bundle_id"].status == "pending"
    assert "obsolete" not in by_id


@pytest.mark.parametrize(
    ("rule_id", "value", "ok"),
    [
        ("android_application_id", "com.demo.retail", True),
        ("android_application_id", "retail", False),
        ("ios_bundle_id", "com.demo.retail-app", True),
        ("ios_bundle_id", "https://demo.com", False),
        ("android_sha256", ":".join(["AB"] * 32), True),
        ("android_sha256", ":".join(["AB"] * 20), False),
        ("gamification_key", "wk_live_abc", False),  # values are never recorded for secrets
        ("android_repo_access", "ghp_x", False),
    ],
)
def test_value_checks(rule_id, value, ok):
    assert (check_value(RULES.by_id()[rule_id], value) is None) is ok


def test_push_adds_the_firebase_project_and_service_account_item():
    for app in ("flutter/firebase", "react-native/direct", "ios/direct", "android/firebase"):
        assert "push_firebase_project" in ids(profile(app, modules=["core", "push"])), app
    assert "push_firebase_project" not in ids(profile("flutter/firebase", modules=["core"]))
    assert "push_firebase_project" not in ids(profile("android/direct", modules=["core", "push"]))  # no push here
    assert "push_firebase_project" not in ids(profile("web/firebase", modules=["core", "push"]))
    item = next(i for i in build_checklist(profile("flutter/firebase", modules=["push"]), RULES) if i.id == "push_firebase_project")
    assert item.owner == "client" and not item.blocking and "secure channel" in item.how


def test_native_android_signature_is_optional_but_react_native_and_flutter_need_it():
    android = {i.id: i for i in build_checklist(profile("android/firebase"), RULES)}
    assert "android_signature_native" in android and not android["android_signature_native"].blocking
    assert "android_sha256" not in android
    for app in ("react-native/direct", "flutter/firebase"):
        got = {i.id: i for i in build_checklist(profile(app), RULES)}
        assert got["android_sha256"].blocking and "android_signature_native" not in got


def test_react_native_package_access_is_to_check_and_every_mobile_app_gets_the_ssl_reminder():
    rn = {i.id: i for i in build_checklist(profile("react-native/firebase"), RULES)}
    assert not rn["rn_package_access"].blocking and rn["rn_package_access"].owner == "client"
    for app in ("android/direct", "ios/firebase", "flutter/direct", "react-native/direct"):
        got = {i.id: i for i in build_checklist(profile(app), RULES)}
        assert "ssl_key_updatable" in got and not got["ssl_key_updatable"].blocking, app
    assert "ssl_key_updatable" not in ids(profile("web/direct"))
    assert "rn_package_access" not in ids(profile("flutter/firebase"))


def test_sha256_accepts_the_signing_report_and_capillarys_stored_form():
    rule = RULES.by_id()["android_sha256"]
    hex64 = "C9F2936D37CF7B97FF3A474D0F24F0866B78D6D4217BBEB6877739603BBA968D"
    pairs = ":".join(hex64[i:i + 2] for i in range(0, 64, 2))
    for ok in (pairs, hex64, hex64.lower(), f"SHA256 - {hex64}", f"SHA-256: {pairs}"):
        assert check_value(rule, ok) is None, ok
    for bad in (hex64[:-2], "SHA1 - " + hex64[:40], "not a fingerprint"):
        assert check_value(rule, bad) is not None, bad
