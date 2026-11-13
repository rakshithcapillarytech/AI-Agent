# Knowledge base changelog

## Deep evaluation and fixes (2026-11-13)
A full evaluation of the knowledge base and the kits built from it.
- **Deterministic audit** (`uv run python -m evals.audit_kb`, no model): 11 checks (fences, embedded JSON/YAML, step numbering and references, cross-references, secrets and internal leaks, cross-platform contamination, leftover markers, front matter vs content, prerequisite rules, evals answerable from their kit, 43 kit combinations). Clean. It found sample `@capillarytech.com` emails in four files (replaced with `user@example.com`).
- **Deep question bank** (`evals/deep/`, 348 questions, 10 files, one per platform and mode): every module, every Correction, every Known Issue, open Gaps (honest "not documented"), cross-platform traps, edge cases and shared-file questions. Run blind by an AI assistant that saw only the generated kit; graded by required strings plus a separate judge (`uv run python -m evals.deep_tools prepare | grade | score`). **Score 339/348 (97.4%) raw; 346/348 (99.4%) after loosening seven over-literal answer keys.** The two remaining misses were omissions by the assistant (the guide has the facts). No knowledge-base errors were found by the questions.
- **Fixes from the question writers' review (about 25 inconsistencies):** stale Gaps removed or corrected (own-FCM-service handling is documented for native Android; React Native region values; Android app signature wording), shared vs platform contradictions (config-mode wording in `overview.md`, per-platform remote log level scales, Account Linking Identifier scope, Org Id per platform, the `source not found` cause now stated as documented for the Android signature and likely for bundle ID / Account Id), a wrong variable in the Flutter `updateGeoConfig` sample, the Flutter verification line vs the height correction, `timezone` in the Web traits type, React Native screen reporting after sign-in, Android prerequisites. `_shared/firebase-setup.md` now reaches Flutter (any mode) and Web direct with push (loader change). Flutter `sdk_version` front matter is `null` (latest release).
- The 35 golden evals are all current (two outdated "not documented" cases about Android minSdk and push were replaced).

## Capillary public developer docs merged into all 10 platform files (2026-11-13)
Source: `docs.capillarytech.com/docs/sdks` and its 51 SDK pages (Android, iOS, React Native, Flutter, Web; most updated 2026-03 to 2026-11-12), plus the PST page *Mapp-SDK Related Issues* (2026-10-09). Every page was read in full by five platform reviewers working in parallel (one per platform); the shared files were merged by hand. All `draft`; **many new `⚠️ Correction` callouts (55 in total now) need SME review**, because the public docs sometimes contradict the 2024 PDFs and the internal June 2026 runbook.

### Changed (all 10 platform files)
- **Android:** the core Android + Firebase integration is now documented (19 steps: install, init, sign-in/up/update/out, events, push permission, push handling, rich push, deep links, gamification); push, in-app and inbox for Firebase mode; minSdk 21, target/compile 34; the Embed View binding disagreement resolved (Option A automatic, Option B `bindEmbedView`); gamification minimum `1.9.22-beta02`; campaign TTL pull delivery; own-FCM-service handling.
- **iOS:** full core init (`generate(with:geoData:supportsPushNotifications:deviceScreenInfo:)`), the six frameworks and install (Xcode and CocoaPods), push (APNs, capabilities, App Group, `FirebaseApp.configure`), the Notification Service Extension and rich push, CTA handling, the Inbox and notification centre, 8 more Known Issues. Corrections: repo `hydra-sdk-ios-packages` and `1.7.5-preprod.12`; `SampleView().gamificationScreen(...)`.
- **React Native:** rebuilt on the public docs (steps 1–14 + G1–G4): `@capillarytech/react-native-hydra-lib` from the public npm registry, `Hydra.sharedInstance().initialize` / `Hydra.initialize`, `Hydra.identify` / `reset` / `track`, visitor flow, multi-account, full API reference. Corrections reverse part of this morning's runbook-based rewrite (package name, init API, sign-in API); the runbook's `HydraNativeInitializer` / `HydraInitializer` and `HydraCore.signUp` / `signIn` are now marked as the older way.
- **Flutter:** `capillary_hydra` and `capillary_hydra_platform_interface` from pub.dev (Correction vs the GitHub repo), Firebase as base setup in every mode, `enable_ssl_pinning`, Flutter ≥ 3.3 / iOS ≥ 15 / Android API ≥ 23, push `passFCMToken`, gamification suppress/theme/callbacks, multi-account ordering and persistence, 8 more Known Issues. Corrections: gamification key, region **and** base URL all required; `if (height >= 0)`; `GamificationLoyaltyView(loyaltyId, onHeightChanged)`.
- **Web:** rebuilt around one `sdkService` file from Capillary's AI runbook, with its rules; full push setup (`hydra-fcm` Firebase app, service worker), full gamification (containers, `hookId` / `embedId`, loyalty token, path rules), 14 public methods; six smoke checks and the troubleshooting-page Known Issues. Corrections: `getAnonymousId()` not `getUser()`; all three gamification fields required; `notifications` must carry `messaging`.

### Shared files
- `_shared/push.md`: reachability takes about one day after the first sign-in; a table of **skipped reasons** (Profile Not Found, Unsubscribe, Request Entity Not Found, NotRegistered, HTTP 401, Gateway Not Found); campaign TTL (15 days default); one source account for both OSes; apps that own their `FirebaseMessagingService`.
- `_shared/firebase-setup.md`: **iOS APNs key to Firebase** (steps) and **Android service account** (custom role permissions, JSON key); gamification key table updated (Flutter, React Native, Web: all three required; Android, iOS unchanged).
- `_shared/prerequisites.md`: SDK package access per platform (public npm / pub.dev / Maven Central vs GitHub credentials, with the conflict recorded as a Gap), Org Id per platform, `enable_ssl_pinning`, Gamification Base URL rules.
- `_shared/overview.md`: the order of an integration and behavioural-event setup. `_shared/troubleshooting.md`: the five sign-in checks, signature format, delivery information to collect.
- `prerequisites.yaml`: Firebase project and config files are base setup for **every Flutter mode**; `org_id` also for iOS with Firebase and for React Native with Firebase only with the visitor flow; `rn_package_access` is now a non-blocking "check" item. The SHA256 check accepts Capillary's stored `SHA256 - <64 hex>` form as well as the signing-report form.
- 22 new golden evals in total (35 cases).

### Conflicts recorded as Gaps (need an SME)
- Internal runbook vs public docs: React Native/Flutter package source and credentials; React Native iOS init for the 0.76+ template; whether `enable_push_notification` and the runbook's `HydraContainer` listeners still apply.
- Per-platform differences in gamification mandatory values; whether iOS passes `orgID` in both modes.
- What Capillary needs from Firebase (service account vs Cloud Messaging server key vs project ID and email).
- Version minimums for gamification per platform; AGP / Kotlin / Gradle / Xcode / Swift versions; Java samples for several Android and React Native steps.
- Doc typos kept and labelled (`setNotificationCallbackDelagte`); inconsistent public samples noted per file.

### Not covered
In-app pages for iOS, Flutter and React Native (`in-app-messaging_ios`, `flutter-sdk-in-app-messaging`, `react-native-sdk-in-app-messaging`) were not in the saved set. The Hydra BE auth Google Doc and the Mobile SDK slide deck were not opened. Recordings were skipped.

## React Native rewrite, troubleshooting playbook, endpoints and key expiry: from the MobileSDK pages (2026-11-12)
Source: the Confluence page tree **MobileSDK** (space CAM, read-only), 10 pages: *SDK Agentic Integration For React Native* (the Hydra SDK team's agent runbook, 2026-06-05), *SDK Integration prerequisites* (2026-06-05), *Hydra API endPoint and SSL Key for various clusters* (2026-09-18), *Mobile SDK - PST Guidelines Document* (2026-01-15), *Hydra SDK - Authentication flow with Hydra BE* (2025-10-08), *Debugging using Remote logs on Grafana* (2025-04-22). The other four had no usable text (a slide deck, an empty page, a diagram, and a recording link). All `draft`.

### Changed
- `react-native/direct.md` and `react-native/firebase.md`: core, push, in-app and inbox rewritten from the 2026 runbook (steps 1–14): package access through GitHub Packages and the setup scripts, `@capillary/react-native-hydra-lib`, `hydra-config.json` keys explained, notification icon rules, Podfile with the extension target, Xcode tasks (including the Xcode 26 "Convert to Group" fix and User Script Sandboxing), Notification Service Extension code, AppDelegate init (Swift old / React Native 0.76+ template, Objective-C), Android Gradle and `MainApplication` init (Kotlin, Java), `HydraContainer` listeners, `HydraCore.signUp` / `signIn`, push permission, in-app (SDK or React Native UI), Inbox API and UI, verification checklist, new Known Issues and API reference. `direct` = values in the native init; `firebase` = Firebase Remote Config keys `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level` (or custom names for several accounts). Gamification content from the older guide is kept (Firebase file: steps G1–G4).
- **Corrections** (pending SME): package `@capillary/react-native-hydra-lib`, not `@capillarytech/react-native-hydra-lib@beta`; Podfile path under `@capillary/`. **Superseded the same day by the public developer docs entry below**, which uses `@capillarytech/react-native-hydra-lib` from the public registry.
- `_shared/prerequisites.md`: how registration is requested, **Base URL by cluster** (IN / APAC, SEA, EU, SG / APAC2, North America), **SSL public key expires about every 9 months** (don't hardcode; certificate pinning failure), SDK package access for all platforms with Capillary-issued, expiring tokens.
- `_shared/push.md`: APNs certificate goes into the Firebase Cloud Messaging configuration; Bundle Name gap resolved (the SDK sends its own bundle identifier when authenticating); new common problems (processed but not shown: `HydraFirebaseMessagingService` in the manifest, iOS delegates; low delivery / stuck in SENT; gateway; reachability).
- `_shared/firebase-setup.md`: React Native core Remote Config keys; APNs certificate location.

### Added
- `_shared/troubleshooting.md` (in every kit): what must match between the app and Capillary, how the SDK authenticates and what 400 / 401 / `source not found` / certificate pinning failures mean, package-download problems, remote SDK logs, test help from Capillary, and what to include when escalating.
- `prerequisites.yaml`: `rn_package_access` (React Native, blocking) and `ssl_key_updatable` (all mobile, non-blocking).
- Four golden evals.

### Gaps recorded
- Which init to use with gamification on React Native (older `Hydra.initialize` with gamification values vs the runbook's `HydraInitializer`); sign-out with the 2026 API; whether `enable_push_notification` still exists; `HydraInbox.getInboxMessages()` arguments; minimum versions.
- Package credentials: Capillary-issued token (newer) vs the client's own GitHub account (older guides); Flutter from pub.dev vs `flutter-hydra-lib`.
- No endpoint listed for the `ME` region; how regions map to clusters.
- The manifest entry for `HydraFirebaseMessagingService` and the iOS delegates for native apps; changing a user's identifiers later.

### Deliberately left out
SSL key values (they expire; Capillary provides the current key), internal people, emails and Slack channels, the auth flow's encryption internals, internal ticket numbers and support-team procedures.

### Not covered
The *Mobile SDK* page in the PST space (a recording link) and the 2022 *Mobile-sdk* PRDs in Apps Infra were not read. *Mapp-SDK Related Issues* (PST space, 2026-10-09) looks useful for more common problems.

## Push, registration and signature: from the Engage+ KT Sessions space (2026-11-12)
Source: the Confluence space *Engage+ KT Sessions* (space CAM, read-only), 51 pages. Only two pages have written content that applies to the Hydra SDK: **"Configuration steps and overview of SDK to CRM"** (page 3997892859, updated 2024-10-24, with its data-flow diagram and screenshots) and **"FCM Logs Enablement in Firebase Console"** (page 4148133902, updated 2026-02-17). All `draft`; they need SME review like the other files.

### Added
- `_shared/push.md` (new): how a push reaches a device, what must match between the app and Capillary's registration (Firebase project, App Signature, Bundle Name, Account Linking Identifier, environment values), what Capillary sets up after the client sends their details, an end-to-end test, the sample FCM data payload, FCM delivery reports through BigQuery, and common problems. Loaded by `app/kb/loader.py` when the profile has the `push` module and a push-capable mobile app (Android with Firebase; iOS, React Native and Flutter in either mode).
- Known Issues in all 8 mobile files: the SDK error `Client Credentials Generation Failed … {"error":"source not found","status":400}` (Android: App Signature registered at Capillary doesn't match the build), and "push never arrives although sign-in works" (except `android/direct.md`, which has no push).
- `prerequisites.yaml`: `push_firebase_project` (Firebase project ID and service account for push; non-blocking; never record or share the file in chat) and `android_signature_native` (non-blocking, to be confirmed). `android_sha256` stays blocking for React Native and Flutter, with a clearer description.
- `_shared/prerequisites.md`: the new client items, where the Account Id comes from (the Source Account Id of the MAPP_SDK account) and that the Base URL is cluster-specific. `android/direct.md` and `android/firebase.md`: prerequisites updated.
- Four golden evals for the above.

### Gaps recorded (⚠️ Gap, need an SME)
- Whether native Android needs the app signature (the native guides don't list it; the KT notes show a mismatch breaks SDK start). Which keys count (debug, release, CI, Play App Signing).
- What happens when a build uses a different package or bundle ID than the registered Bundle Name; whether a wrong bundle ID gives the same `source not found` error on iOS.
- How to share the Firebase service-account file securely, and how long the gateway setup takes.
- iOS push through APNs; how the SDK displays the data messages; behaviour when the app has its own FCM messaging service.
- The BigQuery sample queries filter `message_type = 'DISPLAY_NOTIFICATION'` while Capillary's sample is a data message.
- Tokens stored before the app moves to a different Firebase project (implied by the data flow, not stated).

### Deliberately left out
Capillary-internal operations in the source page (database tables, gateway configuration entries, hotswap queries, service restarts, internal ticket numbers, the customer-API test call). They aren't for a client's kit. **The source pages also contain pasted session cookies, tokens and a Basic-auth header in sample calls; they should be scrubbed and rotated by their owners.** None of that was copied.

### Not covered
About 45 pages in the space are meeting recordings (mp4) with no transcript or text and could not be read. The ones that look SDK-related: *SDK registration and onboarding*, *BE*, *Push Notification Session*, *mobile SDK KT to PST* and *DLR KT session* (listed on *SDK Hydra KT Recordings* as: SDK registration and onboarding, BE, push notification composition and triggering, gateway setup, FCM handling, DLRs). The rest of the space is Engage+ campaign, journey, Facebook, WhatsApp/Zalo and similar content, unrelated to the Hydra SDK.

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
