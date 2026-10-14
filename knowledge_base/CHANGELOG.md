# Knowledge base changelog

## Accuracy review and simplification (2026-10-14)
Every file was re-checked line by line against the source documents (code against the .docx text, or the Flutter guide's page images) and simplified. Meta commentary and page numbers in body text were removed, and repeated explanations and minor gaps were merged. No steps, code, keys or versions were dropped. The golden test set passes 18/18 on the simplified files.

| File | Words before | Words after | Change |
|---|---|---|---|
| `_shared/firebase-setup.md` | 1,729 | 791 | -54% |
| `_shared/overview.md` | 282 | 283 | +0% |
| `_shared/prerequisites.md` | 398 | 424 | +7% |
| `android/direct.md` | 1,430 | 1,405 | -2% |
| `android/firebase.md` | 3,317 | 1,925 | -42% |
| `flutter/direct.md` | 6,579 | 4,049 | -38% |
| `flutter/firebase.md` | 6,085 | 3,868 | -36% |
| `ios/direct.md` | 2,852 | 1,713 | -40% |
| `ios/firebase.md` | 2,982 | 1,670 | -44% |
| `react-native/direct.md` | 3,679 | 2,274 | -38% |
| `react-native/firebase.md` | 2,000 | 1,306 | -35% |
| `web/direct.md` | 3,223 | 2,023 | -37% |
| `web/firebase.md` | 6,308 | 4,676 | -26% |
| **Total** | **40,864** | **26,407** | **-35%** |

### Accuracy fixes (selected)
- **Cap token origin:** "from the client's backend" isn't in any source. Removed everywhere; now a Gap in `_shared/prerequisites.md`.
- **Loyalty View ID:** comes from the Capillary team / the API response, not the gamification dashboard (only Banner and Embedded IDs do).
- **Config modes:** `direct` means settings passed to init instead of Remote Config. It does **not** mean "no Firebase": Flutter and Web direct mode can still use Firebase for push.
- **`android/direct.md`:** restored the source's Java blocks (sign-in, sign-out, events, cap token) and Kotlin forms, removed an invented `// optional` comment, and restored the dependency order.
- **React Native:** restored `Hydra.setCapToken('token')`, and removed an invented `BANNER_ID` declaration, invented file paths and an unsourced `cd ios`.
- **iOS:** removed an invented "don't share the token with Capillary" claim.
- **Web:** restored the source code comment and the original wording of the AI coding-tool prompt.
- **Flutter:** removed invented Known Issue symptoms, and a stale Org Id note.

### Callout format
- Every source-doc problem is now `⚠️ Correction: ✅ Use … ❌ Don't use …` (14, one option clearly right) or `⚠️ Gap: …` (125, including disagreements with no clear winner). `kb lint` rejects anything else.
- The gamification base-URL key is `hydra_gamification_base_url` on every platform. The `_shared/firebase-setup.md` table had listed `hydra_gamification_url` for Flutter, contradicting `flutter/firebase.md`. That contradiction caused a wrong answer in testing.

## Unreleased: first drafts (2026-10-13)
All files below are `review_status: draft`. **They need SME review before any real client session.** The open items are listed in `REVIEW.md` (`uv run python -m app.kb.review`).

### Added
- Structure, platform template (`_template/platform.md`) and the original documents in `source/`:
  - `Integration document _ Experience+ .pdf` / `.docx`
  - `Flutter-Hydra-Integration-Guide.pdf`
- Shared files:
  - `_shared/overview.md`
  - `_shared/prerequisites.md`
  - `_shared/firebase-setup.md`
- All 10 platform × config-mode files, drafted from the source documents (code checked against the .docx text, or against rendered pages for the Flutter guide):

| File | Source pages | Modules covered |
|---|---|---|
| `android/direct.md` | Integration doc pp.100–112 | core, gamification |
| `android/firebase.md` | Integration doc pp.38–51 (gamification add-on) | gamification. **Core Android + Firebase is not documented.** |
| `ios/direct.md` | Integration doc pp.88–99 | core, gamification |
| `ios/firebase.md` | Integration doc pp.25–37 (gamification add-on) | gamification. **Core iOS + Firebase is not documented.** |
| `react-native/direct.md` | Integration doc pp.72–87 | core, gamification |
| `react-native/firebase.md` | Integration doc pp.1–6 (gamification add-on) | gamification. **Core RN + Firebase is not documented.** |
| `flutter/firebase.md` | Flutter guide pp.1–24 + Integration doc pp.52–59 | all modules |
| `flutter/direct.md` | Flutter guide pp.1–24 (advanced setup) + Integration doc pp.52–59 | all modules. Push, in-app and inbox in this mode are *derived*, pending SME confirmation. |
| `web/firebase.md` | Integration doc pp.7–24 | core, push, visitor (partial), gamification |
| `web/direct.md` | Integration doc pp.60–71 | core, push, visitor (partial), gamification |

### Source doc corrections flagged (36, all *pending SME confirmation*)
Each one is an inline ⚠️ callout in its file and is listed in `REVIEW.md`. The most consequential:
- **Versions differ between guides** for the same platform:
  - Android: `1.9.22-beta01` (gamification guide) vs `beta02` (direct guide)
  - iOS: `preprod.10` vs `preprod.12`; SPM sample `from: "1.1.0"`
  - Flutter: `^1.1.1-beta.6` vs "1.1.0 (to be released)"
- **Android init call** differs: `HydraAPI.initialize` (Firebase-mode gamification guide) vs `HydraAPI.instanceWithConfig` (direct guide). Gamification is "bundled within HydraCore" vs separate `hydra-gamification` dependencies.
- **iOS repo** differs: `hydra-ios-sdk-spm.git` vs `hydra-sdk-ios-packages`.
- **Gamification Remote Config key:** `hydra_gamification_url` (Integration doc, Flutter) vs `hydra_gamification_base_url` (everywhere else). Which gamification keys are mandatory also differs by platform.
- **Web examples** use `WebSDK.track/pageView`, while the import and API table use `HydraSDK`. The direct-mode init sample is missing a comma.
- **`gamificationScreenDisappeared`:** takes a screen name in the Flutter guide and iOS, but no argument in the Integration doc's Flutter and RN samples.
- **RN snippets** use undefined `embedHeight` / `loyaltyHeight`. The RN log configuration (`console_log_level` vs `log_levels` / `LOG_LEVELS`) is inconsistent.
- **No-Firebase checklists** (iOS, Android) name Firebase Remote Config keys. The iOS no-Firebase Podfile lists push pods.
- **Android Embed View ID** is said to match the "bannerId"; it's likely the embedId.
- **iOS Podfile (p.91):** `private_repo` is defined inside the first target block, so the second target can't use it. Moved above both targets in the knowledge file: the only code changed from the source rather than copied.

### Changed
- `_shared/prerequisites.md`:
  - Org Id is optional in Flutter (visitor flow only).
  - Web writes regions in lowercase.

### Withdrawn
- A suspected Android manifest error (`android:name` outside `<application>`, p.105) turned out to be a PDF text-extraction artifact; the .docx is correct.
