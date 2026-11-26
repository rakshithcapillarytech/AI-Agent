# Flutter slice: audit of knowledge_base vs docs.capillarytech.com (read-only)

Scope read in full: the 9 public pages (flutter-sdk, -getting-started, -install, -advanced-setup, flutter-setup-overview, -push-notifications, configuring-notification-center, gamification-flutter, -api-reference) against knowledge_base/flutter/direct.md, flutter/firebase.md, _shared/{prerequisites,firebase-setup,push,troubleshooting,overview}.md, requirements.yaml, prerequisites.yaml, faq.yaml, step_modules.yaml, step_summaries/flutter.yaml.

Headline: the Flutter KB was merged from exactly these pages (its `sources:` line says "updated 2026-11-12") and is very close to them. A token-level check (every backticked identifier, camelCase/PascalCase name, `hydra_*`/`enable_*` key in the 9 pages searched in our Flutter and shared files) found only ONE group of public-doc identifiers absent from the KB: the Game/CMS event-payload section of gamification-flutter (the only page dated after 2026-11-13). No High-severity contradiction was found. The real risks are one missing section, a few doc-internal inconsistencies worth Gap callouts, and one page we could not check because it was never downloaded.

## A. Contradictions (docs and our KB disagree)

**A1. Medium. Gamification "disabled if key or region missing" omits the base URL.**
- Docs: gamification-flutter "requires the Gamification Key, Gamification Region, and Gamification Base Url"; getting-started lists all three RC keys.
- Ours: flutter/firebase.md Gamification step 1 and flutter/direct.md step 1 say "HydraGamification stays disabled if the key or region is missing". The Known Issues row "Gamification campaigns never appear" in both files, and faq.yaml `gamification-not-showing` (answer: "the gamification key and region are missing"), name only key/region. (The same files' Corrections and the firebase.md checklist do say all three are required, so the files are internally uneven.)
- Change: in both Known Issues rows and the FAQ answer say "key, region or base URL missing". Keep the existing wording as the evidence string or update `evidence` in faq.yaml together with the file (tests/test_faq.py). Add "(the docs don't say what happens if only the base URL is missing)" as a Gap. Confidence 85% that this is a real gap; the behaviour with a missing base URL is not documented.

**A2. Low. direct.md labels `setFirebaseRemoteConfigKeys` "Firebase mode only".**
- Docs: flutter-sdk-advanced-setup "Option A: Firebase Remote Config" is not restricted to a mode; `setFirebaseRemoteConfigKeys` reads "values Firebase Remote Config has already fetched".
- Ours: flutter/direct.md API table ("Switch account via Remote Config key names (Firebase mode only)") and Multi-account parenthesis; the models table has no `HydraFirebaseRemoteConfigKeys` row (it is only in firebase.md). direct.md itself says Firebase is base setup in every Flutter mode, so a direct-mode app can hold prefixed keys in RC.
- Change: reword to "needs the account values published in Firebase Remote Config (works in either mode)" and add the `HydraFirebaseRemoteConfigKeys` row to direct.md's Models table. Confidence 70%.

**A3. Low. firebase.md step 9 heading "(no AppDelegate code needed)" can mislead when In-App is selected.**
- Docs: flutter-sdk-install iOS step 5 "You don't need any Hydra-specific code in AppDelegate.swift" (about base init only). Our In-App module (source: not in the saved pages, see D1) requires an `application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` override in AppDelegate, and nothing says where that goes under the UIScene lifecycle.
- Change: add "(the In-App module does add one AppDelegate method, see Modules › In-App)" to the step 9 heading line, and a Gap for UIScene placement of that method. Confidence 60%.

**A4. Low (internal KB error, not a doc contradiction). firebase-setup.md header names the wrong sections for Flutter direct.**
- Ours: `_shared/firebase-setup.md` line 10: "Flutter and Web direct-mode apps that still use Firebase for push need sections 1, 2 and 4". Section 4 is the Web VAPID key. Flutter direct needs 1, 2, and for push 6 (iOS APNs key) and 7 (service account).
- Change: "Web direct needs 1, 2 and 4; Flutter direct needs 1, 2, 6 and 7 (push)". Confidence 90%.

## B. Missing from our KB (in the docs, important for integrators, absent from our guides)

**B1. Medium. Game and CMS event payloads, and the event-creation field mapping (gamification-flutter, updated 2026-11-23).**
- Docs: seven events (`game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed`), each with attributes, a sample JSON payload and "fires when". Rules: "`cuid` is required on every event", flat JSON, numbers sent as numbers. A Field mapping table makes four fields required when creating the events: `customerId` (from `cuid`), `identifierType` (mobile, email or externalId, "set based on what is passed to the SDK as the login identifier"), `source` ("Map source to SDK"), `accountId` (the SDK account ID).
- Ours: absent from flutter/direct.md and flutter/firebase.md (only web/*.md mention the seven names, one line). It matters because `_shared/overview.md` already says behavioural events must exist in Capillary before they are accepted.
- Change: add a short "Gamification events" sub-section to both Flutter files (event list, the `cuid` rule, the four-field mapping table, one sample payload) with a Gap: the docs don't say which Capillary screen the "event-creation fields" belong to (presumably Organisation settings, Master Data Management, Data Model, Behavioural events; confirm). Link it from `_shared/overview.md`.

**B2. Low. No direct-mode UIScene code sample.**
- Docs show a UIScene sample only for the custom-Remote-Config-keys variant (advanced-setup). For `initApplication` with UIScene, only the prose exists, also in our direct.md step 10.
- Change: in direct.md step 10 add a sample built from the documented pattern (`didInitializeImplicitFlutterEngine`, `GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)`, then `HydraNativeAPI.shared.initApplication(UIApplication.shared, didFinishLaunchingWithOptions: nil, hydraRemoteConfig: remoteConfig!)`), labelled "derived from the custom-keys sample, pending SME confirmation".

**B3. Low. Whether the plugin's automatic start also runs when you call the initializer yourself (iOS).** See E3; the guides should carry a Gap.

## C. Changed since 2026-11-13

**C1. Medium. Only one Flutter page is dated on/after 2026-11-13: gamification-flutter (2026-11-23).**
- No earlier copy of the page exists in the repo, so a true diff is impossible. Every other section of it (screen tracking incl. Bottom Sheet, three widgets and `onHeightChanged` with `height >= 0`, cap token before mounting, suppression, theme, the three events) is already in both KB files, and the CHANGELOG says they were added on 2026-11-13. By elimination the new material is the "Game and CMS event payloads" section (B1). Confidence about the delta: medium (70%); about the KB gap: high.
- Change: apply B1; update the `sources:` line "(updated 2026-11-12)" to include gamification-flutter 2026-11-23.

**C2. Info. The other eight pages are all dated 2026-11-12 (before the 11-13 merge).** Spot-checked as unchanged in substance against the KB (see G). Nothing to do.

**C3. Info. Process.** Store a dated copy of each fetched public page (or a hash) so future audits can diff instead of infer.

## D. Pages or sections we don't use at all

**D1. Medium. `flutter-sdk-in-app-messaging` was never downloaded.** flutter-sdk.md links to it and the hydra-config table points to it ("Requires the in-app placeholder asset"). Our In-App module (hydra_in_app_placeholder, AppDelegate `didReceiveRemoteNotification` forwarding, `enable_in_app_messaging_in_flutter` note) cannot be checked against the current public page. CHANGELOG line 46 already records the page as "not in the saved set". Recommend downloading it and auditing the In-App sections of both files, especially the placeholder file name, the AppDelegate snippet and the Android side (which our KB says nothing about).

**D2. Low. flutter-sdk.md** is only a navigation hub; nothing to use. Correctly ignored.

**D3. Low. The Game and CMS event payload section** is unused (B1; should be used).

**D4. Low. pub.dev package pages (`capillary_hydra`, `.../example`, `.../changelog`)** are linked from the docs, and the package's pubspec `environment:` would settle the Flutter/Dart minimum (E1). They are not in the downloaded set. Worth a one-off look.

## E. Problems in the docs themselves (keep as Gap callouts)

**E1. Medium. Flutter and Dart minimums are inconsistent.**
- Docs: flutter-sdk-getting-started Prerequisites: "Flutter >= 3.3.0 (Dart >= 3.0)". Dart 3.0 first shipped with Flutter 3.10; Flutter 3.3 bundles Dart 2.18. So the two bounds cannot both be the real minimum.
- Ours: reproduced verbatim in flutter/*.md Requirements, requirements.yaml (value and `check`), and the Gap there lists only compileSdk/AGP/Gradle/Kotlin/Xcode/CocoaPods.
- Change: add a Gap in both Requirements sections: "Flutter >= 3.3.0 and Dart >= 3.0 don't line up (Dart 3.0 arrived with Flutter 3.10); if `pub get` fails on Flutter 3.3 to 3.9, upgrade Flutter, and ask Capillary/check the package's pubspec for the real minimum." Confidence 85% on the version facts; the package's true constraint is unknown.

**E2. Medium. Android Builder remote-log-level scale is ambiguous.**
- Docs: advanced-setup Android sample `... "your_ssl_public_key", 4 // LogType.DEBUG`; table says remote log level "0–5 (HydraLogLevel). Defaults to `0`"; HydraLogLevel has off(0)...debug(4).
- Ours: troubleshooting.md section 4 records the native Android scale as OFF(-1), INFO(0), DEBUG(1), where `LogType.DEBUG` would be 1 and default 0 would be INFO, not "off". Our direct.md already dropped the "LogType.DEBUG" comment but doesn't flag the conflict.
- Change: Gap in direct.md step 12 and the Builder table: "the docs' sample comments 4 as LogType.DEBUG but the parameter is described on the 0 to 5 HydraLogLevel scale; use the 0 to 5 scale and confirm what the default 0 means." Confidence 60%.

**E3. Low-Medium. iOS: unclear whether the plugin's auto-start also runs when you call `initApplication` yourself.**
- Docs: install iOS step 5 "the plugin starts the Hydra SDK itself once it's registered"; advanced-setup says use the variants "instead". For Android the docs state the rule ("only runs when the Application class is exactly HydraApplication"); no such rule is stated for iOS.
- Ours: direct.md step 10 says "Without your own call, the plugin starts Hydra itself", implying it is replaced, which the docs only imply.
- Change: add a Gap: "not documented whether the automatic start is skipped when you call the initializer; if `onHydraSdkInitializationResult(success: false)` appears in direct mode, check for a double start reading missing default Remote Config keys." Confidence 55%.

**E4. Low-Medium. Event `cuid` / `identifierType` allow only mobile, email, externalId.** The API reference lets `customerId` be mobile, email, InTouchUserId, externalId or FCMToken. For an org whose Account Linking Identifier is InTouchUserId or FCMToken, the event-creation mapping is undefined. Add as a Gap next to B1.

**E5. Low. Gamification page lists campaign types inconsistently.** Intro: "Floating Button and Popup campaigns"; screen tracking: "Floating Button, Popup, and Bottom Sheet" (we follow the latter, as does _shared/overview.md). `entry_surface` values (popup, floating_icon, modal, banner_embedded) have no bottom-sheet value. Keep a one-line Gap.

**E6. Low. Handler wording.** install and setup-overview say "Implement a HydraNativeEventHandler"; the API reference says prefer `extends`. We already follow the API reference (direct.md step 15). No change.

**E7. Low. Getting Started says it is "mandatory" to take Account Id, SSL key, Base Url and log level from a remote configuration tool**, yet the same page and advanced-setup allow passing values directly. No change needed (our direct mode covers it); keep wording out of the guides.

**E8. Low. Field-mapping wording** ("Map `source` to SDK", "SDK account ID") doesn't say what literal value to enter. Add to the B1 Gap.

**E9. Low. "Don't make any code changes Firebase suggests" vs the manual Google Services plugin step.** Firebase's own console suggests that same Gradle plugin change; the Flutter docs then ask for it in the install page. Our step 1 wording ("You add them in steps 9 and 11") already prevents confusion; no change.

Existing Gap and Correction callouts that remain valid against the current pages: AppSheet link for Firebase registration; the `HydraFirebaseRemoteConfigKeys` Map usage sample in the API reference (re-confirmed: it is still a `Map` with key `'ind_account'`); `remoteConfig!` force-unwrap; no SPM steps; compileSdk/AGP/Gradle/Kotlin/Xcode/CocoaPods unspecified; RC value type unspecified; `use_default_inbox_ui_config: false` undocumented.

## F. Impact on derived files

**F1. Medium. requirements.yaml (flutter).** After E1, add the Dart/Flutter mismatch to `gaps` (and to the guides' Requirements Gap callouts, since tests compare them). Keep the `value`/`check` strings unchanged.

**F2. Medium. faq.yaml `gamification-not-showing`** (A1): add the base URL to the answer and update `evidence` to match the edited Known Issues text.

**F3. Low. faq.yaml `with-or-without-firebase`** says generically that without Firebase you pass settings in init. For Flutter, direct mode still needs the Firebase project, `google-services.json`, `GoogleService-Info.plist` and the Google Services Gradle plugin. Add a Flutter-specific sentence (the file supports `platforms`, so add a separate Flutter item, or append to the answer).

**F4. Low. requirements.yaml "Apple developer account access (push)"** has `modules: [push]`. The Inbox API on iOS also needs the Notification Service Extension and App Group (configuring-notification-center step 1), i.e. developer.apple.com access. Add the inbox module(s) to that item's `modules` (check the module ids used by the profile).

**F5. Low. prerequisites.yaml:** no Flutter item is wrong. After B1 is confirmed by an SME, consider a non-blocking gamification item for creating the seven events with the four-field mapping (owner not yet known: client or Capillary).

**F6. None needed: step_modules.yaml** has no Flutter entries and all 17 (direct) and 15 (firebase) steps are core; step_summaries/flutter.yaml matches the current steps (RC key names, `4.4.2`, `HydraInitializer.initialize()` placement, Application class rules, theme). Adding B2's sample does not renumber steps.

## G. Confirmed matching (checked both sides)

- Requirements: Flutter >= 3.3.0 (Dart >= 3.0), iOS >= 15.0, Android API 23; packages `capillary_hydra` and `capillary_hydra_platform_interface` via `flutter pub add`, same version, `flutter pub upgrade`; Android SDK from Maven Central, no credentials; both pub.dev changelog links.
- Prerequisites: bundle id, applicationId, SHA256 signature to Capillary; Account Id, Base url, SSL key back; Org Id only for visitor flow; Gamification Key, Region, Base Url (all three) only for gamification.
- RC key names (`hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level`, `hydra_org_id`, `hydra_gamification_key/_region/_base_url`) and the `ind_hydra_*` prefixed set; log scale 0 to 5.
- `hydra-config.json`: all 9 keys, defaults, platform column (Android only: `enable_in_app_messaging_in_flutter` non-functional, `hydra_notification_color`; iOS only: `use_default_inbox_ui_config`), `enable_ssl_pinning` semantics; `capillary/` and `capillary/icons/` pubspec assets; `HydraInitializer.initialize()` in `main()` after `ensureInitialized`.
- iOS: Podfile `require_relative` path, `hydra_pods` inside Runner, `pod install`, SPM skip, both lifecycles; `HydraNativeAPI.shared.initApplication` and `initApplicationWithFirebaseRemoteConfig` samples; call after `GeneratedPluginRegistrant.register`; UIScene `didInitializeImplicitFlutterEngine` with `UIApplication.shared` and `nil`.
- Android: Google Services plugin `4.4.2` (Kotlin and Groovy forms), `android/app/google-services.json`, `HydraApplication` rules (exact class auto-initialises; subclass calls `initializeUsingFirebaseRemoteConfig` or `initialize` right after `super.onCreate()`), Builder positional args, optional setters and default 0, AppCompat theme string.
- Push: `hydra_notification_small_icon`, Push + Background Modes (Background fetch, Remote notifications), mandatory Notification Service Extension, App Group `group.<runner_target_bundle_id>.hydra`, `extension_pods`, `NotificationService.swift` body identical, `requestPermission`/`getFCMToken`/`onTokenAvailable`/`passFCMToken` (Android only, no-op on iOS), push preferences, unsubscribe methods.
- Inbox API and UI: `enable_inbox_api`, `enable_inbox_ui`, `hydra_inbox_ui_placeholder`, iOS NSE and App Group dependency, five `HydraInbox` methods, two `HydraInboxUI` methods, no "inbox updated" event.
- Multi-account: both switch methods, order (init result, set, then identify), persistence, iOS `false` vs Android `true` when keys are missing, `HydraAccountConfig` and `HydraFirebaseRemoteConfigKeys` fields.
- API reference: every method signature, the 16 `HydraNativeEventHandler` callbacks, `HydraUserDetails`, `HydraGeoConfig`, `HydraPushPreferences`, `HydraLogLevel`, `HydraThemeMode`, `UserState`, `HydraNotification*` models and enums, `NonHydraNotification`, throws/none behaviour of suppression and theme calls.
- Gamification (non-event parts): same `screenName` for appeared and disappeared, Bottom Sheet auto-show, three widgets and their signatures, `height >= 0` collapse rule, `setCapToken` before mounting, suppression, theme, three event callbacks.
- Derived files: requirements.yaml Flutter `check` strings, prerequisites.yaml Flutter items (blocking SHA256, gamification three-value rule, org id only with visitor), step_summaries/flutter.yaml step content, faq.yaml Flutter-relevant evidence strings all exist in the guides.

## Summary

The Flutter KB reflects the nine public pages almost completely; no High-severity contradiction exists. The substantive gaps are (1) the Game/CMS event-payload section added to gamification-flutter on 2026-11-23, which our guides lack, (2) the unchecked In-App module because `flutter-sdk-in-app-messaging` was never downloaded, (3) two doc-internal inconsistencies worth Gap callouts (Flutter 3.3.0 vs Dart >= 3.0; Android `LogType.DEBUG` vs the 0 to 5 scale) plus an undocumented iOS double-start question, and (4) small KB wording issues: base URL left out of the "gamification disabled" rule and FAQ, "Firebase mode only" on `setFirebaseRemoteConfigKeys`, and a wrong section list in the firebase-setup header. Derived-file impact is small (requirements gap, one FAQ answer, one FAQ addition, one `modules` list).

Counts: A = 4 (0 High, 1 Medium, 3 Low); B = 3 (1 Medium, 2 Low); C = 3 (1 substantive, 2 info); D = 4 (1 Medium, 3 Low); E = 9 (2 Medium, 2 Low-Medium, 5 Low); F = 6 (2 Medium, 3 Low, 1 none needed); G = 11 verified groups.
