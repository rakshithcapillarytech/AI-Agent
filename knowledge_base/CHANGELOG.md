# Knowledge base changelog

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
