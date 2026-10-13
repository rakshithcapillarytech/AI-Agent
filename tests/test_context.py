from app.config import Settings
from app.graph import context


def _system_message(monkeypatch, provider: str):
    monkeypatch.setattr(context, "get_settings", lambda: Settings(llm_provider=provider))
    return context.build_system_message({"messages": [], "phase": "discovery"})


def test_claude_gets_two_cached_blocks(monkeypatch):
    blocks = _system_message(monkeypatch, "anthropic").content
    assert [b["cache_control"] for b in blocks] == [{"type": "ephemeral"}] * 2
    assert '<phase name="discovery">' in blocks[1]["text"]


def test_gemini_gets_one_plain_string_static_part_first(monkeypatch):
    content = _system_message(monkeypatch, "google").content
    assert isinstance(content, str)
    assert content.startswith("You are the Experience+ Integration Copilot")
    assert '<phase name="discovery">' in content
