from app.graph.nodes.guardrails import redact


def test_redacts_github_tokens_and_keys():
    text = (
        "token=ghp_abcdefghijklmnopqrstuvwxyz0123 "
        "pat=github_pat_11ABCDEFG0123456789_abcdefghij "
        "key=wk_live_abc123"
    )
    redacted = redact(text)
    assert "ghp_" not in redacted
    assert "github_pat_" not in redacted
    assert "wk_live_" not in redacted


def test_redacts_private_keys():
    key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADAN\n-----END PRIVATE KEY-----"
    assert redact(f"here: {key}") == "here: [REDACTED_PRIVATE_KEY]"


def test_leaves_normal_text_alone():
    text = "Could not resolve com.capillary:hydra-core:1.9.22-beta02 (401)"
    assert redact(text) == text


from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.graph.nodes.guardrails import guardrails, ungrounded_symbols

CORPUS = "Call `HydraInitializer.initialize()` in main. Use hydra_gamification_base_url and onScreenChanged."


def test_known_names_pass_and_made_up_ones_are_flagged():
    reply = "Use `HydraInitializer.initialize()` and `onScreenChanged`, then `Hydra.makeItWork()`."
    assert ungrounded_symbols(reply, CORPUS) == ["Hydra.makeItWork"]


def test_plain_words_filenames_and_code_fences_are_not_checked():
    reply = "Edit `build.gradle` and `settings` then:\n```kotlin\nfooBarBaz()\n```"
    assert ungrounded_symbols(reply, CORPUS) == []


async def test_guardrails_node_appends_a_hidden_note_for_ungrounded_names():
    state = {
        "messages": [
            HumanMessage("how do I init?"),
            AIMessage("Call `HydraSdk.bootEverything()` first."),
        ],
        "loaded_files": [],
        "prerequisites": [],
    }
    update = await guardrails(state)
    note = update["messages"][0]
    assert note.additional_kwargs["guardrail"] and "`HydraSdk.bootEverything`" in note.content


async def test_names_the_client_or_tools_said_are_grounded():
    state = {
        "messages": [
            HumanMessage("my id is com.demo.retail_app"),
            ToolMessage("- [pending] firebase_project: Create a project", tool_call_id="1"),
            AIMessage("Noted `com.demo.retail_app`, next `firebase_project`."),
        ],
        "loaded_files": [],
        "prerequisites": [],
    }
    assert await guardrails(state) == {}
