# Experience+ Integration Copilot

A web portal that onboards clients onto Capillary's Hydra SDK (Experience+). The client answers a short wizard about their apps and the portal produces an **Integration Kit**: one Markdown guide tailored to their setup, plus ready-made prompts. The client attaches the guide to **their own AI assistant running on their machine** (Claude Code, Cursor, Claude, ChatGPT …) and does the setup and debugging there, where the assistant can see their real code and run their build. The full design is in [PLAN.md](PLAN.md).

> **Direction change, 2026-11-10.** The first version had a hosted chat agent (Gemini) doing the setup and debugging inside the portal. The kit above is now the main flow. The Gemini chat **stays accessible in the portal exactly as it is (the UI is unchanged)** as an optional extra; it isn't being extended and the kit doesn't depend on it. See PLAN.md §0 and §14.

**Stack:**
- Python 3.12 · FastAPI · Postgres
- Frontend: React 19 + TypeScript + Vite (`web/`), styled with Capillary's console design tokens
- **No hosted LLM in the main flow.** The kit is generated deterministically from the knowledge files.
- LangGraph + LangChain with Gemini (free key) or Claude are used by the optional chat assistant and by the evals. Switching is one env var: `LLM_PROVIDER` (see [app/llm.py](app/llm.py)).

> ⚠️ On the free Gemini tier, Google may use prompts to improve its products. Use **synthetic test data only** whenever a model is called.

## Status

**Main flow (the Integration Kit)**
- **Setup wizard (portal).** 5 steps with plain-English choices: company, apps (+ Firebase yes/no/not sure), features, account details, then review.
- **Integration Kit v0.** Once every app's Firebase question is answered, the client downloads one Markdown file with only the documentation for their setup plus rules for their AI assistant (`GET /sessions/{id}/guide`, built by `app/kb/guide.py`), and copies a personalised **setup** or **debug** prompt (`web/src/lib/prompts.ts`).
- **Knowledge base.** **All 10 platform × mode files plus 5 shared files drafted**, merged from the 2024 PDFs, three Confluence sources and Capillary's public developer docs (`docs.capillarytech.com`, November 2026) from the source docs, all `review_status: draft`. The SME review checklist (207 items; 55 corrections to confirm) is in [knowledge_base/REVIEW.md](knowledge_base/REVIEW.md).
- **Prerequisites rules.** `knowledge_base/prerequisites.yaml` turns a profile into a personalised checklist (`app/rules/prereq_engine.py`; every item cites its knowledge file). Built; it will be rendered into the guide.
- **Learning loop (review side).** Issue drafts, a lint gate, approval into `knowledge_base/issues/`, and a doc-gap report (`app/learning/`, the **Issue drafts** and **Doc gaps** tabs at `/?admin=1`, no login yet). Today the drafts come from the chat; they will come from a "report back" form (PLAN.md §4 ⑥).

```bash
uv run python -m app.kb.lint
```

```bash
uv run python -m app.kb.review
```

`kb lint` checks that every platform file follows the template. `kb review` regenerates REVIEW.md from the ⚠️ callouts.

**Deep evaluation.** `uv run python -m evals.audit_kb` runs 11 deterministic checks and builds 43 kit combinations (no model). `evals/deep/` holds 348 questions (one file per platform and mode), run blind against the generated kit with `uv run python -m evals.deep_tools prepare | grade | score`; the last run scored 339/348 (97.4%) raw, 346/348 (99.4%) with over-literal answer keys loosened (see CHANGELOG).

**Answer-quality tests (golden evals).** 18 questions with known answers in [evals/golden.yaml](evals/golden.yaml), checked automatically (required strings, forbidden strings, and yes/no checks by an AI grader). They currently run against the chat assistant; the plan is to point them at the kit (PLAN.md §12). Run them after any change to the model, the prompts or the knowledge:

```bash
uv run python -m evals.run_evals
```

Add `--model gemini-3.5-flash-lite` to test a specific model, or `--case <id>` for a single case. Each run calls the real model, so it uses API quota.

**Kept, optional: the hosted Gemini chat assistant** (built under the first plan; still accessible in the portal, UI unchanged, works and tested, not extended): discovery chat that records the profile, phase machine and step plan, in-portal checklist and `google-services.json` / plist checks, keyword search tools, troubleshooting tools, `escalate_to_human` with an engineers' queue, reply guardrail, session persistence in Postgres, and the streaming chat UI. Table of what is reused: PLAN.md §14.

Not built yet (see the PLAN.md §8 timeline):
- **Kit v1** (phase A): prerequisites checklist, AI operating rules (agentic and chat-only), troubleshooting and escalation protocol, learned issues and report-back instructions in the guide; a stateless `POST /kit`; a "Your integration kit" portal page; wizard and home copy for the new flow
- **Kit tests** (phase B): evals and scenario checks with the guide as the model's context
- **Report-back form** (phase D)
- SME review of the drafts, `prerequisites.yaml`, seeded issues and golden Q&A
- new-doc ingestion (`kb propose`), promoting recurring issues into Known Issues

## Setup

**1. Install the tools (macOS, with Homebrew):**

```bash
brew install uv
```

```bash
brew install --cask docker
```

uv installs Python 3.12 for the project automatically.

**2. Configure your environment.** Copy the example file. The portal and the kit need no API key; the chat assistant needs one. Add a Gemini key (from https://aistudio.google.com/apikey) as `GOOGLE_API_KEY` only to run the evals or the chat assistant; to use Claude instead, set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`.

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
PLAN.md                 the project plan (revision 2: Integration Kit)
knowledge_base/         curated .md knowledge (one file per platform × config mode); see its README
app/
  api/main.py           FastAPI: guide download, admin review (kept: sessions, SSE chat)
  kb/guide.py           builds the Integration Kit guide from the profile
  kb/loader.py          profile → knowledge files
  kb/lint.py, review.py knowledge-file template checks and the SME review checklist
  rules/prereq_engine.py  profile → prerequisites checklist
  learning/             issue drafts and doc gaps: review queue, lint gate, publishing
  kb/search.py, steps.py  keyword search; step list from the Steps sections (authoring tools)
  # kept, optional chat assistant:
  graph/ · tools/ · validators/ · escalation/ · llm.py
web/                    React portal (Vite): wizard, kit download and prompts, admin review (kept: chat UI, unchanged)
tests/                  unit tests + graph smoke test
```
