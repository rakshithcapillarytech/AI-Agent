# Plan: Hydra SDK Onboarding Agent ("Experience+ Integration Copilot")

## 1. Context

**The problem.** Today, every client that adopts the Hydra SDK (Experience+) is onboarded through manual calls with the integration team. On those calls the team:
- gathers the client's requirements (Android, iOS, React Native, Flutter or Web; which modules),
- chases prerequisites (bundle IDs, SHA256 signatures, Firebase files, App Groups, GitHub repo access, CRM settings),
- walks developers through the integration,
- debugs their errors.

**Where the knowledge lives.** Two documents:
- `Integration document _ Experience+ .pdf/.docx` (112 pages)
- `Flutter-Hydra-Integration-Guide.pdf` (24 pages)

They mix platforms and config modes (Firebase Remote Config vs. "without Firebase") in one place, and they contain version drift and inconsistencies. **More documents will be added over time.**

**The goal.** An AI agent behind a web onboarding portal that:
1. Runs requirements discovery.
2. Produces and tracks a personalised prerequisites checklist.
3. Guides the integration step by step, with the client's own values filled into the code.
4. Troubleshoots issues.
5. Gets better from every resolved issue.

**MVP target.** A working demo for the team. One builder, about 6 weeks.

**Decisions made**

| Topic | Decision |
|---|---|
| Channel | Web onboarding portal |
| Language | Python |
| Agent framework | **LangGraph + LangChain** (`langchain-anthropic`), with the guardrails in §6.2 |
| Knowledge | **Curated `.md` files per platform × config mode**, loaded whole per client, plus **keyword search**. Vector search only when evals show the need. |
| LLM | **Development (now):** the free Gemini key with `gemini-3.8-flash` (main) and `gemini-3.5-flash-lite` (helper) via `ChatGoogleGenerativeAI`, using **synthetic data only**. **Production target:** Claude (Opus 5.5 main, Haiku 5.5 helper) via `ChatAnthropic`; Bedrock-ready. Switching is one env var: `LLM_PROVIDER`. |
| Escalation target | Open. Pluggable adapter; MVP uses an admin-console queue. |

---

## 2. Core design decisions

### 2.1 Knowledge = one curated Markdown file per platform × config mode (source of truth)
Separate `.md` files keep information from being mixed up, are human-reviewable and versioned in git, and make the agent's job *"load the files that match this client"*. Four refinements:

1. **Split by platform *and* config mode.** The biggest mix-up risk is Firebase vs. no-Firebase *within* one platform:
   - Android without Firebase has no push and uses the GitHub Maven + PAT setup.
   - Flutter's Remote Config key is `hydra_gamification_url`, not `hydra_gamification_base_url`.

   So the files are, for example, `android/direct.md` and `android/firebase.md`.
2. **Shared files for common content.** Overview, prerequisites exchange, Firebase project setup and CRM account linking are written once in `_shared/`.
3. **One fixed template for every file:** same front-matter and headings, enforced by `kb lint`. Gaps become visible and every file is navigable the same way.
4. **New documents are merged into these files, not added beside them.** Claude proposes a diff and an SME approves it (§5.3).

### 2.2 Agent = LangGraph state graph + LangChain model/tool wrappers
- **LangGraph runs the stateful, multi-day flow:**
  - an explicit `StateGraph`,
  - a **Postgres checkpointer**, so a session resumes days later when the client comes back with their Firebase files,
  - **`interrupt()`** for human escalation,
  - token streaming to the UI.
- **LangChain provides:**
  - `ChatAnthropic` (Claude),
  - `@tool` functions with Pydantic arguments,
  - `MarkdownHeaderTextSplitter` for the search index,
  - a `BaseRetriever` interface, so adding vector search later is a drop-in `EnsembleRetriever`.

### 2.3 Retrieval = load the matching files whole and cache them, plus keyword search
- **Measured corpus today:** 126k characters ≈ **~35k tokens** in total, so each platform file is roughly **3–10k tokens**.
- **After discovery:** the client's file(s) plus `_shared/*` are loaded **in full** into a **cached** prompt.
- **For cross-cutting questions and learned issues:** a keyword/fuzzy search tool covers all files.

### 2.4 Trade-offs (recorded for the team)

**A. Curated `.md` files vs. classic RAG (chunk the PDFs → embed → vector search)**

These are not strictly opposites:
- `.md` files are the *knowledge format*.
- RAG is a *retrieval method*.

What gets replaced is "auto-chunk the raw PDFs and trust vector similarity". Search over the `.md` files stays.

| | Curated `.md` files (chosen) | Classic vector RAG over PDFs |
|---|---|---|
| **Accuracy for step-by-step setup** | ✅ The whole, ordered file for the exact platform × mode | ❌ Top-k chunks can skip steps or mix modes and platforms |
| **Predictability** | ✅ Same profile → same knowledge; unit-testable | ⚠️ Depends on query wording and similarity |
| **Exact tokens** (API names, error strings) | ✅ Keyword/fuzzy search finds them exactly | ⚠️ Embeddings are weak on identifiers |
| **Fixing wrong info** | ✅ Edit one file, SME reviews the diff, history in git | ❌ Re-chunk and re-embed; the stale chunk can still surface |
| **Debugging a bad answer** | ✅ See exactly which file and section was used | ⚠️ Debugging retrieval rankings is hard |
| **Infrastructure** | ✅ Files + Postgres | ❌ Embedding model, vector index, chunk and top-k tuning |
| **Reuse** | ✅ Can become the public docs, Cursor rules or MCP resources | — |
| **Upfront effort** | ❌ ~1 week of curation + SME review | ✅ Ingest the PDFs as-is |
| **Ongoing maintenance** | ❌ Needs owners; every new doc must be merged (Claude drafts the diff) | ✅ Just add files |
| **Very large or messy corpora** (tickets, Slack, thousands of pages) | ❌ Can't hand-curate | ✅ What RAG is built for |
| **Paraphrased questions** | ⚠️ Keyword search can miss them. Softened because the whole platform file is in context; fully fixed by adding vectors later. | ✅ Semantic match |

**Long-term shape: a hybrid.**
- Curated `.md` files for the **core specification**.
- Vector RAG over the **long tail**: past tickets, Slack threads, release-note archives, other products.

The long tail is added as another retriever behind `search_knowledge`, with no agent change.

**B. Framework: LangGraph + LangChain (chosen)**
- **Benefits:**
  - built-in checkpointing/resume and `interrupt()`,
  - graph visualisation,
  - LangSmith tracing and evals,
  - a widely known stack for the team.
- **Known costs:**
  - LangChain wrappers can lag new Claude API features,
  - some defaults conflict with Opus 5.5,
  - frequent version churn.

  These are handled by the guardrails in §6.2: pinned versions, explicit settings, and a Week-2 compatibility spike.

---

## 3. What the current docs contain → how they map to files

| Target file | Source content today | Status |
|---|---|---|
| `flutter/firebase.md` | Flutter guide pp.1–24 + Integration doc pp.52–59 (gamification) | **Full** |
| `flutter/direct.md` | Flutter guide "Advanced Android/iOS setup" pp.6–9 (`HydraInitializer.initialize(this, hydraRemoteConfig)`) | Partial |
| `react-native/firebase.md` | Integration doc pp.1–6 (gamification only) | **Gap:** core RN + Firebase guide missing |
| `react-native/direct.md` | Integration doc pp.72–87 | **Full** |
| `web/firebase.md` | Integration doc pp.7–24 (gamification + Cursor runbook) | **Full** |
| `web/direct.md` | Integration doc pp.60–71 (incl. CSP) | **Full** |
| `ios/firebase.md` | Integration doc pp.25–37 (gamification) | **Gap:** push + Firebase/APNs not documented |
| `ios/direct.md` | Integration doc pp.88–99 (SPM, CocoaPods, private repo) | **Full** |
| `android/firebase.md` | Integration doc pp.38–51 (gamification) | **Gap:** push + Firebase not documented |
| `android/direct.md` | Integration doc pp.100–112 (GitHub Maven + PAT; push N/A) | **Full** |

**Missing on every platform.** SMEs fill these in Week 1:
- minimum OS and tooling versions
- troubleshooting/FAQ
- a verification procedure
- staging vs. prod URLs
- APNs key upload

**Doc errors are fixed while writing the files.** Each correction becomes an inline callout:

> ⚠️ *Source doc says X; confirmed Y — SME, date*

Corrections are also logged in `CHANGELOG.md` for the docs team. Seed list (needs SME confirmation):

| Area | Issue |
|---|---|
| Gamification key name | `hydra_gamification_url` (Flutter) vs. `hydra_gamification_base_url` (others). Mandatory keys also differ per platform. |
| Web API names | `WebSDK.track/pageView` vs. `HydraSDK.track/pageView` |
| Web init sample | Missing comma (p.62) |
| Web gamification fields | "Required" vs. "silently skipped" (p.65) |
| RN logging | `console_log_level` vs. `log_levels`/`LOG_LEVELS` |
| RN log-level param | `remoteLogLevel` (iOS) vs. `remoteDebugLevel` (Android) |
| RN snippets | Undefined `embedHeight`/`loyaltyHeight` |
| iOS SPM | `from: "1.1.0"` vs. required `1.7.5-preprod.12` |
| iOS no-Firebase Podfile | Lists push pods |
| No-Firebase checklists | Name Firebase RC keys |
| Android Embed view | "bannerId", likely embedId |
| `gamificationScreenDisappeared` | Argument differs by platform |
| Version drift | Flutter `^1.1.1-beta.6` vs. "1.1.0". Android `beta01` vs. `beta02`. iOS `preprod.10` vs. `.12`. |

---

## 4. End-to-end flow (what the client experiences)

```
 Invite link (CSM creates session: org name, region, CSM contact)
        │
 ① DISCOVERY ──► ② PREREQUISITES ──► ③ GUIDED INTEGRATION ──► ④ VERIFICATION ──► ✅ DONE
        ▲                 ▲                    ▲                      ▲
        └─────────────── ⑤ TROUBLESHOOTING (can interrupt any phase, returns to it) ──┘
                                   │ unresolved after 3 tries / low confidence
                                   ▼
                          ⑥ HUMAN ESCALATION (LangGraph interrupt) ──► answer resumes the chat
                                   │
                          ⑦ LEARNING LOOP (issue .md drafted → SME approves → knowledge base)
```

**① Discovery.** Conversational slot-filling builds an `IntegrationProfile` (Pydantic). The profile is shown live in a side panel, and the client confirms it. **The profile decides which `.md` files are loaded.**

| Slot | Values |
|---|---|
| Platforms | Android / iOS / React Native / Flutter / Web (multi) |
| Config mode | Uses Firebase? → `firebase`, otherwise `direct` |
| Per platform | Language/UI (Kotlin/Java; Swift-UIKit/SwiftUI/Obj-C); framework version; package manager (SPM/CocoaPods; npm/yarn/pnpm/bun); custom `Application` class?; `AppDelegate` customisations? |
| Modules | Core (identify/track), Push, In-App, Inbox API/UI, Visitor flow, Gamification (auto campaigns, Banner, Embed, Loyalty), multi-account |
| Environment | UAT/POC (beta builds) vs. prod; region `IN` / `US` / `ME` |
| Identity | Which identifier is `customerId`. Must match the CRM Account Linking Identifier. |
| Web specifics | Framework, CSP?, sub-path deploy?, web push? |
| Logistics | Dev contacts, go-live date |

**② Prerequisites.** A deterministic rules engine (`prerequisites.yaml`) turns the profile into a checklist. Each item has an **owner**, a **status** and a **validator**:
- **Client gives Capillary:** bundle ID, applicationId, SHA256 signing cert.
- **Capillary gives client:** accountId, baseURL, SSL public key, orgId, gamification key/region/URL, Banner/Embed/Loyalty IDs, GitHub repo access.
- **Client sets up:**
  - Firebase files and Remote Config keys
  - VAPID key and service worker
  - Apple portal: Push, App Group `group.<bundle>.hydra`, NSE bundle ID
  - Xcode capabilities
  - CRM Account Linking Identifier
  - icon assets
  - CSP allowlist
  - cap-token backend

**Validators catch mistakes early.** For example:
- `google-services.json` → `package_name` must equal the applicationId.
- The plist's `BUNDLE_ID` must equal the bundle ID.
- SHA256 must be in the right format.

**③ Guided integration.**
- The agent walks the loaded file's **Steps** section one step at a time.
- Code blocks contain placeholders (`{{account_id}}`, `{{application_id}}`, `{{sdk_version}}` …). The renderer fills them from the profile and the Capillary-side values, so code comes from curated files rather than being improvised.
- The **Integration Pack** download contains:
  - the rendered file,
  - every code block tagged with `file=…`, extracted as ready files,
  - a tailored **AI-coding-tool prompt**, generalising the Cursor prompt in the Web runbook (pp.14–24).

**④ Verification.** The client works through the file's **Verification** section:
- `onHydraSdkInitializationResult` / `isSdkInitialized()`,
- FCM token,
- gamification `onInitSuccess`,
- a test push,
- a campaign appearing.

The client uploads console logs and a log analyser checks known success and failure lines.

**⑤ Troubleshooting** (a subgraph):
1. Extract signals: error strings, platform, SDK version, step.
2. Search **approved issue files first** (`issues/*.md`), then the platform file's **Known Issues**, then all files.
3. Diagnose: ranked hypotheses with citations (`file#heading`).
4. Propose a fix, then confirm with the client.
5. After 3 failed attempts or low confidence → escalate.

**⑥ Escalation.** The `escalate` node calls LangGraph **`interrupt()`** with a **context pack**: profile, current step, logs, and fixes already tried. An engineer answers in the admin console, which resumes the thread with `Command(resume=answer)`; the agent relays the answer and continues.

**⑦ Learning loop.** "Learns from it" means **curated knowledge, not fine-tuning**.
- Every resolved thread → Haiku drafts an **issue file**: `issues/<platform>-<slug>.md` with front-matter `{platform, config_mode, sdk_version, error_signature, root_cause, fix, source_session}`.
- An SME approves it, and it is committed and indexed at the highest precedence.
- Recurring issues are promoted into the platform file's *Known Issues* section.
- Unanswerable questions are logged as **Doc Gaps**.
- Feedback buttons and "that worked" confirmations raise an issue's confidence.
- Real conversations become eval cases.

---

## 5. The knowledge base (designed for more documents)

### 5.1 Folder structure
```
knowledge_base/
  _shared/
    overview.md            # what Hydra / Experience+ is, modules, glossary
    prerequisites.md       # two-way exchange, CRM Account Linking, repo access, regions
    firebase-setup.md      # common Firebase project + Remote Config steps (firebase mode only)
  _template/platform.md    # the mandatory template for every platform file
  flutter/      firebase.md · direct.md
  react-native/ firebase.md · direct.md
  ios/          firebase.md · direct.md
  android/      firebase.md · direct.md
  web/          firebase.md · direct.md
  issues/                  # learned issue files (one per issue, SME-approved)
  prerequisites.yaml       # checklist rules engine input
  CHANGELOG.md             # every knowledge change + doc corrections
  source/                  # original PDFs/DOCX, archived as provenance
  inbox/                   # drop new documents here
```

### 5.2 Mandatory template (every platform file)
```markdown
---
platform: android            # flutter | react-native | ios | android | web
config_mode: direct          # firebase | direct
sdk_package: com.capillary:hydra-core
sdk_version: 1.9.22-beta02   # used by {{sdk_version}} in code blocks → one-line version bumps
modules_covered: [core, gamification, inapp, inbox]
modules_missing: [push]      # agent escalates instead of guessing
sources: ["Integration document _ Experience+ pp.100–112"]
owner: <SME name>
last_verified: 2026-10-20
---
# Android (without Firebase)
## Coverage            ← what's documented vs. not
## Requirements        ← min OS/tooling versions
## Prerequisites       ← platform-specific items (links to _shared/prerequisites.md)
## Steps               ← numbered: 1. Install … 2. Initialize … (code blocks with {{placeholders}}, file=…)
## Modules             ← ### Push · ### In-App · ### Inbox · ### Visitor · ### Gamification
## Verification        ← how to confirm each step/module works
## Known Issues        ← symptom → cause → fix (promoted from issues/)
## API Reference       ← methods, config keys
```
**`kb lint` enforces the template:**
- required front-matter and headings are present,
- placeholders are known,
- no hard-coded versions that differ from front-matter,
- every API/config symbol in a code block is on the allowlist.

**Size rule:** a file over ~15–20k tokens gets split by module (e.g. `android/direct/gamification.md`).

### 5.3 Adding new documents (the growth path)
Run `kb propose <file in inbox/>`:
1. **Convert** to Markdown with `docling` (via `langchain-docling`), keeping code blocks and tables.
2. **Classify:** Haiku (`with_structured_output`) decides which platform(s), mode(s) and modules the content belongs to.
3. **Propose edits:** Opus produces a **diff against the target `.md` files**. It merges steps, bumps the `sdk_version` front-matter, adds Known Issues, and flags **contradictions**. A new platform gets a new file from the template.
4. **SME review** in the admin "Knowledge Inbox": side-by-side diff; accept, edit or reject.
5. **Publish:** run `kb lint`, then commit and update `CHANGELOG.md`, rebuild the search index and symbol allowlist, then run the **regression gate**. Golden evals re-run and publishing is blocked on a score drop. Each new doc also brings 5–10 drafted golden Q&A pairs.

Later, **connectors** (Google Drive, Confluence, GitHub release notes) can feed `inbox/`. Your Claude workspace already has a "Capillary knowledge sources" search connector, which is worth evaluating as a source.

### 5.4 How the agent reads the knowledge (scales without re-architecture)
The agent's tools stay fixed:
- `load_platform_docs`
- `read_file_section`
- `search_knowledge`
- `search_issues`

| Stage | When | Mechanism |
|---|---|---|
| **A. Whole-file loading** (MVP) | Matching files ≤ ~60k tokens (today ~5–15k) | Load the matching platform file(s) plus `_shared/*` in full, delimited by file name, and **cache** them |
| **B. Keyword search** (MVP) | Any size | Custom LangChain `BaseRetriever` over Postgres full-text + `pg_trgm` fuzzy matching. Sections come from `MarkdownHeaderTextSplitter`, filtered by front-matter, with issues ranked first. |
| **C. + Semantic search** | Evals show recall below target, or the long tail (tickets, Slack) is added | `PGVector` retriever in the same Postgres + `EnsembleRetriever` (keyword + vector). **No agent change.** |
| **D. Heading-index loading** | Matching files > ~60k tokens | Load headings plus one-line summaries; the agent calls `read_file_section` on demand |

---

## 6. Architecture

```
┌──────────────────────── React portal (web/) ───────────────────────┐
│ Client portal: chat · live Profile & Checklist panel · file upload │
│ Admin: sessions · escalation queue (resume interrupts) · issue     │
│        review · Knowledge Inbox (doc diffs) · Capillary values ·   │
│        doc-gap report                                              │
└───────────────────────────────┬────────────────────────────────────┘
                                │ REST + SSE (graph.astream, stream_mode="messages")
┌───────────────────────────────▼────────────────────────────────────┐
│ FastAPI  /sessions  /sessions/{id}/messages  /files  /admin/*  /kb  │
│  └─ LangGraph OnboardingGraph  (PostgresSaver checkpointer)         │
│       router ─► agent ⇄ ToolNode ─► phase_transition ─► guardrails │
│                   └─► troubleshoot subgraph ─► escalate (interrupt) │
│     LangChain: ChatAnthropic (Opus 5.5 / Haiku 5.5) · @tool fns ·   │
│                KeywordRetriever (BaseRetriever) · text splitters    │
│  ├─ KB service: lint · index build · propose-diff · publish         │
│  └─ llm.py: ChatAnthropic for MVP → ChatBedrockConverse later       │
└───────┬─────────────────────────────┬───────────────────┬──────────┘
 Postgres 16 (+pg_trgm)          knowledge_base/ (git)      LangSmith
 checkpoints, sessions,          *.md platform files,       traces, datasets,
 profiles, checklists, KB        _shared, issues,           experiments,
 search index, escalations       prerequisites.yaml         feedback
```

### 6.1 LangGraph design
- **State (`OnboardingState`):**
  - `messages` (add_messages reducer; **append-only**)
  - `phase`
  - `profile: IntegrationProfile`
  - `prerequisites: list[PrereqItem]`
  - `loaded_files: list[str]`
  - `plan_steps`, `current_step`
  - `open_issue` (signature, attempts, hypotheses tried)
  - `escalation`
  - `citations`
- **Nodes:**
  - `router` (Haiku, structured output) classifies the latest message: `provide_info | ask_question | report_issue | step_done | off_topic`.
  - `agent` (Opus with **all tools bound once**) and `ToolNode` loop until there are no more tool calls.
  - `phase_transition` (plain Python, deterministic exit criteria):
    - profile confirmed → prerequisites
    - all blocking client-owned items done → integration
    - all steps done → verification

    On a phase change it sets `loaded_files` and the phase instructions.
  - `guardrails` runs the symbol allowlist check, secret redaction and a citation check.
- **Troubleshoot subgraph:** `extract_signals → search_issues/search_knowledge → diagnose → propose → await → resolved? → draft_issue | escalate(interrupt)`.
- **Tools (`@tool`, Pydantic args):**
  - `update_profile`, `confirm_profile`
  - `get_checklist`, `record_prerequisite`, `validate_file`, `request_capillary_items`
  - `load_platform_docs`, `read_file_section`, `search_knowledge`, `search_issues`
  - `render_step`, `build_integration_pack`, `mark_step`
  - `analyze_logs`, `escalate_to_human`

### 6.2 LLM configuration and LangChain guardrails (important with Opus 5.5)
- **Models:**
  - Main: `ChatAnthropic(model="claude-opus-5-5")`, $4 / $20 per MTok, cache reads $0.20.
  - Helper: `ChatAnthropic(model="claude-haiku-5-5")`, $0.10 / $0.50.
- **Development provider (until Claude credentials arrive):**
  - **Models:** Gemini via `langchain-google-genai`, with the free API key from AI Studio.
  - **Data:** on the free tier, Google uses prompts to improve its products, so **only synthetic test data**: never real client details, logs or files. Rate limits are per project and shown in AI Studio, and each agent turn takes 2–3 model calls.
  - **Thought signatures:** Gemini 3 requires them to be sent back with function-call history. The graph's append-only history covers this.
  - **Prompt caching:** Gemini caches implicitly, so the system prompt is sent as one plain string, static part first.
  - **Before any real client session,** switch `LLM_PROVIDER` to `anthropic` (or a paid Gemini tier, if that's ever the decision).
- **Structured output:** always `with_structured_output(Model, method="json_schema")`. **Never use forced tool calling:** Opus 5.5 returns a 400 for `tool_choice` `any`/specific tool. Bind tools with `tool_choice="auto"` (the default).
- **Prompt caching.** The system prompt has two content blocks, each with `cache_control`:
  1. the static persona/rules,
  2. the phase instructions plus the loaded `.md` files.

  Block 2 changes only on phase transitions, about 4–5 cache rebuilds per session, which is negligible. Bind the full tool set once, because changing tools also breaks the cache. Verify `cache_read_input_tokens` > 0 in LangSmith.
- **Thinking:** it can't be disabled on Opus 5.5. Keep the AIMessage content blocks, including thinking blocks, exactly as returned. **Do not use `trim_messages` or summarisation that edits earlier turns**: history must be append-only, and sessions fit easily in the 1M context.
- **Effort:** set it explicitly (Opus 5.5 defaults to `medium`): `medium` for chat, `high` for diagnosis and doc diffs. It is passed through `ChatAnthropic` model kwargs.
- **Pin versions** of `langgraph`, `langgraph-checkpoint-postgres`, `langchain-core` and `langchain-anthropic` in `uv.lock`, and upgrade deliberately.
- **Week-2 compatibility spike.** Confirm that `langchain-anthropic` passes through effort, `cache_control`, thinking blocks and refusal stop reasons. If any one is missing, that single call goes through a small node that calls the `anthropic` SDK directly. Everything else stays LangChain. For Gemini, confirm two things: tool calls work with the nested Pydantic schema (`update_profile`), and thought signatures survive the Postgres checkpointer round-trip.
- **Bedrock later.** Swap `ChatAnthropic` for `ChatBedrockConverse` (`langchain-aws`) in `llm.py` only.
- **Cost estimate (rough):** about $2–5 per complete onboarding (~60 calls, mostly cache reads). Proposing edits for a new 100-page doc costs well under $1.

### 6.3 Tech stack summary

| Layer | Choice |
|---|---|
| Language / tooling | Python 3.12, `uv`, `ruff`, `pytest` |
| API | FastAPI with SSE streaming |
| Agent orchestration | **LangGraph** (`StateGraph`, `ToolNode`, `interrupt`, `PostgresSaver`) |
| LLM + tools | **LangChain**: `langchain-anthropic` `ChatAnthropic`, `@tool`, structured output (`json_schema`) |
| Models | Claude Opus 5.5 (main), Claude Haiku 5.5 (router, extraction, drafting, judge) |
| Knowledge | `.md` files in git (`python-frontmatter`, `MarkdownHeaderTextSplitter`); `docling` for new docs; Postgres FTS + `pg_trgm` via a custom `BaseRetriever`; `PGVector` + `EnsembleRetriever` only at stage C |
| DB | Postgres 16 (SQLAlchemy + Alembic); uploads on local disk, S3 later |
| UI | React 19 + TypeScript + Vite (`web/`), Capillary console design tokens. Setup wizard, then chat. Admin pages to follow in React. |
| Observability / evals | **LangSmith** (traces, datasets, experiments). If data must stay in-house, self-hosted Langfuse via its LangChain callback. |
| Run | `docker-compose` (postgres, api, ui) |
| Escalation | `Escalator` protocol. MVP: admin queue that resumes interrupts, plus optional Slack webhook. Jira/Freshdesk adapter later. |

### 6.4 Security and privacy
- **Never ask for secrets in chat** (PATs, `.p8` keys, service accounts). The agent explains where to place them locally.
- **Inbound redaction:** `ghp_`/`github_pat_`, `wk_live_`, private keys. Redaction runs **before** anything is sent to LangSmith.
- **Capillary-side values** are entered by the CSM in admin and rendered only inside the authenticated session and the pack.
- **Uploaded logs and new docs are untrusted data.** They are delimited in prompts and never treated as instructions.
- **MVP auth:** a per-session magic link and an admin password. SSO comes later.

---

## 7. Repository layout (new project in `~/Desktop/AI model - Experience +`)

```
pyproject.toml · uv.lock · docker-compose.yml · .env.example · README.md
knowledge_base/                       # §5.1 (git-tracked, SME-owned)
app/
  api/main.py                         # FastAPI routes, SSE streaming from graph.astream
  graph/state.py                      # OnboardingState, IntegrationProfile, PrereqItem
  graph/builder.py                    # StateGraph wiring + PostgresSaver
  graph/nodes/{router,agent,phase_transition,guardrails}.py
  graph/subgraphs/troubleshoot.py     # incl. escalate (interrupt)
  graph/prompts/*.md
  tools/{profile,prereqs,files,docs,render,logs,escalation}.py   # @tool functions
  kb/{loader,lint,index,retriever,render,propose,publish}.py
  rules/prereq_engine.py
  validators/{google_services,plist,signing,logs}.py
  learning/{issues,doc_gaps}.py
  escalation/{base,admin_queue,slack_webhook}.py
  llm.py                              # ChatAnthropic factory (Bedrock-ready), pinned settings
  db/{models.py,migrations/} · cli.py # `kb lint|index|propose|publish|eval`
web/ (React portal: setup wizard, chat, details panel; admin pages later)
evals/{golden_qa.yaml, scenarios/, run_evals.py}   # LangSmith datasets + evaluators
tests/
```

---

## 8. MVP scope and timeline (solo, ~6 weeks)

**In scope for the demo**
- **All 10 platform × mode files drafted.** Q&A works across all platforms, and gaps are marked in `modules_missing`.
- **Two files fully SME-verified for guided integration:**
  - **Flutter + Firebase** (push + inbox + gamification).
  - **Android + direct** (core + gamification; a good troubleshooting story with GitHub Maven PAT auth).

  Swap these for your most common client stacks if they differ.
- A live "add a new document" flow.

| Week | Deliverables |
|---|---|
| **1 Knowledge base** (most important) | `_template/platform.md`. Convert the docs with docling, then have Claude draft all 10 platform files and the `_shared` files. **SME review of the 2 demo files**, errata corrections, `prerequisites.yaml`. **Collect 20–30 real past issues** into `issues/`. ~40 golden Q&A. |
| **2 KB tooling + LangChain spike + evals** | `kb lint`, the keyword retriever (FTS + trigram), placeholder renderer, symbol allowlist. **The §6.2 compatibility spike.** LangSmith dataset and evaluators. |
| **3 Graph core + UI** | `OnboardingState`, router, agent ⇄ ToolNode, phase_transition, PostgresSaver, discovery + prerequisite tools, rules engine, validators, FastAPI SSE, React portal with the live profile/checklist panel. |
| **4 Integration + troubleshooting** | Steps walker, Integration Pack, troubleshoot subgraph, guardrails node, `interrupt()` escalation + admin resume. |
| **5 Learning + growth** | Issue drafting/approval (writes `.md`), Known Issues promotion, doc-gap report, `kb propose` + Knowledge Inbox, regression gate, simulated-client scenario evals. |
| **6 Hardening + demo** | Cost and latency check, rehearsed demo, one-page results summary. |

**Demo script**
1. "Acme Retail" is interviewed, and the profile panel fills: Flutter, iOS + Android, Firebase, push + gamification, region IN. The graph loads `flutter/firebase.md` and `_shared/*`.
2. A personalised checklist appears. The uploaded `google-services.json` is caught with a **package_name mismatch**.
3. Guided steps follow with real values in the code. The client downloads the Integration Pack and AI-tool prompt.
4. An Android client pastes `Could not resolve com.capillary:hydra-core … 401`. The answer cites `android/direct.md#known-issues`: the PAT needs `read:packages`.
5. An unknown error → `interrupt()` → an engineer answers in admin → the thread resumes → an issue `.md` is approved → **a new session solves the same error instantly.**
6. **Drop a new doc** (release notes with a newer Android version) → a diff to `android/direct.md` is proposed with the version conflict flagged → the SME approves → the agent uses the new version.
7. Bonus: show the LangGraph graph view and the LangSmith trace of the session.

---

## 9. Success metrics

| Metric | Demo | Pilot |
|---|---|---|
| Correct files loaded for the profile | 100% | 100% |
| Answer correctness (judge + SME spot-check) | ≥ 85% | ≥ 90% |
| Hallucinated API/config symbols | 0 on eval set | ~0 |
| Discovery completed without a human | Demonstrated | ≥ 80% |
| Troubleshooting deflection | Demonstrated | ≥ 60% |
| Kickoff → first successful SDK init | Baseline captured | –50% vs. today |
| New doc → merged and live (incl. review) | < 1 hour | < 1 day |
| Cost per completed onboarding | Measured | < $10 |

---

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| LangChain lag or incompatibility with Opus 5.5 | Pinned versions; `json_schema` structured output; no forced `tool_choice`; Week-2 spike; per-call fallback to the `anthropic` SDK inside a node |
| Free-tier Gemini during development (prompts used by Google; tight rate limits) | Synthetic data only; switch `LLM_PROVIDER` to Claude before any real client session; evals re-run on the production model before the demo |
| Cache misses from changing prompts or tools | Tools bound once; phase/doc block changes only on transitions; monitor `cache_read_input_tokens` |
| Doc inconsistencies and version drift | Corrections inside the curated files; version in front-matter only; `kb propose` flags contradictions |
| Shared facts drift between files | `_shared/` + `kb lint` + SME-reviewed diffs |
| Missing docs | `modules_missing` → the agent says "not documented → escalating"; Week-1 SME interviews |
| Files grow too large | Size rule (split by module); stage C/D retrieval ready |
| Hallucinated APIs | Code from curated files; symbol allowlist; citations; evals |
| Knowledge maintenance burden | `owner` + `last_verified` per file; stale-file report in admin |
| Secrets in chat or traces | Never-ask policy; redaction before LLM and LangSmith |
| Client distrust of a bot | An always-visible "talk to a human" button; context-rich handoffs |

---

## 11. Post-MVP roadmap
1. SSO for the React portal, plus admin pages (escalations, issue review, Knowledge Inbox).
2. Server-side verification via Capillary telemetry (init, identify and token events for the account).
3. SME verification of the remaining 8 files, and filling the documented gaps.
4. Source connectors feeding `inbox/`.
5. **Stage C RAG over the long tail:** past tickets, Slack threads, release notes.
6. The real escalation target via the adapter.
7. An **MCP server** for Cursor or Claude Code, so developers can have their Podfile, Gradle and manifest inspected.
8. Publish the curated `.md` files as the public docs.
9. A Slack Connect channel.
10. Bedrock for data residency.
11. An analytics dashboard.

---

## 12. Verification
- **Unit tests:**
  - `kb lint` (passes on all files, fails on a broken fixture);
  - the profile → file-selection mapping;
  - the rules engine (profile → expected checklist per platform × mode);
  - validators;
  - the placeholder renderer (output parses as JSON/Gradle/Swift);
  - the symbol extractor;
  - `phase_transition` exit criteria.
- **Graph tests:** run the compiled graph with a fake chat model (LangChain `GenericFakeChatModel`) to assert routing, phase transitions and that `interrupt()` → `Command(resume=…)` continues correctly.
- **Knowledge evals (LangSmith experiment):** for each golden question, was the expected `file#heading` loaded or cited? Answer correctness is scored by Claude-as-judge, with an SME spot-check of 20.
- **Scenario evals:** persona-driven simulated clients run both demo files. Each run asserts the final profile, loaded files, checklist, completed steps, escalation when expected, and an issue file created.
- **New-doc test:** `kb propose` on a synthetic release-notes doc. Assert that the right file is targeted, the conflict is flagged, the gate passes, and the answer reflects the new version.
- **Manual:** `docker compose up`, then run the §8 demo twice. In LangSmith, check the cache hit rate, cost per session and latency.
- **Resume:** kill the API mid-session, restart it, and confirm the thread continues from the PostgresSaver checkpoint.

---

## 13. Immediate next steps after approval
1. Scaffold the project in `~/Desktop/AI model - Experience +`: uv with pinned LangGraph/LangChain versions, docker-compose with Postgres, a FastAPI + Streamlit skeleton, a minimal `StateGraph` with PostgresSaver, and `llm.py`.
2. Write `_template/platform.md` and `_shared/*`. Convert the source docs and draft the 10 platform files, with gaps and corrections marked for SME review.
3. Draft `prerequisites.yaml` and seed `issues/` from the integration team's past cases.
4. Optional: publish this plan as a shareable page for the team.
