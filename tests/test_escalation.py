"""Escalation end to end with a scripted model: pause on escalate_to_human, answer, resume."""

import json

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.api import main
from app.escalation.store import InMemoryEscalationStore
from app.graph.builder import build_graph
from app.tools.troubleshoot import MAX_ATTEMPTS, escalate_to_human, log_fix_attempt, resolve_issue
from tests.test_graph_smoke import ScriptedModel


def call(tool, state, **args):
    return tool.invoke({"type": "tool_call", "id": "c1", "name": tool.name, "args": {**args, "state": state}})


def test_third_failed_fix_tells_the_agent_to_escalate():
    state: dict = {}
    for n in range(1, MAX_ATTEMPTS + 1):
        update = call(log_fix_attempt, state, problem="gradle 401", fix=f"fix {n}").update
        state = {**state, **update}
        assert state["open_issue"]["attempts"] == n
    assert "escalate_to_human" in update["messages"][0].content
    assert "escalate_to_human" not in call(log_fix_attempt, {}, problem="p", fix="f").update["messages"][0].content


def test_resolving_records_the_issue_for_the_learning_loop():
    state = {"open_issue": {"attempts": 2, "tried": ["a", "b"]}, "plan_steps": ["f › 1. x"], "current_step": 0,
             "profile": {"platforms": [{"platform": "android", "config_mode": "direct"}]}}
    update = call(resolve_issue, state, problem="401", resolution="new PAT").update
    assert update["open_issue"] is None
    record = update["resolved_issues"][0]
    assert record["tried"] == ["a", "b"] and record["step"] == "f › 1. x" and record["apps"] == ["android/direct"]


@pytest.fixture
def client():
    # The fake model drops tool calls when it streams, so it replies in one piece.
    model = ScriptedModel(
        disable_streaming=True,
        messages=iter(
            [
                AIMessage(
                    content="An engineer has been asked to help.",
                    tool_calls=[{"name": "escalate_to_human", "args": {"summary": "SDK init crashes with E42"}, "id": "t1"}],
                ),
                AIMessage(content="The engineer says: upgrade to the latest SDK, then retry."),
            ]
        )
    )
    main.app.state.graph = build_graph(checkpointer=InMemorySaver(), model=model)
    main.app.state.escalations = InMemoryEscalationStore()
    return TestClient(main.app)


def events(response) -> list[dict]:
    return [json.loads(l[6:]) for l in response.text.splitlines() if l.startswith("data: ")]


PROFILE = {
    "company": "Demo Retail", "platforms": [{"platform": "android", "config_mode": "direct"}],
    "modules": ["core"], "environment": "uat", "region": "IN", "customer_id_type": "mobile",
    "contacts": [], "go_live_date": None,
}


def test_escalate_pause_admin_answer_resume(client):
    sid = "s1"
    response = client.post(f"/sessions/{sid}/start", json={"profile": PROFILE})
    assert response.status_code == 200
    assert {"type": "escalated"} in events(response)

    # The thread is paused: the portal is told, and new messages are refused (a tool call is open).
    assert client.get(f"/sessions/{sid}").json()["escalation"] == {"status": "open"}
    assert client.post(f"/sessions/{sid}/messages", json={"content": "hello?"}).status_code == 409

    # The admin queue shows the context pack.
    (row,) = client.get("/admin/escalations").json()
    assert row["summary"] == "SDK init crashes with E42" and row["session_id"] == sid
    assert row["context"]["company"] == "Demo Retail" and row["context"]["apps"] == ["android/direct"]

    answered = client.post(f"/admin/escalations/{row['id']}/answer", json={"answer": "Upgrade the SDK."})
    assert answered.status_code == 200
    assert client.post(f"/admin/escalations/{row['id']}/answer", json={"answer": "again"}).status_code == 409

    # The agent relayed the answer, the pause is over, and the chat works again.
    session = client.get(f"/sessions/{sid}").json()
    assert session["escalation"] is None
    assert session["messages"][-1]["text"] == "The engineer says: upgrade to the latest SDK, then retry."
    assert client.get("/admin/escalations").json() == []


def test_escalate_to_human_is_bound_in_the_graph():
    from app.graph.builder import TOOLS

    assert escalate_to_human in TOOLS
