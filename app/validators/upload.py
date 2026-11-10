"""Handling a file uploaded in the portal: check it, update the checklist, tell the agent.

The agent never sees file contents. It gets a short check result as the client's next message
and replies to it; the checklist item is marked verified here, by the system, only when the
file matches.
"""

import re

from langchain_core.messages import HumanMessage

from app.graph.state import PrereqItem
from app.validators.firebase_files import check_firebase_file

# History entries starting with this are shown as just their first line ("Uploaded file: x").
UPLOAD_HEADER = "Uploaded file:"
MAX_UPLOAD_BYTES = 256 * 1024
_IDENTIFIER_ITEMS = ("android_application_id", "ios_bundle_id")


def safe_filename(name: str) -> str:
    """The name is shown to the model, so keep it to plain characters."""
    name = name.replace("\\", "/").rsplit("/", 1)[-1]
    return re.sub(r"[^\w. \-]", "_", name)[:80] or "file"


def process_upload(state: dict, filename: str, content: bytes) -> dict:
    """The state update for an uploaded file: the new checklist (if it changed) and a message."""
    items = [PrereqItem.model_validate(p) for p in state.get("prerequisites") or []]
    expected = {i.id: i.value for i in items if i.id in _IDENTIFIER_ITEMS}
    check = check_firebase_file(content, expected)

    item = next((i for i in items if check.kind and i.validator == check.kind), None)
    update: dict = {}
    if check.kind and item is None:
        result = (
            f"{check.detail} This client's checklist doesn't include that file, so it isn't "
            "needed for their setup."
        )
    elif check.outcome == "match" and item is not None:
        item.status = "verified"
        update["prerequisites"] = [i.model_dump() for i in items]
        result = f"{check.detail} Checklist item recorded as verified."
    else:
        result = check.detail

    text = (
        f"{UPLOAD_HEADER} {safe_filename(filename)}\n"
        "(Automatic check by the system. The file's contents were not shared with you.)\n"
        f"Result: {result}"
    )
    update["messages"] = [HumanMessage(content=text)]
    return update
