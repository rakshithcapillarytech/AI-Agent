"""End-to-end graph run with a scripted fake model: no API key or network needed."""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.builder import build_graph


class ScriptedModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def _tool_call(name: str, args: dict, call_id: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


async def test_discovery_to_prerequisites():
    model = ScriptedModel(
        messages=iter(
            [
                _tool_call(
                    "update_profile",
                    {
                        "updates": {
                            "platforms": [{"platform": "flutter", "config_mode": "firebase"}],
                            "modules": ["core", "push", "gamification"],
                            "environment": "uat",
                            "region": "IN",
                            "customer_id_type": "mobile",
                        }
                    },
                    "call_1",
                ),
                AIMessage(content="Here's your profile. Is it correct?"),
                _tool_call("confirm_profile", {}, "call_2"),
                AIMessage(content="Great, let's sort out the prerequisites."),
            ]
        )
    )
    graph = build_graph(checkpointer=InMemorySaver(), model=model)
    config = {"configurable": {"thread_id": "test"}}

    state = await graph.ainvoke(
        {"messages": [HumanMessage("Flutter app with Firebase, push + gamification")]}, config
    )
    assert state.get("phase", "discovery") == "discovery"
    assert state["profile"]["platforms"][0]["platform"] == "flutter"
    assert state["messages"][-1].content == "Here's your profile. Is it correct?"

    state = await graph.ainvoke({"messages": [HumanMessage("Yes, that's right")]}, config)
    assert state["phase"] == "prerequisites"
    assert state["profile"]["confirmed"] is True
    assert "flutter/firebase.md" in state["loaded_files"]
    assert "_shared/firebase-setup.md" in state["loaded_files"]


async def test_prerequisites_checklist_to_integration():
    """Wizard-started Android session: the agent reads the checklist, records both blocking
    client items, and the system moves the session to integration."""
    from app.api.setup import initial_state
    from app.graph.state import IntegrationProfile

    profile = IntegrationProfile(
        platforms=[{"platform": "android", "config_mode": "direct"}],
        modules=["core"],
        environment="uat",
        region="IN",
        customer_id_type="mobile",
    )
    model = ScriptedModel(
        messages=iter(
            [
                _tool_call("get_checklist", {}, "call_1"),
                AIMessage(content="Here's what you need."),
                _tool_call(
                    "record_prerequisite",
                    {"item_id": "android_application_id", "status": "provided", "value": "com.demo.retail"},
                    "call_2",
                ),
                _tool_call(
                    "record_prerequisite",
                    {"item_id": "android_repo_access", "status": "provided"},
                    "call_3",
                ),
                AIMessage(content="All set, let's add the SDK."),
            ]
        )
    )
    graph = build_graph(checkpointer=InMemorySaver(), model=model)
    config = {"configurable": {"thread_id": "prereqs"}}

    state = await graph.ainvoke(
        {**initial_state(profile), "messages": [HumanMessage("Please start our onboarding.")]}, config
    )
    assert state["phase"] == "prerequisites"
    assert "android_repo_access" in state["messages"][-2].content  # the checklist tool result

    state = await graph.ainvoke(
        {"messages": [HumanMessage("Sent com.demo.retail, and we have repo access.")]}, config
    )
    assert state["phase"] == "integration"
    by_id = {p["id"]: p for p in state["prerequisites"]}
    assert by_id["android_application_id"]["value"] == "com.demo.retail"
    assert by_id["account_id"]["status"] == "pending"  # Capillary's values don't block
