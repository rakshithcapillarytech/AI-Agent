# Experience+ Integration Copilot

An AI agent that onboards clients onto Capillary's Hydra SDK (Experience+). It gathers requirements, tracks prerequisites, guides the integration, troubleshoots problems, and learns from resolved issues. The full design is in [PLAN.md](PLAN.md).

**Stack:**
- Python 3.12 · LangGraph + LangChain · FastAPI · Postgres
- Frontend: React 19 + TypeScript + Vite (`web/`), styled with Capillary's console design tokens
- **LLM in development:** Gemini (free key)
- **LLM in production:** Claude Opus 5.5 / Haiku 5.5. Switching is one env var: `LLM_PROVIDER` (see [app/llm.py](app/llm.py)).

> ⚠️ On the free Gemini tier, Google may use prompts to improve its products. Use **synthetic test data only** until the project switches to Claude.

## Status: discovery → verification, with troubleshooting and escalation (plan weeks 3–4)

Working skeleton:
- **Discovery phase.**
  - The agent interviews the client and records an `IntegrationProfile` (`update_profile`).
  - The client confirms it (`confirm_profile`).
  - The phase moves to *prerequisites* deterministically, and the client's platform × mode knowledge files are selected.
- **System prompt.** A static block plus a phase/knowledge block, both cached. Knowledge files that aren't written yet are marked *missing*, so the agent escalates instead of guessing.
- **Session persistence.** Sessions are LangGraph threads checkpointed in Postgres. The portal URL (`?session=…`) resumes a session.
- **Input redaction.** Secrets (GitHub tokens, gamification keys, private keys) are redacted before reaching the LLM.
- **Portal (React).** A 5-step setup wizard with plain-English choices: company, apps (+ Firebase yes/no/not sure), features, account details, then review. A complete profile starts the session already confirmed, with the right guides loaded. The chat streams replies as Markdown (with copy buttons on code), and a details panel shows progress, setup and the guides in use. Recent onboardings are listed in the sidebar.
- **Prerequisites checklist.** `knowledge_base/prerequisites.yaml` turns the profile into a personalised checklist (rules engine in `app/rules/prereq_engine.py`; every item cites its knowledge file). The agent reads it with `get_checklist` and records progress with `record_prerequisite`, which format-checks identifiers (application ID, bundle ID, SHA256) and never stores secrets. Once every blocking client item is done, the session moves to integration on its own. The checklist follows later profile changes, keeping progress, and shows in the portal's details panel.
- **Guided integration.** When the prerequisites are done, the system builds the step plan from the `## Steps` of each loaded platform file (`app/kb/steps.py`). The agent walks it one step at a time with `get_integration_plan` / `complete_step`, with the client's own application ID and bundle ID filled into the code. After the last step the session moves to verification, and `confirm_verification` marks it done. The portal shows the steps in the details panel.
- **Keyword search.** `search_knowledge` and `search_issues` (`app/kb/search.py`) find sections by error text or API name, in memory with TF-IDF. Approved files in `knowledge_base/issues/` (front-matter `platform`, `config_mode`, `status: approved`, `error_signature`, `root_cause`, `fix`) rank first.
- **Troubleshooting and escalation.** The agent searches past issues and the Known Issues section, logs each fix it proposes (`log_fix_attempt`), and records a resolution (`resolve_issue`). After 3 failed fixes, a gap in the docs or a request for a person, `escalate_to_human` pauses the thread with LangGraph `interrupt()`. The portal tells the client an engineer was asked and polls for the reply. Engineers answer at **`/?admin=1`** (no login yet); the answer resumes the thread and the agent relays it. The queue is the `escalations` table in Postgres.
- **Output guardrail.** After each reply, code-like names (`HydraConfig.Builder`) that appear nowhere in the loaded knowledge or the conversation get a visible note telling the client to double-check them.
- **File checks.** The client uploads `google-services.json` or `GoogleService-Info.plist` from the checklist panel (`POST /sessions/{id}/files`). The system checks the package name or bundle ID inside against the one the client stated (`app/validators/`), marks the item verified on a match, and tells the agent only the result. The agent never sees the file, because it holds API keys.
- **Downloadable AI guide.** Once every app's Firebase question is answered, the client can download one Markdown file with only the documentation for their setup, plus rules for their AI assistant, and attach it to Claude, Cursor or ChatGPT (`GET /sessions/{id}/guide`, built by `app/kb/guide.py`).

Knowledge base: **all 10 platform × mode files plus 3 shared files drafted** from the source docs, all `review_status: draft`. The SME review checklist (183 items) is in [knowledge_base/REVIEW.md](knowledge_base/REVIEW.md).

```bash
uv run python -m app.kb.lint
```

```bash
uv run python -m app.kb.review
```

`kb lint` checks that every platform file follows the template. `kb review` regenerates REVIEW.md from the ⚠️ callouts.

**Answer-quality tests (golden evals).** 18 questions with known answers in [evals/golden.yaml](evals/golden.yaml), checked automatically (required strings, forbidden strings, and yes/no checks by an AI grader). Run them after any change to the model, the prompts or the knowledge:

```bash
uv run python -m evals.run_evals
```

Add `--model gemini-3.5-flash-lite` to test a specific model, or `--case <id>` for a single case. Each run calls the real model, so it uses API quota. On the free Gemini tier, `gemini-3.8-flash` allows only 20 requests a day; when it runs out, the agent falls back to flash-lite automatically.

Not built yet (see the PLAN.md §8 timeline):
- SME review of the drafts, `prerequisites.yaml`, seeded issues and golden Q&A (week 1)
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

**4. Run everything.** Either use Docker Compose (Postgres, API on :8000, portal on :8080):

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
npm --prefix web install
```

```bash
npm --prefix web run dev
```

Open http://localhost:5173 (the dev server proxies `/api` to the API on :8000).

## Layout

```
PLAN.md                 the approved project plan
knowledge_base/         curated .md knowledge (one file per platform × config mode); see its README
app/
  api/main.py           FastAPI: sessions, SSE streaming, session state
  graph/                LangGraph: state, builder, nodes (agent, phase_transition, guardrails), prompts
  tools/profile.py      discovery tools (update_profile, confirm_profile)
  validators/           uploaded-file checks (Firebase config files) and the upload handler
  escalation/store.py   the engineers' queue (Postgres; in memory in tests)
  kb/search.py, steps.py  keyword search; the integration plan from the Steps sections
  kb/loader.py          profile → knowledge files, delimited loading
  llm.py                the only place models are constructed (Bedrock swap goes here)
web/                    React portal (Vite): src/components, src/lib (API hooks, labels), styles/tokens.css
tests/                  unit tests + graph smoke test
```
