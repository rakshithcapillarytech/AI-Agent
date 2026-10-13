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
