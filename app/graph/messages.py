def message_text(content) -> str:
    """Visible text of a message: plain str, or the `text` blocks of provider content blocks."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )
