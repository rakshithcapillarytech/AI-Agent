"""The only place that constructs chat models. Swap providers here, nowhere else.

Providers (LLM_PROVIDER):
- google: Gemini via langchain-google-genai, for development on the free key. The free tier
  lets Google use prompts to improve its products, so use synthetic data only, never real
  client details or logs.
- anthropic: Claude, the production target (PLAN.md §6.2). Thinking is always on with Opus 5.5
  (don't send a `thinking` param); never force tool use; effort defaults to `medium`.
- bedrock: post-MVP.

Both Gemini 3 (thought signatures) and Claude (thinking blocks) require earlier assistant
messages to be sent back exactly as returned; the graph's history is append-only for this.
"""

from langchain_core.language_models.chat_models import BaseChatModel

from app.config import get_settings

DEFAULT_MODELS = {
    # provider: (main agent, helper for routing / extraction / drafting)
    "google": ("gemini-3.8-flash", "gemini-3.5-flash-lite"),
    "anthropic": ("claude-opus-5-5", "claude-haiku-5-5"),
}
# Tried in order when the main model errors. Free-tier Gemini Flash often returns 503 "high
# demand"; flash-lite is weaker (it reversed a documented correction in testing) but available.
FALLBACK_MODELS = {
    "google": ["gemini-3.5-flash-lite"],
    "anthropic": [],
}
ANTHROPIC_MAX_TOKENS = 16_000


def _build(model_id: str, effort: str | None = None) -> BaseChatModel:
    provider = get_settings().llm_provider

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Reads GOOGLE_API_KEY. `effort` is Claude-specific and is ignored here.
        # Fail fast: the default retry/backoff turns a 503 into a multi-minute silent hang.
        return ChatGoogleGenerativeAI(model=model_id, max_retries=1, timeout=45)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        kwargs = {}
        if effort:
            # Week-2 spike: confirm langchain-anthropic forwards output_config unchanged.
            kwargs["model_kwargs"] = {"output_config": {"effort": effort}}
        return ChatAnthropic(
            model=model_id, max_tokens=ANTHROPIC_MAX_TOKENS, streaming=True, **kwargs
        )

    if provider == "bedrock":
        raise NotImplementedError(
            "Bedrock is post-MVP: return langchain_aws.ChatBedrockConverse here, using the "
            "model ID shown in your Bedrock console."
        )
    raise ValueError(f"Unknown LLM_PROVIDER {provider!r}; use google, anthropic or bedrock.")


def main_model(effort: str | None = None) -> BaseChatModel:
    settings = get_settings()
    return _build(settings.main_model or DEFAULT_MODELS[settings.llm_provider][0], effort)


def fallback_models() -> list[BaseChatModel]:
    settings = get_settings()
    main = settings.main_model or DEFAULT_MODELS[settings.llm_provider][0]
    return [_build(m) for m in FALLBACK_MODELS[settings.llm_provider] if m != main]


def helper_model() -> BaseChatModel:
    settings = get_settings()
    return _build(settings.helper_model or DEFAULT_MODELS[settings.llm_provider][1])
