# Knowledge base

The source of truth the agent reads. Every file here is written for **one platform and one config
mode**, so information from different platforms never mixes (see `../PLAN.md` §2.1 and §5).

| Path | What it is |
|---|---|
| `_shared/overview.md` | What Hydra / Experience+ is, its modules, a glossary |
| `_shared/prerequisites.md` | The two-way exchange of values with Capillary, CRM Account Linking, repo access, regions |
| `_shared/firebase-setup.md` | Common Firebase project and Remote Config steps (Firebase mode only) |
| `<platform>/firebase.md` | The platform when the app uses Firebase Remote Config |
| `<platform>/direct.md` | The platform when the app doesn't use Firebase |
| `issues/*.md` | Learned issues, one per file, SME-approved |
| `_template/platform.md` | The required structure for every platform file |
| `source/` | Original vendor documents, kept as provenance (not read by the agent) |
| `inbox/` | Drop new documents here, then run `kb propose` (Week 5) |
| `CHANGELOG.md` | Every knowledge change, including corrections to the source docs |

Rules:
1. **Platform files follow the template.** That means the same front-matter and headings. `kb lint` enforces this from Week 2.
2. **Versions live only in the front-matter `sdk_version`.** Code blocks use `{{sdk_version}}`.
3. **Problems in the source docs are inline callouts**, in one of two forms (enforced by `kb lint`), and logged in `CHANGELOG.md`:
   - `> ⚠️ Correction: ✅ Use X. ❌ Don't use Y (where Y appears). *Pending SME confirmation.*` when one option is clearly right;
   - `> ⚠️ Gap: what isn't documented or what the docs disagree on. Ask a Capillary engineer.` for everything else.
   Once an SME confirms a correction, fold the ✅ value into the steps and drop the callout.
4. **New documents are merged into these files.** They never sit beside them as separate files.
