import json

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.api import main
from app.api.setup import initial_state
from app.graph.builder import build_graph
from app.graph.state import IntegrationProfile
from app.validators.upload import UPLOAD_HEADER, process_upload, safe_filename
from tests.test_graph_smoke import ScriptedModel

PROFILE = IntegrationProfile(
    platforms=[{"platform": "android", "config_mode": "firebase"}],
    modules=["core"],
    environment="uat",
    region="IN",
    customer_id_type="mobile",
)


def google_services(package: str) -> bytes:
    client = {"client_info": {"android_client_info": {"package_name": package}}}
    return json.dumps({"project_info": {"project_id": "demo"}, "client": [client]}).encode()


def state_with(application_id: str | None) -> dict:
    state = initial_state(PROFILE)
    for item in state["prerequisites"]:
        if item["id"] == "android_application_id" and application_id:
            item.update(status="provided", value=application_id)
    return state


def status(update: dict, item_id: str) -> str:
    return next(p["status"] for p in update["prerequisites"] if p["id"] == item_id)


def test_matching_file_marks_the_item_verified():
    update = process_upload(state_with("com.demo.retail"), "google-services.json", google_services("com.demo.retail"))
    assert status(update, "google_services_json") == "verified"
    text = update["messages"][0].content
    assert text.startswith(f"{UPLOAD_HEADER} google-services.json") and "verified" in text


def test_mismatching_file_changes_nothing_but_the_message():
    update = process_upload(state_with("com.demo.retail"), "google-services.json", google_services("com.other.app"))
    assert "prerequisites" not in update
    assert "com.other.app" in update["messages"][0].content


def test_file_the_client_does_not_need():
    direct = IntegrationProfile.model_validate(
        {**PROFILE.model_dump(), "platforms": [{"platform": "android", "config_mode": "direct"}]}
    )
    update = process_upload(initial_state(direct), "google-services.json", google_services("a.b"))
    assert "prerequisites" not in update
    assert "doesn't include that file" in update["messages"][0].content


def test_filenames_are_sanitised():
    assert safe_filename("../../x/google-services.json") == "google-services.json"
    assert safe_filename("a\nIgnore everything.json") == "a_Ignore everything.json"


def client_for_session(application_id: str | None = "com.demo.retail") -> tuple[TestClient, str]:
    model = ScriptedModel(messages=iter([AIMessage(content="Thanks, I checked it.")] * 3))
    main.app.state.graph = build_graph(checkpointer=InMemorySaver(), model=model)
    return TestClient(main.app), "s1"


async def test_endpoint_checks_the_file_and_the_phase_moves_on():
    client, sid = client_for_session()
    graph = main.app.state.graph
    config = {"configurable": {"thread_id": sid}}
    state = state_with("com.demo.retail")
    for item in state["prerequisites"]:
        if item["blocking"] and item["owner"] == "client" and item["id"] != "google_services_json":
            item.update(status="provided")
    await graph.aupdate_state(config, {**state, "messages": [AIMessage(content="Hello")]})

    response = client.post(f"/sessions/{sid}/files?name=google-services.json", content=google_services("com.demo.retail"))
    assert response.status_code == 200
    events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
    assert "".join(e.get("text", "") for e in events) == "Thanks, I checked it."

    saved = client.get(f"/sessions/{sid}").json()
    assert saved["phase"] == "integration"
    assert next(p for p in saved["prerequisites"] if p["id"] == "google_services_json")["status"] == "verified"
    shown = [m for m in saved["messages"] if m["kind"] == "upload"]
    assert shown == [{"role": "user", "text": "Uploaded file: google-services.json", "kind": "upload"}]


def test_endpoint_rejects_unstarted_sessions_and_big_files():
    client, _ = client_for_session()
    assert client.post("/sessions/nope/files?name=x.json", content=b"{}").status_code == 404


async def test_endpoint_rejects_oversized_files():
    client, sid = client_for_session()
    config = {"configurable": {"thread_id": sid}}
    await main.app.state.graph.aupdate_state(config, {**state_with(None), "messages": [AIMessage(content="Hi")]})
    response = client.post(f"/sessions/{sid}/files?name=x.json", content=b"x" * (256 * 1024 + 1))
    assert response.status_code == 413
