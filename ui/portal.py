"""Client onboarding portal (MVP): chat on the left, live integration status on the right.

The session id lives in the URL (?session=…), so the link doubles as the client's resumable
magic link.
"""

import json
import os

import requests
import streamlit as st

API = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Experience+ Integration Copilot", layout="wide")


def new_session() -> None:
    response = requests.post(f"{API}/sessions", timeout=10)
    response.raise_for_status()
    st.session_state.session_id = response.json()["session_id"]


def stream_reply(session_id: str, text: str):
    with requests.post(
        f"{API}/sessions/{session_id}/messages", json={"content": text}, stream=True, timeout=600
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            event = json.loads(line[len("data: "):])
            if event["type"] in ("token", "error"):
                yield event["text"]


if "session_id" not in st.session_state:
    if session_param := st.query_params.get("session"):
        st.session_state.session_id = session_param
    else:
        new_session()
st.query_params["session"] = st.session_state.session_id

session = requests.get(f"{API}/sessions/{st.session_state.session_id}", timeout=30).json()

chat, panel = st.columns([2, 1], gap="large")

with panel:
    st.subheader("Your integration")
    st.markdown(f"**Phase:** {session['phase']}")
    profile = session["profile"]
    if profile:
        st.markdown(f"**Profile** {'✅ confirmed' if profile.get('confirmed') else '(draft)'}")
        st.json({k: v for k, v in profile.items() if v not in (None, [], False)})
    if session["loaded_files"]:
        st.markdown("**Knowledge in use**")
        st.markdown("\n".join(f"- `{f}`" for f in session["loaded_files"]))
    st.divider()
    if st.button("Start a new session"):
        new_session()
        st.rerun()

with chat:
    st.title("Experience+ Integration Copilot")
    if not session["messages"]:
        st.info(
            "Hi! I'll help you integrate the Hydra SDK. "
            "Tell me which app(s) you're integrating: Android, iOS, React Native, Flutter or Web."
        )
    for message in session["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

if prompt := st.chat_input("Message the copilot"):
    with chat:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.write_stream(stream_reply(st.session_state.session_id, prompt))
    st.rerun()
