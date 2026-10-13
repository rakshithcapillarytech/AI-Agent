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
