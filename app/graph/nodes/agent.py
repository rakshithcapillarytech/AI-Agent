from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool

from app.config import get_settings
from app.graph.context import build_system_message
from app.graph.messages import message_text
from app.graph.state import OnboardingState

# Gemini's recitation filter returns an empty reply (finish_reason RECITATION) when an answer
# reproduces a long code sample that also exists publicly (e.g. the iOS NotificationService.swift
# template). Asking only to "paraphrase" is still blocked; asking for short code passes. The note
# is sent for that one call and never stored in history.
RETRY_NOTE = (
    "(Your previous reply was blocked by a content filter, probably because it reproduced a long "
    "code sample. Answer the client's last message again: describe the steps in your own words, "
    "keep exact key names, method names and versions as written in the knowledge, and do NOT "
    "reproduce code blocks longer than 3 lines. Instead, point to the guide section that has the "
    "full code.)"
)
NO_ANSWER = (
    "Sorry, I couldn't put together an answer to that just now. Please try rephrasing your "
    "question. If it keeps happening, a Capillary engineer can help."
)


def _is_empty(message: BaseMessage) -> bool:
    return not message_text(message.content).strip() and not getattr(message, "tool_calls", None)


def make_agent_node(
    model: BaseChatModel, tools: list[BaseTool], fallbacks: list[BaseChatModel] | None = None
):
    # Bind every tool once, with the default tool_choice="auto": a fixed tool list keeps the
    # prompt cache stable, and Opus 5.5 rejects forced tool use.
    bound = model.bind_tools(tools)
    if fallbacks:
        # If the main model errors (e.g. 503 "high demand"), retry the call on the next model.
        bound = bound.with_fallbacks([f.bind_tools(tools) for f in fallbacks])

    async def agent(state: OnboardingState) -> dict:
        messages = [build_system_message(state), *state["messages"]]
        response = await bound.ainvoke(messages)
        # Only Gemini needs the retry. On Claude, thinking blocks are tied to the exact
        # conversation, so a reply produced with an unstored extra message must not be kept.
        if _is_empty(response) and get_settings().llm_provider == "google":
            response = await bound.ainvoke([*messages, HumanMessage(RETRY_NOTE)])
        if _is_empty(response):
            response = AIMessage(content=NO_ANSWER)
        # Appended unchanged (thinking blocks included); history is never edited.
        return {"messages": [response]}

    return agent
