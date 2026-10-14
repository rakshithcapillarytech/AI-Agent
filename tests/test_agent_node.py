from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from app.graph.nodes.agent import NO_ANSWER, RETRY_NOTE, make_agent_node


class ScriptedModel(GenericFakeChatModel):
    seen: list = []

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, *args, **kwargs):
        self.seen.append(messages)
        return super()._generate(messages, *args, **kwargs)


async def _run(replies):
    model = ScriptedModel(messages=iter(replies), seen=[])
    node = make_agent_node(model, [])
    result = await node({"messages": [HumanMessage("How do we set up iOS push?")], "phase": "prerequisites"})
    return result["messages"], model.seen


async def test_empty_reply_is_retried_with_a_note_that_isnt_stored():
    stored, seen = await _run([AIMessage(content=[]), AIMessage(content="Add a Notification Service Extension.")])
    assert [m.content for m in stored] == ["Add a Notification Service Extension."]
    assert seen[1][-1].content == RETRY_NOTE


async def test_still_empty_after_retry_gives_a_clear_message_not_a_blank():
    stored, _ = await _run([AIMessage(content=""), AIMessage(content="")])
    assert stored[0].content == NO_ANSWER
