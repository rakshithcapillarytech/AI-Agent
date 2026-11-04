from app.graph.nodes.phase_transition import next_phase, phase_transition
from app.graph.state import IntegrationProfile, PrereqItem

CONFIRMED = IntegrationProfile(
    platforms=[{"platform": "android", "config_mode": "direct"}],
    modules=["core", "gamification"],
    environment="uat",
    region="IN",
    customer_id_type="mobile",
    confirmed=True,
)


def test_discovery_waits_for_confirmation():
    unconfirmed = CONFIRMED.model_copy(update={"confirmed": False})
    assert next_phase("discovery", unconfirmed, [], [], 0) == "discovery"
    assert next_phase("discovery", CONFIRMED, [], [], 0) == "prerequisites"


def test_prerequisites_wait_for_blocking_client_items_only():
    items = [
        PrereqItem(id="app_id", title="applicationId", owner="client", status="provided"),
        PrereqItem(id="account_id", title="accountId", owner="capillary"),  # not the client's
        PrereqItem(id="icons", title="Icons", owner="client", blocking=False),
    ]
    assert next_phase("prerequisites", CONFIRMED, items, [], 0) == "integration"

    items.append(PrereqItem(id="sha256", title="SHA256", owner="client"))
    assert next_phase("prerequisites", CONFIRMED, items, [], 0) == "prerequisites"


def test_prerequisites_never_complete_with_an_empty_checklist():
    assert next_phase("prerequisites", CONFIRMED, [], [], 0) == "prerequisites"


def test_integration_completes_after_last_step():
    assert next_phase("integration", CONFIRMED, [], ["install", "init"], 1) == "integration"
    assert next_phase("integration", CONFIRMED, [], ["install", "init"], 2) == "verification"


def test_leaving_discovery_loads_the_profile_files():
    update = phase_transition({"messages": [], "phase": "discovery", "profile": CONFIRMED.model_dump()})
    assert update["phase"] == "prerequisites"
    assert "android/direct.md" in update["loaded_files"]


def test_no_change_returns_empty_update():
    assert phase_transition({"messages": [], "phase": "discovery", "profile": {}}) == {}


def test_leaving_discovery_builds_the_checklist():
    update = phase_transition({"messages": [], "phase": "discovery", "profile": CONFIRMED.model_dump()})
    ids = {p["id"] for p in update["prerequisites"]}
    assert {"android_application_id", "android_repo_access", "gamification_key"} <= ids


def test_profile_changes_after_discovery_update_files_and_checklist():
    start = phase_transition({"messages": [], "phase": "discovery", "profile": CONFIRMED.model_dump()})
    for item in start["prerequisites"]:
        if item["id"] == "android_application_id":
            item["status"] = "provided"
    with_ios = IntegrationProfile.model_validate(
        {**CONFIRMED.model_dump(), "platforms": [*CONFIRMED.model_dump()["platforms"], {"platform": "ios", "config_mode": "direct"}]}
    )
    update = phase_transition({"messages": [], "phase": "prerequisites", **start, "profile": with_ios.model_dump()})
    assert "ios/direct.md" in update["loaded_files"]
    by_id = {p["id"]: p for p in update["prerequisites"]}
    assert by_id["ios_bundle_id"]["status"] == "pending"
    assert by_id["android_application_id"]["status"] == "provided"


def test_prerequisites_complete_once_client_blocking_items_are_done():
    start = phase_transition({"messages": [], "phase": "discovery", "profile": CONFIRMED.model_dump()})
    state = {"messages": [], "phase": "prerequisites", "profile": CONFIRMED.model_dump(), **start}
    state["phase"] = "prerequisites"
    assert "phase" not in phase_transition(state)
    for item in state["prerequisites"]:
        if item["owner"] == "client" and item["blocking"]:
            item["status"] = "provided"
    assert phase_transition(state)["phase"] == "integration"
