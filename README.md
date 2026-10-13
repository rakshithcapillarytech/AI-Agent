# Experience+ Integration Copilot

An AI agent that onboards clients onto Capillary's Hydra SDK (Experience+). It gathers requirements, tracks prerequisites, guides the integration, troubleshoots problems, and learns from resolved issues. The full design is in [PLAN.md](PLAN.md).

**Stack:**
- Python 3.12 · LangGraph + LangChain · FastAPI · Streamlit · Postgres
- **LLM in development:** Gemini (free key)
- **LLM in production:** Claude Opus 5.5 / Haiku 5.5. Switching is one env var: `LLM_PROVIDER` (see [app/llm.py](app/llm.py)).

> ⚠️ On the free Gemini tier, Google may use prompts to improve its products. Use **synthetic test data only** until the project switches to Claude.

## Status: scaffold (end of plan step 1)

Working skeleton:
- **Discovery phase.**
  - The agent interviews the client and records an `IntegrationProfile` (`update_profile`).
  - The client confirms it (`confirm_profile`).
  - The phase moves to *prerequisites* deterministically, and the client's platform × mode knowledge files are selected.
- **System prompt.** A static block plus a phase/knowledge block, both cached. Knowledge files that aren't written yet are marked *missing*, so the agent escalates instead of guessing.
- **Session persistence.** Sessions are LangGraph threads checkpointed in Postgres. The portal URL (`?session=…`) resumes a session.
- **Input redaction.** Secrets (GitHub tokens, gamification keys, private keys) are redacted before reaching the LLM.
- **Portal.** Streamlit chat with streaming replies and a live profile panel.

Knowledge base: **all 10 platform × mode files plus 3 shared files drafted** from the source docs, all `review_status: draft`. The SME review checklist (183 items) is in [knowledge_base/REVIEW.md](knowledge_base/REVIEW.md).

```bash
uv run python -m app.kb.lint
```

```bash
uv run python -m app.kb.review
```

`kb lint` checks that every platform file follows the template. `kb review` regenerates REVIEW.md from the ⚠️ callouts.

Not built yet (see the PLAN.md §8 timeline):
- SME review of the drafts, `prerequisites.yaml`, seeded issues and golden Q&A (week 1)
- keyword search (week 2)
- the prerequisites checklist (week 3)
- integration steps, troubleshooting and escalation (week 4)
- the learning loop and new-doc ingestion (week 5)

## Setup

**1. Install the tools (macOS, with Homebrew):**

```bash
brew install uv
```

```bash
brew install --cask docker
```

uv installs Python 3.12 for the project automatically.

**2. Configure your environment.** Copy the example file, then add your Gemini key (from https://aistudio.google.com/apikey) as `GOOGLE_API_KEY` in `.env`. Later, to switch to Claude, set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`.

```bash
cp .env.example .env
```

**3. Install dependencies and run the tests.** The tests need no API key; the graph test uses a scripted fake model.

```bash
uv sync
```

```bash
uv run pytest
```

Commit the generated `uv.lock`. It pins the LangGraph/LangChain versions (PLAN.md §6.2).

**4. Run everything.** Either use Docker Compose (Postgres, API on :8000, portal on :8501):

```bash
docker compose up --build
```

or run Postgres in Docker and the app locally with reload:

```bash
docker compose up -d postgres
```

```bash
uv run uvicorn app.api.main:app --reload
```

```bash
uv run streamlit run ui/portal.py
```

Open http://localhost:8501.

## Layout

```
PLAN.md                 the approved project plan
knowledge_base/         curated .md knowledge (one file per platform × config mode); see its README
app/
  api/main.py           FastAPI: sessions, SSE streaming, session state
  graph/                LangGraph: state, builder, nodes (agent, phase_transition, guardrails), prompts
  tools/profile.py      discovery tools (update_profile, confirm_profile)
  kb/loader.py          profile → knowledge files, delimited loading
  llm.py                the only place models are constructed (Bedrock swap goes here)
ui/portal.py            Streamlit client portal
tests/                  unit tests + graph smoke test
```
