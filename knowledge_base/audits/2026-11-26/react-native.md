# React Native: audit of knowledge_base against docs.capillarytech.com (read-only audit, 2026-11-26)

Scope: 10 public pages in the slice (all read in full) vs `knowledge_base/react-native/direct.md`, `react-native/firebase.md`, the React Native parts of `_shared/{prerequisites,firebase-setup,push,troubleshooting,overview}.md`, `requirements.yaml`, `prerequisites.yaml`, `faq.yaml`, `step_summaries/react-native.yaml`, `step_modules.yaml`, and `app/kb/loader.py` (read only, to confirm which shared files load).
Extra page fetched by me: `react-native-sdk-in-app-messaging` (linked from two slice pages but absent from the downloaded set; HTTP 200, saved at `.../scratchpad/rn_extra/rn-inapp.md`, updatedAt 2026-11-12).

Headline: our two RN files are in very close sync with the 2026-11-12 pages (every API signature, config key, default, Podfile/AppDelegate/Gradle snippet, enum and class I checked matches). The only page changed on/after 2026-11-13 is `gamification-react-native` (2026-11-23), which added a large "Game and CMS event payloads" section that our KB does not have and whose absence makes one of our Gap callouts stale. The remaining issues are in derived files (prerequisites.yaml) and in a few Gap callouts that the docs now partly answer.

## A. Contradictions (docs and our KB disagree)

**A1. Stale Gap: gamification event names and payloads are now documented. Severity: Medium (confidence high).**
- Docs: `gamification-react-native` (updated 2026-11-23) now has "Game and CMS event payloads": seven events (`game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed`) with attribute tables and sample payloads.
- Ours: `react-native/direct.md` and `react-native/firebase.md` › Modules › Gamification: "Gap: event and analytics-event names and payload contents aren't documented."
- Change: narrow the Gap. Event names and payloads for the seven Experience+ events are documented; what is still not stated is which `name` / `payload` values `addGamificationEventTriggerListener` and `addGamificationAnalyticsEventListener` actually deliver (the page does not link the two). Add the new content per B1/B2.

**A2. Org Id is required for React Native direct mode in prerequisites.yaml, but the docs say it is optional (visitor flow only). Severity: Medium (confidence medium-high).**
- Docs: `react-native-sdk-advanced-setup`: orgId "optional ... required only for the Anonymous/Visitor Flow", "Pass `nil` if unused" (iOS and Android tables). `react-native-sdk-getting-started`: "If you plan to use the Anonymous/Visitor Flow, the apps team also provides: Org Id".
- Ours: `prerequisites.yaml` item `org_id` lists `react-native/direct` with no module condition and `blocking: true`; `_shared/prerequisites.md` Org Id row says "native direct-mode init (Android, iOS, React Native) ... React Native passes it in direct mode generally". Our own `react-native/direct.md` correctly says orgId is only for the visitor flow, so the yaml contradicts the guide too.
- Change: in `prerequisites.yaml` move `react-native/direct` into the `modules: [visitor]` entry (with `flutter`, `react-native/firebase`); rewrite the `_shared/prerequisites.md` Org Id row. Keep a Gap only if an SME confirms the runbook needs it. Also update the `short` text of `org_id`.

**A3. Step 3 starter `hydra-config.json` differs from the documented defaults and from the no-push config. Severity: Low (confidence high).**
- Docs: `react-native-sdk-install`: `enable_inbox_api` default `false`; example lists `enable_push_notification` and `enable_ssl_pinning` explicitly. `react-native-sdk-advanced-setup`: without Firebase, `enable_hydra_sdk_firebase_registration`, `enable_inbox_api`, `enable_in_app_messaging`, `enable_inbox_ui` must all be `false` and `enable_push_notification: false`.
- Ours: `direct.md` and `firebase.md` step 3 starter sets `enable_inbox_api: true` and `enable_hydra_sdk_firebase_registration: true`, omits `enable_push_notification`/`enable_ssl_pinning` (the table covers them), and adds the runbook-only `enable_in_app_messaging_in_react_native`. Correct no-push JSON exists only under Modules › Push › Without Firebase.
- Change: add one line under the starter JSON: "No push or no Firebase: use the JSON under Modules › Push › Without Firebase instead" and mention that the Inbox API on iOS needs the Notification Service Extension and App Group. Optional: add `"enable_push_notification": true` to the starter for clarity.

**A4. `_shared/push.md` Gap about the React Native manifest entry is partly answered. Severity: Low (confidence medium).**
- Docs: `react-native-sdk-advanced-setup`: "With push off, Android uses a manifest without the Firebase messaging service of Hydra"; `react-native-sdk-install` `enable_push_notification`: "Android also swaps in a manifest variant without the Firebase notification icon meta-data". This implies the package supplies the Hydra messaging service itself when push is on, so no manual manifest entry is documented or needed.
- Ours: `_shared/push.md` (line ~90): "neither is the `HydraFirebaseMessagingService` manifest entry for React Native and Flutter apps" documented; line ~64 says apps owning their `FirebaseMessagingService` "must hand tokens and payloads to the SDK ... `passFCMToken` in React Native". The RN docs document tokens only (`passFCMToken`); there is no RN API for forwarding payloads.
- Change: reword for React Native: "the package ships the Hydra messaging service in its own manifest; with your own `FirebaseMessagingService` only tokens are handed over (`passFCMToken`); how payloads reach Hydra is not documented. Ask a Capillary engineer."

## B. Missing from our KB (in the docs, important for integrators, absent from our guides)

**B1. The seven Game and CMS event payloads (names, attributes, types, required flags, sample payloads). Severity: Medium (confidence high).**
- Docs: `gamification-react-native` › "Game and CMS event payloads": `cuid` is required on every event, all other attributes optional; flat JSON; numbers sent as numbers. Attributes: `campaign_id`, `game_type`, `entry_surface` (popup, floating_icon, modal, banner_embedded), `embed_id`, `entry_point_id`, `entry_point_location`, `deep_link_url`, `hyper_link_url`, `load_time_ms`, `total_time_ms`, `reward_id`, `reward_type`, `content_surface` (widget, banner, full_page), `page_id`.
- Ours: absent (only `web/direct.md` / `web/firebase.md` list the seven names, with no attributes).
- Change: add a compact "Gamification events" table under Modules › Gamification in both RN files (event, when it fires, attributes; mark `cuid` required). Do not add as numbered steps (see F5). Do not invent which listener emits them (see E1).

**B2. Event creation and Field mapping: four required fields. Severity: High (confidence medium-high).**
- Docs: `gamification-react-native` › "Field mapping": "When creating the events, map the event fields ... All four are required." `customerId` <- `cuid`; `identifierType` <- identifier passed to the SDK (mobile, email or externalId); `source` = SDK; `accountId` = SDK account ID.
- Ours: absent for React Native. `_shared/overview.md` line 41 only says behavioural events must exist in Capillary before the app sends them, with no mapping rules, and `events-missing` FAQ does not mention these.
- Why it matters: if the Capillary-side events are created without the mapping, the gamification events probably will not be recorded against the customer. The docs do not say where in Capillary the events are created or who does it (the client or Capillary), so say so in a Gap.
- Change: add the Field mapping table to Modules › Gamification plus a Gap ("where the events are created, and whether this is a client step, isn't stated"). Add to `_shared/overview.md` next to the behavioural events sentence. Consider a non-blocking prerequisite item (see F3) once an SME confirms.

## C. Changed since 2026-11-13 (pages dated on/after that day)

**C1. `gamification-react-native` (updatedAt 2026-11-23): new "Game and CMS event payloads" section (+ Field mapping). Severity: Medium. Our KB does not reflect it.**
- Every other part of this page matches our RN Gamification content exactly (Android FCM token callout, screen reporting, height listener, suppression, theme, three listeners, embeddable views table, sample code, "height 0 means collapse", `openExternalUrl` warning). The new content is lines ~53-267 of the page: summary table of 7 events, per-event attribute tables and JSON samples, Field mapping table. Nothing in the older text was removed that our KB relies on.
- The same section was added the same day to `gamification-android`, `-ios`, `-flutter`, `-web` (not in my slice); only Web in our KB lists the event names.
- Change: see A1, B1, B2.

**C2. Front matter `sources` in `react-native/direct.md` and `firebase.md` say "gamification-react-native 2026-11-12". Severity: Low.**
- Change: update to 2026-11-23 and add the new section to the description once B1/B2 are merged.

**C3. The other 9 slice pages are dated 2026-11-12 (before the 11-13 merge). Severity: none.**
- I re-checked their facts against our files (see G); nothing new to merge.

## D. Pages or sections we don't use at all (and whether we should)

**D1. "Game and CMS event payloads" and "Field mapping" in `gamification-react-native`. Should we: yes.** See B1/B2.

**D2. `react-native-sdk-in-app-messaging` (updatedAt 2026-11-12; page exists, linked from the index and install pages, missing from llms.txt and our download). Should we: yes, cite it.**
- Content: two steps only: add `hydra_in_app_placeholder` in `PROJECT_ROOT/capillary/icons` (PNG recommended, JPG/JPEG accepted) and set `enable_in_app_messaging` to `true`. It says "for both iOS and Android". It gives no listener, report API or React Native UI option.
- Ours: sources list cites a generic `in-app-messaging` (2026-10-20), not this page; both RN files say In-App is "Documented from the runbook only" and the Gap says "The public in-app page's configuration (`InAppConfig`, `HydraInAppUIHelper`) is for native Android".
- Change: add this page to `sources`; reword the Gap: "The public React Native in-app page covers only the flag and placeholder image; `enable_in_app_messaging_in_react_native`, `addHydraInAppMessageListener` and `HydraInAppMessaging` remain runbook-only." The changelog already notes the page was missing from the saved set.

**D3. `setting-up-react-native-project-for-hydra-sdk` (index page). Should we: no.** It is only a link list; all linked pages are covered.

## E. Problems in the docs themselves (keep as Gap callouts)

**E1. Event payloads are not linked to the listeners. Severity: Medium.** `gamification-react-native` describes the seven events and `addGamificationEventTriggerListener` / `addGamificationAnalyticsEventListener` ("A game or campaign triggered a named event with a payload") but never says whether the listeners deliver these events or what their `name` values are. Also the section says "Experience+ sends the following events", with no description of how the app receives them. Gap: "whether the gamification listeners emit these seven events isn't stated."

**E2. Identifier lists disagree. Severity: Low.** Event table says `cuid` is "the loginIdentifier value (mobile number, email, or externalId)" and `identifierType` allows mobile, email, externalId; `react-native-sdk-api-reference` › HydraUserDetails says `customerId` can be mobile, email, InTouchUserId, externalId or FCMToken. Not stated whether InTouchUserId / FCMToken customers can have gamification events. Gap.

**E3. Event vocabulary does not match campaign vocabulary. Severity: Low.** `entry_surface` values (`popup`, `floating_icon`, `modal`, `banner_embedded`) vs the page's campaign types "Floating Button, Popup, and Bottom Sheet" (no `bottom_sheet` value; `modal` unexplained). Also "Map `source` to SDK" gives no literal value. Gap.

**E4. Filename typo in `react-native-sdk-install`. Severity: Low.** iOS step 3 says "Add `GoogleServices-Info.plist`"; `react-native-sdk-getting-started` and `react-native-sdk-advanced-setup` say `GoogleService-Info.plist` (our KB uses the latter). Keep a note in the KB so nobody searches for the wrong name.

**E5. In-app page not indexed. Severity: Low.** `react-native-sdk-in-app-messaging` is linked from `setting-up-react-native-project-for-hydra-sdk` and `react-native-sdk-install` but missing from llms.txt (see D2); it is only reachable via a direct link, so future syncs may miss it.

**E6. Stale-looking platform minimums. Severity: Low.** `react-native-sdk-getting-started`: `targetSdk` and `compileSdk` "31 or later" while React Native 0.77 itself needs a much higher compile SDK; React Native "0.77.0 or later" but sample apps for 0.72-0.76 (our Gap already covers the second point). Add the first to the existing Requirements Gap.

**E7. API reference nits. Severity: Low.** Signatures are shown as static (`HydraNativeEventEmitter.addXListener(...)`) but all usage examples call `getInstance()` first (our Correction callout already covers this). `HydraAccountConfig` and `HydraFirebaseRemoteConfigKeys` name the log-level argument `remoteDebugLevel` / `keyForRemoteDebugLevel`, while iOS native is `remoteLogLevel` / `keyForRemoteLogLevel` and all prose says "remote log level" (already in our Native section). Usage sample `deleteInboxMessage(hydranotification)` has a lower-case variable. `addHydraNotificationShownListener` text says "notification token is shown". No change needed beyond what we have.

**E8. Setup overview nits. Severity: Low.** Item 8 "Use the HydraInbox class to manage them" has no antecedent; item 4 lists only `requestPermission` and `getFCMToken` for `HydraPushNotification` while `passFCMToken` and `openExternalUrl` appear only in item 21. No KB change.

**E9. Template-version Gap may be mis-dated (not from the docs; confidence about 65%).** Our Gap says "The React Native 0.76+ template (`RCTReactNativeFactory`) has no `super` call". From my own knowledge, the default Swift AppDelegate of 0.77 still extends `RCTAppDelegate` (so docs' `super.application(...)` order works), and the `RCTReactNativeFactory`-style AppDelegate arrived in 0.78+. If so the docs' "0.77.0 or later" minimum is open-ended and the risk starts at 0.78, not 0.76. Verify with a Capillary engineer or the sample branches (`example_rn77_new_arch`, `example_rn76_new_arch`) before editing the Gap.

## F. Impact on derived files (requirements.yaml, prerequisites.yaml, faq.yaml, step titles)

**F1. `prerequisites.yaml` › `org_id`: see A2.** Remove `react-native/direct` from the always-on entry; add it to the `modules: [visitor]` entry. Update `_shared/prerequisites.md` row. `tests/test_prereq_engine.py` only checks that `source` files exist, so no test change is expected.

**F2. `prerequisites.yaml` › `firebase_project`, `google_services_json`, `google_service_info_plist` do not apply to `react-native/direct` with push. Severity: Medium (confidence high).**
- Docs: `react-native-sdk-getting-started` makes "Set up Firebase for push notifications" (register the app, download `google-services.json` and `GoogleService-Info.plist`) a prerequisite whenever push is used, regardless of where the account values come from. Our `direct.md` Prerequisites repeats this ("Firebase (push only)"), and its steps 5, 9 need both files.
- Ours: those three items list `react-native/firebase` only, so an RN direct + push client gets no Firebase checklist items and no upload validators. `app/kb/loader.py` also does not load `_shared/firebase-setup.md` for `react-native/direct` (only `push.md` loads, as `react-native/direct` is in `_PUSH_APPS`).
- Change: add `- platforms: [react-native/direct]` with `modules: [push]` to those three items (as done for `web/direct`); consider loading `firebase-setup.md` for RN direct with push (loader change, needs tests updated). `remote_config_values` correctly stays Firebase-only.

**F3. New optional prerequisite after SME confirmation (from B2).** A non-blocking client/Capillary item "Create the gamification events with the field mapping (`customerId`, `identifierType`, `source`, `accountId`)", `modules: [gamification]`, `source: knowledge_base/_shared/overview.md` (after adding the text there). Do not add until it is clear who creates the events.

**F4. `requirements.yaml` › `react-native`: no change needed.** All eight `check` strings still exist in both RN files, and the values match the docs (0.77.0, iOS 15.0, API 21, Node 18.0.0, 31/31, plugin 4.4.2). If E6 is added to the existing Gap, copy it into the `gaps` list. Minor inconsistency: the "Hydra SDK version" row says "Latest release (no version pinned)" while `firebase.md` front matter has `sdk_version: 1.7.0-beta.7` (a beta from the older gamification guide), which also feeds `{{sdk_version}}` in step G1. The public docs install with no tag. Consider setting `sdk_version: null` as done for Flutter, or keep it but make G1 say "latest release".

**F5. `step_modules.yaml` and `step_summaries/react-native.yaml`: no change if the new event content goes under Modules › Gamification** (recommended). Adding a numbered step (direct 17, firebase G5) would need new `step_modules` entries (`modules: [gamification]`, a `title` that appears in the heading) and new `step_summaries` entries with `evidence` strings that appear in the guide. All 16 + G1-G4 existing evidence strings were found in the current guides.

**F6. `faq.yaml`: existing React Native evidence strings still hold** (`screen not reported, reported before sign-in, or reported without the 500 ms delay`, `` `Hydra.setCapToken(...)` before showing it ``). Optional new FAQ (category problems): "Which gamification events does the SDK send, and do I need to create them in Capillary?", answered once B1/B2 are merged and E1 is resolved; add evidence from the new table. Also extend `events-missing` evidence with the field-mapping rule.

## G. Confirmed matching (verified identical in docs and our RN files)

- Requirements: RN 0.77.0+, iOS 15.0+, Android API 21, Node 18.0.0+, targetSdk/compileSdk 31+; six sample branches (`example_rn72_new_arch` ... `example_rn77_new_arch`) of `Capillary/react-native-hydra-lib`.
- Package `@capillarytech/react-native-hydra-lib` (npm/yarn), migration note (remove `@capillary` registry/token entries and `hydra_github_setup.gradle`), Android SDK from Maven Central with consumer ProGuard/R8 rules, no credentials.
- `hydra-config.json` at `PROJECT_ROOT/capillary/`: all 10 keys, types and defaults (`console_log_level` 4, `enable_in_app_messaging` false, `enable_inbox_api` false, `enable_inbox_ui` false, `use_default_inbox_ui_config` true iOS-only, `max_notification_count` 200, `enable_hydra_sdk_firebase_registration` true, `enable_push_notification` true, `enable_ssl_pinning` true, `hydra_notification_color`), icons folder `capillary/icons` with `hydra_notification_small_icon`, `hydra_inbox_ui_placeholder`, `hydra_in_app_placeholder`.
- iOS: Podfile `HydraPods.rb` require block, `hydra_pods`, SPM (`$RNHydraUseSPM`, `use_frameworks! :linkage => :dynamic`, `hydra_post_install`, `-ObjC`), `hydra-ios-sdk-spm` and `HYDRA_SPM_REQUIREMENT`, `extension_pods` no-op under SPM, `HydraPushNotificationServiceExtension` product, App Group `group.<bundle_id>.hydra`, NSE Swift and Objective-C code, AppDelegate Objective-C import (`__has_include`) and Swift import, `Hydra.sharedInstance().initialize(...)` signatures, call-order note (super first, Inbox UI wraps root controller), Xcode < 16 import issue.
- Android: `com.google.gms:google-services:4.4.2` classpath and plugin, `google-services.json` in `android/app`, `com.hydralib.nativeapis.Hydra`, `Hydra.initialize(this)`, `HydraFirebaseRemoteConfigKeys` (8 args), `HydraRemoteConfig.Builder(...)` with `.orgId/.gamificationKey/.gamificationRegion/.gamificationBaseUrl`, `Hydra.initialize(this, remoteConfig = remoteConfig)`.
- Remote Config keys: `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level`, `hydra_org_id`, three `hydra_gamification_*`; custom `ind_hydra_*` names; `HydraNativeFirebaseRemoteConfigKeys` iOS argument labels.
- Without Firebase: JSON, skip list, `setHydraAccountConfig` only (never `setFirebaseRemoteConfigKeys`), dummy `passFCMToken`, listeners not to register, Firebase libs still linked.
- Multi-account: both methods, order (init, set account, identify), rejection message "Failed to get values for these keys from Firebase remote config", persistence across launches, same-account no-op.
- Setup overview: deprecated `HydraCore.signUp/signIn/signOut/reportUserEvent` and replacements, listener list, log levels 0-5 (`HydraLogLevel`), remote level source, `passFCMToken` + `openExternalUrl` note.
- Push, Notification Center, Visitor flow, Gamification (non-event) pages: all steps, listener names, `UserState` flow, `GamificationBannerView/EmbedView/LoyaltyView` props, `setCapToken`, suppression, `ThemeMode`, height-0 handling, sample code.
- API reference: every method signature and return type, all 20 `HydraNativeEvent` names, enums (`HydraLogLevel`, `ThemeMode`, `UserState`, `HydraNotificationCtaType`, `HydraNotificationGateway`), models (`HydraUserDetails`, `HydraGeoConfig`, `HydraPushPreferences`, `HydraAccountConfig`, `HydraFirebaseRemoteConfigKeys`, `HydraVisitorInfo`, `HydraNotification` and sub-classes, `NonHydraNotification`).
- Shared: `_shared/prerequisites.md` package-access row for React Native, Gamification base URL required for React Native, `enable_ssl_pinning` note; `_shared/firebase-setup.md` React Native gamification key row; `_shared/troubleshooting.md` package name line.

## Summary

The React Native knowledge base is accurate against the nine pages dated 2026-11-12 and I found no wrong code, version, key or signature in `direct.md` or `firebase.md`. The one page changed since the 2026-11-13 merge, `gamification-react-native` (2026-11-23), adds seven gamification event payloads and a four-field event-creation mapping that we lack; this makes our "event names and payloads aren't documented" Gap stale and leaves a possibly important Capillary-side step undocumented in our guides. The other problems are in derived files: `prerequisites.yaml` always asks React Native direct clients for an Org Id that the docs treat as visitor-flow-only, and it gives React Native direct + push clients no Firebase project or config-file items (and the loader skips `firebase-setup.md` for them) although the docs require Firebase for push. A few Gap callouts (in-app page, Android manifest entry, no-push starter config) should be refined, the in-app page that exists but is missing from the downloaded set should be cited, and several minor typos and ambiguities in the docs should be kept as Gaps.

Counts: A = 4, B = 2, C = 3, D = 3, E = 9, F = 6, G = 1 list (11 groups). High: 1 (B2). Medium: A1, A2, B1, C1, E1, F2. The rest are Low.
