from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool

from app.graph.context import build_system_message
from app.graph.state import OnboardingState


def make_agent_node(model: BaseChatModel, tools: list[BaseTool]):
    # Bind every tool once, with the default tool_choice="auto": a fixed tool list keeps the
    # prompt cache stable, and Opus 5.5 rejects forced tool use.
    bound = model.bind_tools(tools)

    async def agent(state: OnboardingState) -> dict:
        response = await bound.ainvoke([build_system_message(state), *state["messages"]])
        # Appended unchanged (thinking blocks included); history is never edited.
        return {"messages": [response]}

    return agent
