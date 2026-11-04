from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.rules.prereq_engine import build_checklist, load_rules
from app.tools.prereqs import get_checklist, record_prerequisite

PROFILE = IntegrationProfile(
    platforms=[{"platform": "android", "config_mode": "direct"}],
    modules=["core"],
    environment="uat",
    region="IN",
    customer_id_type="mobile",
    confirmed=True,
)
STATE = {
    "messages": [],
    "profile": PROFILE.model_dump(),
    "prerequisites": [
        i.model_dump() for i in build_checklist(PROFILE, load_rules(get_settings().knowledge_base_dir))
    ],
}


def call(tool, state=STATE, **args):
    command = tool.invoke(
        {"type": "tool_call", "id": "call_1", "name": tool.name, "args": {**args, "state": state}}
    )
    return command.update, command.update["messages"][0]


def test_get_checklist_groups_by_owner_and_lists_what_blocks():
    _, message = call(get_checklist)
    text = message.content
    assert text.index("The client does or provides") < text.index("Capillary provides")
    assert "android_application_id" in text and "account_id" in text
    assert "Still needed from the client before integration: android_application_id, android_repo_access" in text


def test_get_checklist_before_discovery_ends():
    _, message = call(get_checklist, state={"messages": [], "profile": {}})
    assert "no checklist yet" in message.content


def test_record_status_and_value():
    update, message = call(
        record_prerequisite, item_id="android_application_id", status="provided", value=" com.demo.retail "
    )
    item = next(p for p in update["prerequisites"] if p["id"] == "android_application_id")
    assert item["status"] == "provided" and item["value"] == "com.demo.retail"
    assert "before integration: android_repo_access" in message.content
    # The input state isn't mutated.
    assert STATE["prerequisites"][0]["status"] == "pending"


def test_record_rejects_bad_values_and_unknown_ids():
    for args in (
        {"item_id": "android_application_id", "status": "provided", "value": "not an id"},
        {"item_id": "nope", "status": "provided"},
    ):
        update, message = call(record_prerequisite, **args)
        assert message.status == "error"
        assert "prerequisites" not in update


def test_record_never_stores_a_value_on_items_without_one():
    update, message = call(
        record_prerequisite, item_id="android_repo_access", status="provided", value="ghp_secret"
    )
    item = next(p for p in update["prerequisites"] if p["id"] == "android_repo_access")
    assert item["status"] == "provided" and item["value"] is None
    assert "ghp_secret" not in message.content
    assert "value was not stored" in message.content
