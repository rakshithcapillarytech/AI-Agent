"""OnboardingGraph wiring.

    START → agent ─(tool calls)→ tools → phase_transition → agent
                  └(no tool calls)→ END

Running phase_transition right after tools means a confirmation (e.g. confirm_profile) moves
the session to the next phase within the same turn, and the agent continues in it.
The router, troubleshoot subgraph and guardrails node arrive in weeks 3–4 (PLAN.md §8).
"""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.graph.nodes.agent import make_agent_node
from app.graph.nodes.phase_transition import phase_transition
from app.graph.state import OnboardingState
from app.tools.profile import TOOLS


def build_graph(
    checkpointer: BaseCheckpointSaver | None = None,
    model: BaseChatModel | None = None,
    fallbacks: list[BaseChatModel] | None = None,
):
    if model is None:
        from app.llm import fallback_models, main_model

        model, fallbacks = main_model(), fallback_models()

    graph = StateGraph(OnboardingState)
    graph.add_node("agent", make_agent_node(model, TOOLS, fallbacks))
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("phase_transition", phase_transition)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "phase_transition")
    graph.add_edge("phase_transition", "agent")
    return graph.compile(checkpointer=checkpointer)
