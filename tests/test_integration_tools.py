from app.config import get_settings
from app.graph.nodes.phase_transition import next_phase, phase_transition
from app.graph.state import IntegrationProfile
from app.kb.loader import read_files, render_values
from app.tools.integration import complete_step, confirm_verification, get_integration_plan
from app.tools.search import search_issues, search_knowledge

PROFILE = IntegrationProfile(
    platforms=[{"platform": "android", "config_mode": "direct"}],
    modules=["core"],
    environment="uat",
    region="IN",
    customer_id_type="mobile",
    confirmed=True,
)
PLAN = ["android/direct.md › 1. A", "android/direct.md › 2. B"]


def call(tool, state, **args):
    command = tool.invoke(
        {"type": "tool_call", "id": "c1", "name": tool.name, "args": {**args, "state": state}}
    )
    return command


def test_entering_integration_builds_the_plan_from_the_loaded_files():
    from app.api.setup import initial_state

    state = initial_state(PROFILE)
    for item in state["prerequisites"]:
        if item["owner"] == "client" and item["blocking"]:
            item["status"] = "provided"
    update = phase_transition({**state, "messages": []})
    assert update["phase"] == "integration"
    assert update["plan_steps"][0] == "android/direct.md › 1. Store GitHub credentials locally"
    assert update["current_step"] == 0


def test_the_plan_is_not_rebuilt_once_it_exists():
    from app.api.setup import initial_state

    state = {**initial_state(PROFILE), "phase": "integration", "plan_steps": PLAN, "current_step": 1}
    assert "plan_steps" not in phase_transition({**state, "messages": []})


def test_complete_step_advances_and_the_phase_follows():
    state = {"plan_steps": PLAN, "current_step": 0, "phase": "integration"}
    first = call(complete_step, state)
    assert first.update["current_step"] == 1 and "[CURRENT] android/direct.md › 2. B" in first.update["messages"][0].content
    last = call(complete_step, {**state, "current_step": 1}, status="skipped")
    assert last.update["current_step"] == 2
    assert next_phase("integration", PROFILE, [], PLAN, 2) == "verification"


def test_complete_step_errors_without_a_plan_or_past_the_end():
    for state in ({"plan_steps": []}, {"plan_steps": PLAN, "current_step": 2}):
        command = call(complete_step, state)
        assert command.update["messages"][0].status == "error" and "current_step" not in command.update


def test_get_integration_plan_marks_the_current_step():
    text = call(get_integration_plan, {"plan_steps": PLAN, "current_step": 1}).update["messages"][0].content
    assert "1. [done]" in text and "2. [CURRENT]" in text


def test_verification_only_after_integration():
    early = call(confirm_verification, {"phase": "integration"})
    assert early.update["messages"][0].status == "error" and "verified" not in early.update
    assert call(confirm_verification, {"phase": "verification"}).update["verified"] is True
    assert next_phase("verification", PROFILE, [], PLAN, 2, verified=True) == "done"
    assert next_phase("verification", PROFILE, [], PLAN, 2) == "verification"


def test_client_identifiers_fill_their_placeholders_but_capillary_values_do_not():
    assert render_values("id={{application_id}} k={{gamification_key}}", {"application_id": "com.a.b"}) == (
        "id=com.a.b k={{gamification_key}}"
    )
    kb = get_settings().knowledge_base_dir
    filled = read_files(["flutter/firebase.md"], kb, {"application_id": "com.demo.retail"})
    assert "{{application_id}}" not in filled and "com.demo.retail" in filled
    assert "{{bundle_id}}" in filled  # not stated yet, so it stays a placeholder
    assert "{{account_id}}" in filled


STATE = {"loaded_files": ["android/direct.md"], "profile": PROFILE.model_dump()}


def test_search_tools_cite_file_and_heading_and_admit_when_empty():
    text = call(search_knowledge, STATE, query="401 from maven.pkg.github.com read:packages")
    assert "android/direct.md › Known Issues" in text.content
    assert "No matching" in call(search_knowledge, STATE, query="qqzzx wwvv").content
    assert "No approved past issue" in call(search_issues, STATE, query="401 gradle").content
