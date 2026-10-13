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
