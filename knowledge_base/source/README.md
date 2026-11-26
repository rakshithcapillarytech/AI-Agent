# Sources

- `capillary-docs/`: the **current source of truth** for SDK facts, a mirror of Capillary's public developer docs made by `uv run python -m app.sync run` (see `../sources.yaml`). Don't edit it by hand.
- `Integration document _ Experience+ .pdf` / `.docx` and `Flutter-Hydra-Integration-Guide.pdf`: **legacy offline documents** from 2024. Public facts they carry are superseded by the online docs (the 2026-11-26 audit found several that are out of date, for example the Android Maven group, the iOS repository and the SDK versions). They stay here only because a few Corrections and Gaps in the guides cite them for internal-only statements. Don't add new offline documents: add an online source to `sources.yaml` instead.
