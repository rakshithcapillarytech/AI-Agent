# Android slice: public docs vs knowledge base

Scope: 13 public pages in full (android-sdk, android-sdk-getting-started, configure-firebase, set-up-source-account, configure-gateway, installing-sdk, sdk-initialisation, push-notification, configure-notification-center, gamification-android, android-sdk-api-reference, xiaomi-push-notification, sdks) against `knowledge_base/android/direct.md`, `android/firebase.md`, the Android parts of `_shared/{prerequisites,firebase-setup,push,troubleshooting}.md`, `requirements.yaml`, `prerequisites.yaml`, `faq.yaml`, plus the derived `step_summaries/android.yaml`, `step_modules.yaml`, evals and tests that hard-code the same strings.

Page dates: gamification-android 2026-11-23; configure-firebase 2026-11-16; push-notification 2026-11-16 (all three are after 2026-11-13). android-sdk-getting-started, installing-sdk, set-up-source-account, configure-notification-center, xiaomi-push-notification are dated 2026-11-12 (one day before the merge, yet our front matter cites older dates for several of them, so treat them as unverified). The rest are 2026-03-25 / 2026-08-14.

Note on method: I compared current page text with our KB; I had no copy of the older page text, so "what changed" in section C is inferred from where the KB differs and from the dates our front matter cites.

---

## A. Contradictions (docs and our KB disagree)

**A1. (High) Maven group is `com.capillarytech`, our KB says `com.capillary`.**
- Docs: installing-sdk `from("com.capillarytech:hydra-catalog:1.10.6")`, `implementation("com.capillarytech:hydra-core:1.10.6")`, `hydra-firebase`, `hydra-pushbase`; push-notification `com.capillarytech:hydra-richnotification:1.10.6`; configure-notification-center `com.capillarytech:hydra-inbox-core:1.10.6`; gamification-android Option B `com.capillarytech:hydra-core|hydra-inapp|hydra-inbox-*|hydra-gamification|hydra-gamification-ui`; xiaomi `com.capillarytech:hydra-mi-push-kit:1.10.6`. Five pages agree.
- Ours: `android/direct.md` front matter `sdk_package`, step 3 (all 12 coordinates), Known Issues, API table; `android/firebase.md` front matter, steps 2, 3, 13, Modules (Xiaomi, In-App, Inbox), Known Issues. `react-native/*.md` and `_shared/prerequisites.md` already say `com.capillarytech:hydra-*` for the same SDK family.
- Effect: Gradle cannot resolve `com.capillary:hydra-core`; every copy-pasted dependency line fails.
- Change: replace `com.capillary:` with `com.capillarytech:` in every dependency coordinate (both files, `sdk_package`, step_summaries, evals, tests, `_template/platform.md`). Confidence high on the docs; if an SME knows an older group is still published, keep it only as a Gap.

**A2. (High) Java/Kotlin and XML class packages are `com.capillarytech.hydra.*`, ours are `com.capillary.hydra.*`.**
- Docs: push-notification manifest `android:name="com.capillarytech.hydra.firebase.HydraFirebaseMessagingService"`; imports `com.capillarytech.hydra.sdk.entity.Token`, `com.capillarytech.hydra.sdk.listeners.TokenAvailableListener`, `com.capillarytech.hydra.firebase.NonHydraPushListener`; gamification-android `<com.capillarytech.hydra.gamification.ui.entrypoints.BannerView|EmbedWebView|LoyaltyEmbedView>` (Option A and B).
- Ours: `android/firebase.md` step 10 (manifest service), step 12 (two import lines, one Java import), Modules › Gamification XML, API Reference table; `android/direct.md` Modules › Gamification XML (3 tags) and API table.
- Effect: manifest service not found (SDK never receives FCM), layout inflation `ClassNotFoundException` for the gamification views.
- Change: replace with `com.capillarytech.hydra...` everywhere. `_shared/push.md` names the service without a package, so it needs no edit.

**A3. (High) SDK version: docs say `1.10.6` for every module, ours say `1.9.22-beta02` (Beta) with a `1.9.20` Gap.**
- Docs: android-sdk-getting-started table, all eight modules `1.10.6`; gamification-android callout "Minimum SDK version: `1.10.6`"; Option B and installing-sdk samples use `1.10.6`; xiaomi `1.10.6`. No beta label anywhere.
- Ours: both files' front matter `sdk_version: 1.9.22-beta02`; `{{sdk_version}}` "(Beta, for UAT/POC) or later"; firebase.md Requirements `⚠️ Correction` (beta02 not beta01) and the `1.9.20` Gap; requirements.yaml note "Beta, for UAT and POC".
- Effect: integrators pin an old beta, below the documented gamification minimum.
- Change: set `sdk_version: 1.10.6` in both files; delete "Beta, for UAT/POC"; delete the `1.9.20` Gap (resolved: one version for all modules); rewrite or delete the beta01/beta02 Correction (it came from the internal Integration doc; public docs now supersede it, so note "internal doc said beta02, public docs say 1.10.6, confirm with SME"). Update `requirements.yaml` and the tests listed in F1.

**A4. (High) Firebase service-account role: docs now give a least-privilege recipe, ours is an old 11-permission list.**
- Docs (configure-firebase, step 4): dedicated service account, "Don't reuse an existing service account"; role `roles/firebasecloudmessaging.admin`, or a custom role with only `cloudmessaging.messages.create`; "Don't use the Owner, Editor, or Firebase Admin roles."
- Ours: `_shared/firebase-setup.md` §7 step 1 "custom role with these permissions" listing 11 (`fcmdata.deliverydata.list`, `firebase.clients.get/list`, `firebasenotifications.messages.create/delete/get/list/update`, `iam.serviceAccounts.get`, ...). Nothing about a dedicated account or forbidden roles.
- Change: rewrite §7 to the docs' recipe (dedicated account, the two role options, the three forbidden roles). Keep the old 11-permission list only as a Gap ("older page; unclear if delivery-report or notification-API features still need them"). Confidence high that docs and KB differ; medium on whether the extra permissions are still needed for anything.

**A5. (High) Stale Gap: "the push page lists an FCM server API key", the push page now lists the service-account private key.**
- Docs: push-notification "# Prerequisite": "The Capillary backend needs a Firebase service-account private key... see Configure Firebase". No server key anywhere; configure-firebase says Capillary uses the FCM HTTP v1 API (`https://fcm.googleapis.com/v1/projects/<project-id>/messages:send`, scope `firebase.messaging`).
- Ours: `android/firebase.md` Prerequisites Gap (line 53); `_shared/firebase-setup.md` §7 Gap (line 85, names "Android and iOS push pages"); also CHANGELOG/REVIEW.
- Effect: an integrator may hand over a legacy Cloud Messaging server key, which cannot authenticate against the v1 API.
- Change: for Android, delete the Gap and state "Capillary needs the service account (see §7); a server key is not used". Keep the server-key caveat only for iOS until the iOS page is re-checked (outside this slice).

**A6. (Medium) "How to share the key isn't documented" is no longer true.**
- Docs (configure-firebase step 6): one-time link from an enterprise password manager or secrets vault (1Password, HashiCorp Vault), restricted to the recipient's email, expiring in 24 to 48 hours, single view; or a restricted link from an enterprise file-sharing platform (OneDrive, Google Drive), shared only with the recipient's email, expiry date, access removed after Capillary confirms.
- Ours: `_shared/push.md` Gap "the channel for sharing the service-account file... aren't documented"; `_shared/firebase-setup.md` §7 step 3 and `prerequisites.yaml › push_firebase_project` say "the secure channel the Capillary contact names".
- Change: add the two documented methods and their constraints; reduce the Gap to "how long gateway setup takes". Keep "never chat, email, ticket or git".

**A7. (Medium) App signature: the source-account page lists it as required for Android; our Gap says the native guides don't list it.**
- Docs: set-up-source-account "App signature - Enter the app signature. This is required only for Android apps. Contact the app developer for the app signature." Getting Started and gamification Option B prerequisites still name only the application ID.
- Ours: `android/direct.md` Prerequisites + Gap; `_shared/prerequisites.md` Gap; `prerequisites.yaml › android_signature_native` ("to be confirmed", `blocking: false`).
- Change: reword the Gaps to "the source-account page (set-up-source-account) says the app signature is required for Android; the install guides don't repeat it". Make `android_signature_native` non-tentative and blocking like `android_sha256` (the KT notes already show a mismatch stops the SDK). Cite set-up-source-account in `sources`.

**A8. (Medium) `hydra-mi-push-kit` version: docs give `1.10.6`, ours says `x.x.x` and "version isn't listed".**
- Docs: xiaomi-push-notification `implementation("com.capillarytech:hydra-mi-push-kit:1.10.6")`. (Getting Started's table still omits this module, which is the real doc gap, see E2.)
- Ours: `android/firebase.md` Modules › Push › Xiaomi step 3 and the Gap below it.
- Change: use `com.capillarytech:hydra-mi-push-kit:1.10.6` and reword the Gap to "missing from Getting Started table, given on the Xiaomi page".

**A9. (Medium) `android_repo_access` applies to direct mode only, but the Firebase install path needs the same GitHub credentials.**
- Docs: installing-sdk (the Firebase/catalog path) adds the `maven.pkg.github.com/Capillary/hydra-sdk-android-maven` repository and a `github.properties` with username and token.
- Ours: `prerequisites.yaml › android_repo_access` `when: platforms: [android/direct]`; `android/firebase.md` Prerequisites and steps 1 to 2 do require it.
- Change: `platforms: [android]` (both modes). See F3.

---

## B. Missing from our KB (in the docs, important for integrators, absent from our guides)

**B1. (High) Enable the "Firebase Cloud Messaging API (V1)" for the project.**
- Docs: configure-firebase step 3 "Turn on the Firebase Cloud Messaging API (V1) for the project."
- Ours: absent from `_shared/firebase-setup.md` §7, `_shared/push.md`, `android/firebase.md` step 4, `prerequisites.yaml`.
- Effect: Capillary's v1 sends fail until the API is on.
- Change: add as a numbered sub-step in `firebase-setup.md` §7 (before creating the service account); mention in `android/firebase.md` step 4 (no new numbered step, see F4).

**B2. (Medium) The private key belongs only to the Capillary backend, never in the app.**
- Docs: configure-firebase Note: "Only the Capillary backend needs the service-account private key. Your Android app, iOS app, and website don't need it and must never contain it"; apps use `google-services.json` (Android).
- Ours: `_shared/push.md` and firebase-setup only say "never in chat, email, git".
- Change: add one sentence to `android/firebase.md` step 4 and `_shared/push.md` (what the app does ship: `google-services.json`).

**B3. (Medium) Missing key / wrong account causes HTTP 401 on every send.**
- Docs: configure-firebase "Without the private key, Google doesn't issue a token, so every send is rejected with 401 Unauthorized"; Google tokens last about an hour.
- Ours: `_shared/push.md` skipped-reason `HTTP 401` says only "credentials have expired". 
- Change: extend that row and `faq.yaml › push-skipped-reasons`: also check the key was shared, belongs to the registered project's dedicated service account, was not deleted or rotated, and the account holds one of the two roles.

**B4. (Medium) Game and CMS event payloads (seven events) and their field mapping.**
- Docs (gamification-android, new section): `game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed`; `cuid` required on every event, `event_name` always sent, flat JSON, numbers as numbers; per-event attributes (e.g. `campaign_id`, `game_type` values, `entry_surface` popup/floating_icon/modal/banner_embedded, `load_time_ms`, `total_time_ms`, `reward_type`, `content_surface`, `page_id`). Field mapping when creating the events: `cuid`→`customerId`, `identifierType` (mobile/email/externalId), `source`=SDK, `accountId`=SDK account ID; "All four are required".
- Ours: absent in both Android files (the web guides only list the seven names, `web/direct.md` line 411).
- Change: add a compact "Gamification events" subsection under Modules › Gamification in both Android files (event table, required fields, the four mapping rules). Not a numbered step.

**B5. (Medium) Sample `subscriptions` payload for `pushUserSignup`.**
- Docs (set-up-source-account): `{"channel":"ANDROID","accountId":"~2024ba96","priority":"BULK","type":"OPTIN","sourceName":"MAPP_SDK"}` (iOS: `"channel":"iOS"`); api-reference only lists the keys "channel, accountId, priority, type and sourcename".
- Ours: both files list the keys only.
- Change: add the sample and say the `accountId` is the Source Account Id. Note the casing mismatch (`ANDROID` vs `iOS`) as a docs quirk (E).

**B6. (Low) Source-account field notes.** FCM Project ID is under *Project settings > General*; FCM Email is the service-account email on the service-account page; "Enable Mirror - Not required"; Account Linking Identifier options are the same for every org. `_shared/push.md` has most; add the two lookup locations.

**B7. (Low) Gateway scopes and who does the work.** configure-gateway: four FCM gateways (android/ios x bulk/trans); `campaign` scope is bulk, `optout`, `otp`, `highvoltrans`, `transaction` are high-priority transactional; "As an SDK-integrating developer, you do not need to perform these steps". Our `_shared/push.md` says Capillary sets up the gateways but not the bulk/transactional split or that the developer does nothing. Add one line; leave out the DPMG and SQL details (internal).

**B8. (Low, needs SME) Behavioural-event samples carry `event_name` and `customerId` inside the attributes map.**
- Docs (api-reference › Adding behavioural events): `pushEvent("productReviewedMapp", mapOf("event_name" to ..., "customerId" to ..., ...))`; the page also says behavioural events need configuration "in the Hydraconfig", but shows no such setting.
- Ours: step 8 (both files) uses only free attributes.
- Change: add a Gap: whether `event_name` / `customerId` must be repeated in attributes, and what "configure in HydraConfig" means. Confidence low that anything is required.

---

## C. Changed since 2026-11-13 (pages dated on or after that day)

**C1. configure-firebase (2026-11-16). Not reflected.** Our front matter cites 2026-03-04. New or changed: FCM HTTP v1 explanation and scope; "private key only for the backend" note; step 3 FCM API V1; step 4 dedicated service account with explicit roles and forbidden roles; step 6 key-sharing methods; "Gateway Configuration" section (the brand's Firebase team raises a ticket with the gateways team). Our reaction needed: A4, A6, B1, B2, B3.

**C2. push-notification (2026-11-16). Partly reflected.** Our front matter cites 2026-08-03. Prerequisite changed from a server key to the service-account private key (not reflected, A5). Class names on the page are `com.capillarytech...` (not reflected, A2). The campaign TTL section (15 days default, org-level, pull on app open, applies to promotional and transactional) is reflected in `android/firebase.md` Modules › Push and `_shared/push.md`. Everything else I checked (requestPushPermission, `FcmConfig(true/false)`, `passPushToken`, `passPushPayload`, `isFromHydraPlatform`, `NotificationConfig`, listener signatures, CTAs, deep-link intent filter) matches.

**C3. gamification-android (2026-11-23). Not reflected.** Our front matter cites 2026-08-18. Differences found: minimum SDK `1.10.6` (A3); `com.capillarytech` coordinates and view packages (A1, A2); the whole "Game and CMS event payloads" section (B4). Option A/B steps, `updateRemoteConfig`, `bindEmbedView` (Option B only), `setCapToken`, lifecycle wiring and the "no Google Services plugin" rule match our KB. Confidence: medium on exactly what moved since 08-18, high on the present differences.

**C4. Pages dated 2026-11-12 where our KB cites older dates or older content:** android-sdk-getting-started (KB says `1.9.20`, page says `1.10.6`), installing-sdk (coordinates and catalog version), configure-notification-center (cited 2026-03-25; only the coordinate/version differs, rest matches), xiaomi-push-notification (cited 2026-03-25; version and coordinate differ, procedure matches), set-up-source-account (not cited at all). Re-verify these against the live pages; the KB may have been built from a cached copy.

---

## D. Pages or sections we don't use at all (and whether we should)

**D1. set-up-source-account: not cited as a source anywhere.** Should be: it is the only public page listing the source-account fields, the App Signature requirement for Android and the single-source-account rule. `_shared/push.md` carries the content from KT notes; add the page to its `sources` and reconcile (A7, B5, B6).

**D2. configure-gateway: not cited.** Capillary-internal setup (DPMG entries, hotswap SQL, restart). Do not copy the table. Do add the one-line "developer does nothing, contact CSM" and the bulk/trans scope split (B7).

**D3. android-sdk (landing) and sdks:** navigation only, nothing to add. The landing page confirms the page order, including "Configure In-app Messaging" (`in-app-messaging`, outside this slice) which Getting Started's 7-step list omits.

**D4. configure-notification-center "Use Case: Retail Loyalty Program" and the benefits list:** marketing text, skip.

**D5. Gamification Option A vs Option B full code:** already covered; no unused sections apart from B4.

---

## E. Problems in the docs themselves (keep as Gap callouts)

**E1. (Medium) Gamification dependencies: "bundled in HydraCore" vs separate artifacts.** gamification-android intro and Option A say HydraGamification is bundled in HydraCore with no extra dependency; Option B adds `hydra-gamification` and `hydra-gamification-ui` at 1.10.6. Neither artifact is in Getting Started's module table or the catalog. Our `android/direct.md` step 3 lists them without a Gap (the CHANGELOG records it, the file does not). Add a Gap to direct.md step 3.

**E2. (Medium) Getting Started module table is incomplete.** Missing `hydra-mi-push-kit`, `hydra-gamification`, `hydra-gamification-ui`, all of which other pages use at 1.10.6. Gap in firebase.md (reword the existing one, A8) and direct.md.

**E3. (Medium) installing-sdk snippets are not copy-pasteable.** The `maven {}` block uses undefined `props` (never loaded from `github.properties`; the gamification page loads it with `Properties()`), curly quotes `props['username’]` / `props[‘username’]`, an angle-bracket URL `"<https://maven.pkg.github.com/...>"`, Groovy `url "..."` inside a block labelled `kotlin`, and a misaligned `password` line. Our KB correctly uses the gamification page's version; add a Gap saying why.

**E4. (Medium) `Map.of(...)` in the Java samples.** api-reference and `android/direct.md` step 7 Java use `Map.of("Age","25","Gender","Male")` (also `pushUserUpdate`, `pushEvent`). `Map.of` needs Android API 30+, but the docs set minSdk 21 (NoSuchMethodError on older devices). Confidence medium-high. Change: use `new HashMap<>()` in our Java snippet (direct.md line 278) and add a Gap.

**E5. (Low) Gradle 7.4 overlap.** installing-sdk says the version catalog is a preview "for Gradle 7.4 and below" and enabled by default "for 7.4 and above". Our KB and requirements.yaml say preview on 7.4 and below, default from 7.4 (matches Gradle's real behaviour, not the page text).

**E6. (Low) Without-catalog install puts `maven {}` in the project-level `repositories`**, while every other snippet sets `FAIL_ON_PROJECT_REPOS` in settings (project-level repositories then fail the build). Xiaomi page also sets both `FAIL_ON_PROJECT_REPOS` and `PREFER_SETTINGS` back to back. Mention in firebase.md step 2.

**E7. (Medium) Who performs Firebase setup is unclear.** Getting Started step 1 "Configure Firebase and gateway - Capillary mobile apps team"; configure-firebase's steps (create project, service account, key) are done in the brand's own Firebase console ("the team setting up the Firebase account for the brand must raise a ticket with the gateways team"); configure-gateway says developers do not do gateway steps. Our overview.md says the client's mobile team does Firebase and Capillary the gateway, which is the likeliest reading; add a Gap.

**E8. (Low) sdk-initialisation:** `.fcmConfig` and `.notificationConfig` are marked "Optional (If not using Firebase SDK)", which contradicts push-notification (`FcmConfig(true)` is used when the SDK handles FCM with Firebase). `baseURL` and `sslPublicKey` are "Optional" although the other pages treat them as required values. Already partly recorded (Java builder styles); add these two.

**E9. (Low) set-up-source-account:** "Source Account Id - Displays the service account id" (it is not the Firebase service account); the sample payloads use `"channel": "iOS"` (mixed case) and `"ANDROID"`; the Bundle-name `android:...;ios:...` format only appears in the field description, not in the paragraph that introduces it.

**E10. (Low) api-reference:** `passUserPreferences` table says `cuid` is Optional ("If null, uses the stored CUID") but the Kotlin signature is a non-null `String`; `initializeConsoleLogger(LogType.Debug)` vs `LogType.DEBUG` (already recorded); event parameter documented as `event_name`, signature uses `eventName`.

**E11. (Low) configure-notification-center:** headings `getUnreadNotificationCount` / `deleteInboxMessages` vs methods `getUnReadMessagesCount` / `deleteInboxMessage`; "register an `InboxMessageListener` to receive in-app message callbacks" is a copy-paste from the in-app page; read-state timestamp style is `bold`; Kotlin click listener passes `cta` (recorded). 

**E12. (Low) push-notification:** prose says `HydraPushAPI`, `HydraFirebaseApi` (recorded); `addNonHydraPushListener()` shown with no argument in the Kotlin prose block; `onNonHydraPushReceived` vs `onPushReceived` (recorded); rich push "available from Hydra SDK 1.2.0 and RichNotification 1.0.0" next to a table giving everything `1.10.6`.

**E13. (Low) gamification-android leaks authoring notes** ("TBD - confirm with dev", "The source guide only shows this wiring in Kotlin"), and the Option B checklist lists the `hydra_gamification_*` Remote Config keys although the page says Firebase is not used. Both are already in our files as a Gap and a Correction; keep them.

**E14. (Low, outside the docs, medium confidence) `targetSdkVersion 34`/`compileSdkVersion 34`** are stated as prerequisites; Google Play has required newer target levels for new submissions since 2025. Our guides repeat 34 as "the requirement"; add a note that it is the documented minimum, not a ceiling. Confirm with an SME.

---

## F. Impact on derived files

**F1. requirements.yaml (High).** `versions › Hydra SDK version`: `check: "1.9.22-beta02"` and `note: Beta, for UAT and POC` must change with A3 (`check: "1.10.6"`). Dependent hard-coded strings: `tests/test_requirements.py:87` (`startswith("1.9.22-beta02")`), `tests/test_humanguide.py:80`, `evals/golden.yaml:55`, `evals/deep/android-firebase.yaml:25-30`. minSdk 21, target/compile 34, Gradle catalog and Firebase account items still match the docs.

**F2. step_summaries/android.yaml (High).** `android/direct` step 3 and `android/firebase` step 3: `do` text and `evidence` strings `"com.capillary:hydra-core"`, `"com.capillary:hydra-firebase"` must change with A1 (the evidence strings must still appear in the guide). Step 10 `do` unchanged but the underlying manifest XML changes (A2).

**F3. prerequisites.yaml (Medium).** (a) `android_repo_access`: `when: [android/direct]` should cover both modes (A9). (b) `android_signature_native`: drop "to be confirmed", make blocking (A7). (c) `push_firebase_project`: `how` should say dedicated service account, role (`roles/firebasecloudmessaging.admin` or custom `cloudmessaging.messages.create`), FCM API V1 enabled, and the two sharing methods (A4, A6, B1). (d) `firebase_project`: optionally add FCM V1. Tests reference `android_repo_access` as a direct-mode item (`tests/test_prereq_tools.py`, `tests/test_graph_smoke.py`), so check them when widening.

**F4. step_modules.yaml (Low).** Titles still match. To avoid breaking it and step_summaries, put the new FCM V1/service-account and event-payload content inside existing step 4 and Modules sections rather than adding numbered steps (a new step would renumber 5 to 19 in `android/firebase`).

**F5. faq.yaml (Medium).** `share-secrets`: add the documented methods (one-time or restricted link, recipient-only, expiry). `push-skipped-reasons` (HTTP 401 line): add missing/rotated key (B3). Add two FAQs: "What does Capillary need from my Firebase project?" (service account with one of two roles, FCM V1 enabled, not a server key) and "Which role should the service account have?". `android-gradle-401` and the evidence strings are unaffected, but if any evidence quotes `com.capillary:` text it must be updated (none found in faq.yaml).

**F6. Tests and evals that hard-code old strings (Medium).** `evals/golden.yaml:45` (`Could not resolve com.capillary:hydra-core`), `evals/deep/android-direct.yaml:39, 215` (`com.capillary.hydra.gamification.ui.entrypoints` in `contains`), `tests/test_kb_search.py:17` (query string with `com.capillary:hydra-core`; harmless if the KB still contains the same token in Known Issues, but rewrite for the new group), `_template/platform.md` `sdk_package`. Fixtures in `tests/test_kb_lint.py` and `tests/test_kb_loader.py` are synthetic and can stay.

**F7. Shared files (Medium).** `_shared/firebase-setup.md` §7 and Gap (A4, A5, B1); `_shared/push.md` Gaps and HTTP 401 row (A5, A6, B3); `_shared/prerequisites.md` signature Gap (A7); `_shared/overview.md › Versions` ("UAT / POC uses the beta SDK builds where a platform file names one") is no longer true for Android once A3 lands.

---

## G. Confirmed matching (verified identical in both)

- Getting Started: Android SDK V21 or above (our "minSdk 21"), targetSdkVersion 34, compileSdkVersion 34, Google Firebase account; step order (Firebase+gateway by Capillary mobile apps team, source account by CSM/PM, install, init, push, APIs, gamification).
- Repository `https://maven.pkg.github.com/Capillary/hydra-sdk-android-maven`, `github.properties` with `username`/`token`, classic PAT with `read:packages`, `dependencyResolutionManagement` + `FAIL_ON_PROJECT_REPOS` snippets (Groovy and Kotlin DSL), version catalog name `hydra`, `enableFeaturePreview("VERSION_CATALOGS")` for Gradle < 7.4, accessors `hydra.core`, `hydra.pushbase`, `hydra.firebase`, AndroidX libs (`core`, `appcompat`, `lifecycle-process`, versions `xxx`).
- `HydraConfig.Builder` options and defaults (debugLevel OFF -1/INFO 0/DEBUG 1/VERBOSE 2; remoteDebugLevel OFF/INFO/DEBUG; `accountId` mandatory and throws if missing; all else optional), `instanceWithConfig(context, config): HydraAPI`, call in `Application.onCreate()`.
- Sign-in/up/update/out signatures, `pushEvent`, `passUserPreferences` (`promPushOpted`, `transPushOpted`), events valid only after sign-in/up and invalid after sign-out, behavioural events created at *Organisation settings > Master Data Management > Data Model > Behavioural events*.
- Push: `requestPushPermission` (Android 13+), `FcmConfig(true/false)`, `HydraFirebaseMessagingService` manifest entry (apart from package, A2), `passPushToken` on `onNewToken` with the three token-change scenarios, `isFromHydraPlatform` then `passPushPayload`, `NotificationConfig(smallIcon, notificationColor, isMultipleNotificationInDrawerEnabled=true default)`, mandatory `HydraPushNotificationListener` with five callbacks and `onNotificationClick` true/false semantics, token and non-Hydra listeners, primary CTA (launcher activity fallback), up to 3 non-primary CTAs, deep-link intent filter, campaign TTL 15 days default.
- Rich push, In-App, Inbox: catalog accessors `hydra.richnotification`, `hydra.inbox.core`, `hydra.inbox.ui`; `NotificationCenterConfig(@DrawableRes defaultImage)` mandatory; `InboxActivity`, `InboxFragment`, `HydraInboxUIHelper.registerOnMessageClickListener`, the five `HydraInboxCoreApi` methods; the style and colour resource names.
- Alarm permission helpers (`canScheduleExactAlarms`, `requestExactAlarmPermission`, `logExactAlarmStatus`).
- Gamification: Option A keys `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url` (optional), conditional builder code, `GamificationRegion.valueOf(region.uppercase())`, `updateRemoteConfig` signature, `GamificationUIManager` wiring and lifecycle callbacks, `onActivityDestroyed` for leaks, `ProcessLifecycleOwner` observer, `GamificationCallback` methods, `setCapToken`, Option B builder methods and `GamificationRegion.IN/.US/.ME`, "no `com.google.gms.google-services`, no Firebase dependencies, no `google-services.json`", explicit `bindEmbedView` only in Option B, push not available in Option B.
- Xiaomi: deprecation notice, flatDir/`fileTree` setup, `PREFER_SETTINGS`, helper repo `https://github.com/Capillary/push-amp-plus`, package `com.hydra.sdk.miPushKit`, receiver and three intent actions, `MiPushHelper.initialiseMiPush`, `HydraMiPushApi` calls.
- Source account: path *Organisation settings > Omni Channel Settings > Channel Configurations > MAPP_SDK*; one account for iOS and Android with semicolon-separated Bundle name; FCM Project ID and FCM Email; Enable Mirror not required; optional deep links; no effect on subscription status when merging accounts.

---

## Summary

The biggest drift is naming and versions: the public docs now use the `com.capillarytech` Maven group and `com.capillarytech.hydra.*` class packages and a single SDK version `1.10.6` (no beta), while both Android guides, `step_summaries/android.yaml`, `requirements.yaml`, evals and tests still carry `com.capillary...` and `1.9.22-beta02`; copied dependency lines, the manifest service and the gamification view tags would all fail. The second cluster is Firebase: the November 16 pages replace the server-key prerequisite with a dedicated service account (role `roles/firebasecloudmessaging.admin` or `cloudmessaging.messages.create` only, FCM API V1 enabled, key shared through a one-time or restricted link), so `_shared/firebase-setup.md` section 7, `_shared/push.md` and two Gaps are stale. New content missing from our guides is the Game/CMS event payload section; the rest is smaller (source-account details, gateway split, App Signature now documented as required for Android, hydra-mi-push-kit version, repo access missing for Firebase mode in `prerequisites.yaml`). Docs defects worth keeping as Gaps include the non-runnable installing-sdk Maven snippet, `Map.of` below API 30, bundled-vs-separate gamification artifacts and unclear ownership of the Firebase step.

Counts: A 9 (High 5, Medium 4: A1-A5 High, A6-A9 Medium); B 8 (High 1, Medium 4, Low 3); C 4; D 5; E 14 (Medium 5, Low 9); F 7; G 10 groups of verified facts.
