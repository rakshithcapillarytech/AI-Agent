from app.api.setup import SETUP_HEADER, initial_state, setup_message
from app.graph.state import IntegrationProfile

COMPLETE = IntegrationProfile(
    company="Demo Retail",
    platforms=[{"platform": "flutter", "config_mode": "firebase"}],
    modules=["core", "push", "gamification"],
    environment="uat",
    region="IN",
    customer_id_type="mobile",
)


def _with(**changes) -> IntegrationProfile:
    return IntegrationProfile.model_validate({**COMPLETE.model_dump(), **changes})


def test_complete_profile_starts_confirmed_with_knowledge_loaded():
    state = initial_state(COMPLETE)
    assert state["phase"] == "prerequisites"
    assert state["profile"]["confirmed"] is True
    assert "flutter/firebase.md" in state["loaded_files"]
    assert "_shared/firebase-setup.md" in state["loaded_files"]


def test_unsure_about_firebase_starts_in_discovery_without_knowledge():
    unsure = _with(platforms=[{"platform": "flutter"}])
    state = initial_state(unsure)
    assert state["phase"] == "discovery"
    assert state["profile"]["confirmed"] is False
    assert state["loaded_files"] == []


def test_client_supplied_confirmed_flag_is_ignored():
    incomplete = IntegrationProfile(company="Demo Retail", confirmed=True)
    assert initial_state(incomplete)["profile"]["confirmed"] is False


def test_setup_message_reads_naturally():
    text = setup_message(COMPLETE)
    assert text.startswith(SETUP_HEADER)
    assert "- Apps: Flutter (uses Firebase)" in text
    assert "- Features: core, push, gamification" in text
    unsure = setup_message(_with(platforms=[{"platform": "web"}]))
    assert "- Apps: Web (not sure about Firebase)" in unsure
