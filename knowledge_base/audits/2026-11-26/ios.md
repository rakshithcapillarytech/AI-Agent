# iOS slice: audit of knowledge_base against docs.capillarytech.com (read-only)

Scope read in full: 12 public pages (ios-sdk, ios-sdk-getting-started, set-up-source-account-ios, configure-gateway-ios, install-sdk, initialise-ios-sdk, core-features, configure-push-notifications, rich-push-notifications, configure-notification-center_ios, gamification-ios, ios-sdk-api-reference); knowledge_base/ios/direct.md and firebase.md; the iOS/source-account/gateway/Firebase/APNs/push parts of _shared/prerequisites.md, firebase-setup.md, push.md, troubleshooting.md; the iOS entries of requirements.yaml, prerequisites.yaml, faq.yaml, step_modules.yaml, step_summaries/ios.yaml; plus cross-checks in tests/ and evals/. I also read configure-firebase.md (outside the slice, but configure-push-notifications links to it).

Key observation: the front matter of ios/direct.md and ios/firebase.md cites ios-sdk-getting-started as "updated 2026-08-14", install-sdk as "2026-03-04" and gamification-ios as "2026-08-18". The current copies are dated 2026-11-12, 2026-11-12 and 2026-11-23. So the iOS guides were built from older versions of the pages that matter most, and most High findings below come from that. Line numbers refer to ios/direct.md (dm) and ios/firebase.md (fb).

Page dates: ios-sdk 2026-08-14; ios-sdk-getting-started 2026-11-12; install-sdk 2026-11-12; rich-push-notifications 2026-11-12; configure-push-notifications 2026-11-16; gamification-ios 2026-11-23; the other six pages 2026-03-04.

---

## A. Contradictions (docs and our KB disagree)

**A1. High. SDK repository is now public; we still say private with a GitHub token.**
- Docs: install-sdk: "The HydraSDK repository is public." and "needs no GitHub account or personal access token" for `https://github.com/Capillary/hydra-ios-sdk-spm`. Same repo is used by rich-push-notifications (SPM target name `hydra-ios-sdk-spm`, Podfile `:git => 'https://github.com/Capillary/hydra-ios-sdk-spm.git'`) and by react-native-sdk-push-notifications.
- Ours: dm/fb front matter `sdk_package` (L4), Prerequisites "Repo access" (dm L41, fb L43), Step 1 "Authenticate to the private repo" (dm L49-62, fb L51-63), Step 2 SPM/Xcode/Podfile URLs `hydra-sdk-ios-packages` (dm L87, L101, L113; fb L89, L103, L115), rich-push step 5 (dm L470-475, fb L485-490).
- Change: replace every URL with `https://github.com/Capillary/hydra-ios-sdk-spm` (Pods: `.../hydra-ios-sdk-spm.git`). Remove the PAT-in-URL option and the Xcode "Accounts" step. Say no GitHub account or token is needed. Add a Gap: the 2024 Integration PDF and the June 2026 internal runbook used private `hydra-sdk-ios-packages` with a PAT; ask Capillary whether the old repo is retired. Confidence high that the public page is current. Medium on whether the old repo still works.

**A2. High. Our two `⚠️ Correction` callouts now steer developers to the wrong repo.**
- Docs: install-sdk now uses `hydra-ios-sdk-spm` and `1.10.6`.
- Ours: dm L96 and fb L98: "✅ Use the repo hydra-sdk-ios-packages … ❌ Don't use hydra-ios-sdk-spm.git or 1.7.5-preprod.10". Also dm L94 / fb L96 name `1.1.0` as the thing to avoid.
- Change: delete both callouts (the premise is gone). If you want a record, write a Gap: "older sources name `hydra-sdk-ios-packages` and `1.7.5-preprod.x`; current docs name `hydra-ios-sdk-spm` and `1.10.6`".

**A3. High. Minimum SDK version.**
- Docs: ios-sdk-getting-started: "iOS SDK version 1.10.6 or above"; every framework in the table is 1.10.6. install-sdk Package.swift uses `from: "1.10.6"`. gamification-ios callout: "Minimum SDK version: 1.10.6".
- Ours: `sdk_version: 1.7.5-preprod.12` (dm/fb L5), "Requirements" L29/L30, and `{{sdk_version}}` flows into the Package.swift, Xcode step, checklist, Known Issues. The front-matter note says "getting-started: SDK 1.7.0 or above, framework table at 1.7.4".
- Change: set `sdk_version: 1.10.6` and rewrite the front-matter comment. Every `{{sdk_version}}` use then becomes correct. Also update the Correction/Gap text that names preprod versions.

**A4. High. Minimum iOS deployment target.**
- Docs: ios-sdk-getting-started: "Minimum deployment version (iOS): 15.6". install-sdk Podfile: `platform :ios, '15.6'`.
- Ours: "Minimum deployment target: iOS 13.0 (the Podfile uses platform :ios, '13.0')" (dm L30, fb L31) and Podfile `platform :ios, '13.0'` (dm L110, fb L112).
- Change: iOS 15.6 in both places. An app targeting 13/14 fails to resolve the 1.10.6 SDK (confidence high on the doc value; the failure mode is my inference).

**A5. High. Xcode version.**
- Docs: install-sdk Xcode method prerequisites: "Xcode 16.1 or later".
- Ours: "Xcode 14 or later (stated for installing through Xcode)" (dm L32, fb L33).
- Change: "Xcode 16.1 or later". The page states it only under "Installing SDK Using Xcode", so also add a Gap: whether 16.1 applies to the SPM and CocoaPods methods isn't stated (assume yes, since the SDK is built with a recent toolchain, but unconfirmed).

**A6. Medium. "Beta for UAT/POC" label no longer in the docs.**
- Docs: none of the 11-12/11-23 pages call 1.10.6 a beta or preprod.
- Ours: dm/fb L5 and L29/L30 "minimum for gamification; Beta for UAT/POC". requirements.yaml also shows the note "Beta; the minimum for gamification".
- Change: drop the Beta wording (it came from the 1.7.5-preprod build in the PDF). Keep a Gap if SMEs want to confirm 1.10.6 is a stable release.

**A7. Medium. Stale Gap about a Firebase "Server Key"; the page now says something else.**
- Docs: configure-push-notifications (2026-11-16) step 3 "Create a service account key for Capillary": the Capillary backend needs a service-account private key, "Your iOS app doesn't need this key and must never contain it", link to configure-firebase. Step 2 now only uploads the APNs key/cert.
- Ours: dm L352 and fb L367 "Gap: … also says to copy the Server Key … Ask a Capillary engineer". _shared/firebase-setup.md L85 says "a Cloud Messaging server key (iOS and Android push pages)".
- Change: delete the two Gaps and the iOS half of the firebase-setup Gap. Add to Push step 1: "Capillary also needs a service-account key from your Firebase project (see `_shared/firebase-setup.md` §7 and `_shared/push.md`); it never goes in the iOS app". Confidence high.

**A8. Medium. Known Issues rows that are now wrong.**
- Ours: dm L761 / fb L870 "SPM resolves an old SDK: the docs' snippet uses from: 1.1.0" (the snippet now says 1.10.6). dm L760 / fb L869 "SDK fetch fails … No access to the private repo / PAT".
- Change: remove the `1.1.0` row. Rewrite the fetch row: check network, Xcode ≥ 16.1, the URL `hydra-ios-sdk-spm`, and that the dependency rule permits 1.10.6. Keep "no access" only if SMEs say the old repo is still needed.

**A9. Medium. Shared files still describe iOS as a private repo.**
- Ours: _shared/prerequisites.md L71 (table row iOS = `hydra-sdk-ios-packages`), L82-86 ("Older guides: access per platform", iOS row with PAT), L77 Gap wording; _shared/troubleshooting.md §3 row 1 ("Access denied / 401 when fetching Capillary's private packages") reads as applying to iOS.
- Change: iOS row = public `hydra-ios-sdk-spm`, no credentials (Swift Package Manager, Xcode or CocoaPods); keep the Android GitHub-PAT rows as they are. In troubleshooting §3 say the token checks apply to Android only (and React Native older setups).

**A10. Medium (cross-slice, flag for the shared/Android reviewer). Service-account role for Capillary.**
- Docs: configure-firebase (2026-11-16): use a dedicated service account with "Firebase Cloud Messaging API Admin (roles/firebasecloudmessaging.admin)" or a custom role with only `cloudmessaging.messages.create`; don't use Owner/Editor/Firebase Admin; turn on the FCM API (V1); Capillary calls the HTTP v1 API.
- Ours: _shared/firebase-setup.md §7 step 1 requires a custom role with 11 permissions (`fcmdata.deliverydata.list`, `firebase.clients.get`, …). Not reconciled with the new page.
- Change: rewrite §7 to the two role options, add "enable FCM API (V1)" and "dedicated account, don't reuse". Keep the 11-permission list only as a Gap (older Android page).

**A11. Low. push.md says only an APNs "certificate".**
- Docs: configure-push-notifications: "upload your APNs authentication key or certificate".
- Ours: _shared/push.md L58 "the app's APNs certificate must be added…".
- Change: "APNs authentication key (or certificate)". The platform files already say this correctly.

**A12. Low. Bundle Name format for an iOS-only account.**
- Docs: set-up-source-account-ios shows only the combined form `android:com.…;ios:com.…`; the iOS-only form is not stated.
- Ours: dm/fb L39/L40 say it is registered "as `ios:{{bundle_id}}`".
- Change: keep, but add a Gap that the single-platform format isn't documented. Confidence low-medium that the plain form differs.

---

## B. Missing from our KB (in the docs, important for integrators, absent from our guides)

**B1. High. After sign-up or sign-in you must also call `update(customerID:)`; on sign-out reset it.**
- Docs: core-features: "IMPORTANT: Also update the SDK's customerId immediately after sign-up/sign-in" with `hydraSDK?.update(customerID: "new_user_123")`, repeated in a Note box. For sign-out: `update(customerID: "GUEST_ID")` or `""`.
- Ours: absent. Step 4 says only "whenever the customer ID changes in the app"; steps 5 and 7 never link to it. core-features is not in either file's `sources`.
- Change: add one sentence to steps 5, 7 and 4 in both files: after `reportUserSignUp`/`reportUserSignIn` call `update(customerID:)` with the same ID; after `reportUserSignOut` set it to a guest ID or clear it. Add to the API table and Verification. Confidence high on the doc text; medium that omitting it causes wrong attribution (the page doesn't say what breaks).

**B2. Medium. Game and CMS event payloads (new section on gamification-ios, 2026-11-23).**
- Docs: seven events `game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed`; `cuid` required on all; flat JSON; and a Field mapping the integrator must apply when creating the events in Capillary: `customerId` ← `cuid`, `identifierType` (mobile, email or externalId, per the login identifier passed to the SDK), `source` = SDK, `accountId` = SDK account ID (all four required).
- Ours: absent from ios/*.md (only web/*.md lists the seven names). The page is the same across platforms.
- Change: add a short "Gamification events" subsection (names, when each fires, required `cuid`, the four-field mapping) to the iOS Gamification module, ideally as a shared snippet reused by all platforms. Needs SME confirmation of where in Capillary the events are created (the page says "while creating the events" without naming the screen).

**B3. Medium. Secure sharing of the service-account file is now documented.**
- Docs: configure-firebase step 6: one-time link from an enterprise password manager or vault (restricted to recipient, expires in 24 to 48 hours, single view), or a restricted file-share link with expiry, access removed after Capillary confirms.
- Ours: _shared/push.md L56 Gap "the channel for sharing the service-account file … aren't documented"; firebase-setup §7 says only "the secure channel the Capillary contact names".
- Change: replace the Gap with these two methods. The "how long gateway setup takes" half of the Gap stays open.

**B4. Low. iOS gamification region value format.**
- Docs: gamification-ios lists no values or type for `gamificationRegion` / `hydra_gamification_region`.
- Ours: dm L156 "Region values: see _shared/prerequisites.md", which gives `IN`/`US`/`ME` from the Android enum.
- Change: add a Gap on iOS: the iOS region type (string or enum) and accepted values aren't documented.

**B5. Low. Inbox metrics.** configure-notification-center_ios lists tracked metrics (inbox opens, notifications viewed, notifications deleted). Absent from our Inbox module. Add one line.

**B6. Low. Framework sizes.** ios-sdk-getting-started table: HydraCore 9.6 MB, HydraInAppMessage 3.5, HydraPushNotification 2.1, HydraPushNotificationServiceExtension 2.7, HydraInboxUI 2.4, HydraInboxCore 1.5 (all 1.10.6). Useful for app-size questions; optional one-line addition to the Step 2 framework table.

**B7. Low. Source-account JSON example.** set-up-source-account-ios shows the shared-account subscription payload (`channel` "ANDROID"/"iOS", same `accountId`, `priority` "BULK", `type` "OPTIN", `sourceName` "MAPP_SDK"), and states the change doesn't affect the subscription status response. Our push.md has the second half. The payload is optional.

---

## C. Changed since 2026-11-13 (and the three pages dated 2026-11-12, which our KB also doesn't reflect)

**C1. configure-push-notifications (2026-11-16): not reflected.**
- Substance: step 3 now "Create a service account key for Capillary" (Capillary backend only; iOS app must never contain it; see configure-firebase). Steps 1, 2 and 4, the AppDelegate/NotificationCore/FCM code, the NSE code and the "Gateway configuration" ticket sentence all match our KB.
- Our state: our KB still carries the old "Server Key" Gap (A7) and no service-account note. Action: A7 and B3.

**C2. gamification-ios (2026-11-23): partly reflected.**
- Substance now: minimum SDK 1.10.6; Option A (Remote Config keys) vs Option B (values from Capillary, passed straight to `HydraConfiguration`); resolution order (base URL first, then region); `HydraConfiguration(accountID:server:orgID:gamificationWriteKey:gamificationRegion:gamificationBaseURL:)` + `Hydra.generate(with:)`; SwiftUI uses the same init; Objective-C needs a Swift bootstrap; screen reporting (UIKit, SwiftUI `.gamificationScreen`, ObjC `reportScreen:` / `reportScreenDisappeared:`); `setCapToken`; Banner / Embedded / Loyalty views in Swift, SwiftUI, ObjC; checklist; new event-payload section.
- Our state: everything except the version and the event section matches (see G). Action: A3, B2. I cannot diff against the August copy, so I can't say which of the matching parts are new.

**C3. install-sdk (2026-11-12), ios-sdk-getting-started (2026-11-12), rich-push-notifications (2026-11-12): not reflected.**
- Substance: public repo `hydra-ios-sdk-spm`, no token; 1.10.6; iOS 15.6; Xcode 16.1+; CocoaPods Podfile `hydra_repo = 'https://github.com/Capillary/hydra-ios-sdk-spm.git'`; rich-push SPM target name and Podfile URL changed and the old "Use your private repo URL if applicable" comment is gone.
- Our state: contradicts (A1 to A6, A8, A9).

**C4. configure-firebase (2026-11-16, outside my slice, linked from C1).** FCM V1, role options and sharing methods. See A10 and B3.

---

## D. Pages or sections we don't use at all (and whether we should)

**D1. core-features (2026-03-04), not in `sources` of either file. Medium: use it.** It is the only page that links sign-up/sign-in with `update(customerID:)` (B1) and gives guest-ID handling at sign-out. It conflicts with ios-sdk-api-reference on several details (E4), so cite both and keep a Gap.

**D2. configure-gateway-ios. Low: keep internal only.** It describes Capillary's own DPMG work (Sustenance team, gateway ids 2066 to 2069, `fcmios_bulk` scopes `["campaign"]`, `fcmios_trans` scopes `["optout","otp","highvoltrans","transaction"]`, restart request). The client-facing parts are already in push.md ("bulk and transactional gateways, restart"). Don't copy the table into client guides. Optionally keep the scopes in an internal note.

**D3. iOS In-App page `in-app-messaging_ios`. Medium: fetch it.** ios-sdk and ios-sdk-getting-started link to it ("Configure In-app Messaging"), but it is not in the downloaded set. Our guides carry a Gap ("page wasn't provided"). Add it to the next download so the In-App module (currently only a forwarding call) can be written.

**D4. ios-sdk.md.** Navigation page only; nothing to add.

**D5. set-up-source-account-ios and the Hydra Sample App link** are used. The sample-app link (`https://github.com/Capillary/HydraSampleApp`) is in our Prerequisites. Fine.

---

## E. Problems in the docs themselves (keep as Gap callouts)

**E1. Medium. install-sdk Package.swift is not valid Swift.** `upToNextMajor(from: "1.10.6")` has no leading dot, and `name: “<Project-name>”` uses curly quotes. We silently fixed both (`.upToNextMajor`). Add to the (rewritten) Correction: "snippet in install-sdk lacks the dot; use `.upToNextMajor(from:)`".

**E2. Medium. install-sdk Podfile.** `hydra_repo` is defined inside `target 'YourAppTargetName' do`, then used in the second target block (Ruby local variables in a block are not visible in a sibling block); a prose line "Ensure you are using the correct source or git URL" is left uncommented. Our two existing Corrections remain valid; only the variable name changes (`hydra_repo`). Also unverified: the repo is named `-spm`, and the page installs CocoaPods from it with `:git`; whether it contains podspecs is not stated (confidence low). Podfile also has no version pin (Gap stays).

**E3. Medium. core-features vs ios-sdk-api-reference disagree.**
- Method name `reportUserSignUP` (core-features) vs `reportUserSignUp` (api-ref).
- Sign-up/sign-in: core-features marks only `customerId` required (firstName, lastName, email, phone optional); api-ref marks `customerId`, `firstName`, `lastName`, `phone` mandatory. Our guides (and step_summaries step 5) state the api-ref version only.
- Subscriptions: core-features uses a custom `MySubscription(channel:type:)`; api-ref uses `HydraSubscription(channel:priority:type:)`.
- Change: add a Gap in steps 5 and 6: "core-features shows only `customerId` as required and a different subscription type; ask a Capillary engineer".

**E4. Medium. Push token paths overlap.** initialise-ios-sdk offers `update(deviceToken:)` for the APNs token; configure-push-notifications forwards it through `application(_:didRegisterForRemoteNotificationsWithDeviceToken:)`. The pages don't say if both are needed. Our existing push Gap covers `NotificationCore` vs `hydraCoreSDK` but not this. Add one sentence to that Gap.

**E5. Low. initialise-ios-sdk leftovers.** An empty step "6. Placeholder"; `update((interfaceID id: String)` with a double parenthesis; `Hydra.generate(...)` called without `try` and with the result unused; `UserDefaults.standard.setPromotionalPushOpted(status: Bool = false)` as a call (not valid; `Bool = false` is a default value in a declaration); log-level examples use `Logger.updateLogLevel(level: .critical)` (we already have that Gap). Mention the opt-in call-site problem in the existing step 4 note.

**E6. Low. Naming slips.** configure-push-notifications calls the framework `HydraPushNotificationExtensionService` (real name `HydraPushNotificationServiceExtension`); ios-sdk-getting-started calls it a "notification content extension" (it is a service extension); configure-notification-center_ios tells you to set App Group on "your App Target" for the extension step; its `HydraInboxCoreConfigGenerator` anchor link doesn't exist; ios-sdk-getting-started links the inbox page under `/update/docs/…`; `HydraInboxEmptyNotificationsConfiguration(...)` in a comment vs type `HydraInboxEmptyNotificationsConfigurator`. No change needed in our files beyond not copying them.

**E7. Low. Rich-push CTA types.** The delegate switch uses `CTAActionType.external`, but the prose says "common types like `external_url`". Ours reproduces both (dm L565 / fb L580). Add a short Gap that the raw value (`external` vs `external_url`) isn't stated.

**E8. Low. configure-gateway-ios vs configure-firebase.** The gateway table uses the legacy FCM endpoint `https://fcm.googleapis.com/fcm/send` with `username/password` "test", and talks about a "client token and project ID"; configure-firebase (2026-11-16) says Capillary uses FCM HTTP v1 and a service-account key. Internal inconsistency; keep out of client guides (D2) and note in internal notes.

**E9. Low. ios-sdk-getting-started "perform the following steps" list** omits Source account, Gateway, Core features, Rich push and Inbox, which ios-sdk lists. Doesn't affect us; don't derive step order from it.

---

## F. Impact on derived files

**F1. requirements.yaml (platforms.ios.versions).** Update three values and their `check` strings to match the rewritten guides: SDK version note (drop "Beta; the minimum for gamification", `check: "Beta for UAT/POC"` must change); `value: "iOS 13.0"`, `check: "iOS 13.0"` → `iOS 15.6`; `value: "14 or later"`, `check: "Xcode 14 or later"` → `16.1 or later`. Keep `gaps` (Swift and CocoaPods versions, Firebase SDK minimum). tests/test_requirements.py checks that the strings appear in the guide.

**F2. prerequisites.yaml `ios_repo_access` (blocking: true, `when: ios/direct`).** The item tells clients to request access to `hydra-sdk-ios-packages`. Remove it, or make it a non-blocking "no access needed" note. Note it never applied to `ios/firebase` even though that guide used the same repo. tests/test_requirements.py lines 73-74 assert `ios_repo_access` is present for ios/direct and absent for ios/firebase: update the test. `push_firebase_project` (title/how) can gain "your iOS app must never contain the service-account key". `source:` for `ios_repo_access` points to _shared/prerequisites.md › SDK package access (A9).

**F3. faq.yaml `github-token-why`.** Answer says "Native Android and iOS install from Capillary's private repositories". iOS is now public. Rewrite to Android (and older React Native setups) only; keep the Android evidence lines; drop "iOS" wording. Evidence texts in _shared/prerequisites.md must still exist after A9 edits (`GitHub username + Personal Access Token with read:packages scope`, `pub.dev packages…`). No other FAQ item references iOS-specific facts that changed.

**F4. step_summaries/ios.yaml steps "1" and "2" (both ios/direct and ios/firebase).** Step 1 text and evidence (`Xcode → Settings (Preferences) → Accounts`, `Capillary/hydra-sdk-ios-packages`) go away. Step 2 says "Use the SDK version stated for this integration, not `1.1.0`": drop the `1.1.0` clause.

**F5. step_modules.yaml (`ios/direct` and `ios/firebase`: "9" current screen, "11" Loyalty View).** If Step 1 (authenticate) is deleted, every later step renumbers, and these keys and the `title` checks in tests/test_humanguide.py break silently or loudly. Safer: keep step 1 as a short "Check access: no credentials needed" step, or renumber both YAML files and the step references inside the guides ("step 3", "step 9", "step 11", "Push step 2" …).

**F6. evals.** evals/golden.yaml L156 expects `hydra-sdk-ios-packages`; evals/deep/ios-direct.yaml cases expect `1.7.5-preprod.12`, `upToNextMajor`, "1.1.0", `hydra-sdk-ios-packages`, "Accounts" and rule out `hydra-ios-sdk-spm.git`. All must be rewritten with A1 to A3. PLAN.md L204 lists the old versions (historical).

**F7. Step titles in the guides.** "### 1. Authenticate to the private repo" (dm L49, fb L51) and `Run `pod install`` evidence strings in step_summaries stay. Any portal text derived from the title "private repo" needs updating with F4.

---

## G. Confirmed matching (checked identical on both sides)

- Frameworks and purposes: HydraCore, HydraPushNotification, HydraPushNotificationServiceExtension, HydraInAppMessage, HydraInboxCore, HydraInboxUI; HydraGamification bundled in HydraCore; supported iPhone + iPad.
- `Hydra.generate(with:geoData:supportsPushNotifications:deviceScreenInfo:) throws` signature and parameter table; GeoData and DeviceScreenInfo fields; the `update(customerID:)`, `update(deviceToken:)`, `update(interfaceID:)`, `update(notificationSupport:)` APIs; opt-in function names; console log default `debug`, remote default `none`, both level tables.
- Sign-up/sign-in/profile-update/sign-out/behavioural-event signatures; mandatory fields as per ios-sdk-api-reference; event validity after sign-in/sign-up and invalid after sign-out; behavioural events need Hydra config + org settings.
- Source account: path Organisation settings → Omni Channel Settings → Channel Configurations → MAPP_SDK; Bundle Name with `;` separator; App Signature Android-only; FCM Project ID / FCM Email; Enable Mirror not required; Valid-till; shared account for Android and iOS.
- Push: APNs key steps (download once, don't rename, save Key ID, certificate alternative), upload to Firebase → Cloud Messaging → iOS app configuration, GoogleService-Info.plist added to the target, `FirebaseApp.configure()` + `Messaging.messaging().delegate`, `NotificationCore.shared` + `update(sdk:)`, the four forwarding methods, `didReceiveRegistrationToken` → `update(interfaceID:)`, the full AppDelegate example, NSE target steps and both NotificationService code patterns, `mutable-content: 1`, CTA delegate (`HydraNotificationCallbackDelegate`, `process(cta:notificationPayload:)`, `setNotificationCallbackDelagte` spelling, only `external` handled without a delegate).
- Inbox: App Group format `group.{your_bundle_id}.hydra`, same group on all targets, Push Notifications + Background Modes → Remote notifications, init order, `maximumNotificationCount` default 250, `HydraInboxUIConfiguration` options, show-Notification-Center options, `setHydraInboxUIDelegate` + `refreshNotificationList()`, the API list and the page's internal Kotlin/closure inconsistencies (already Gaps).
- Gamification: `HydraConfiguration(... gamificationWriteKey, gamificationRegion, gamificationBaseURL)`, base-URL-before-region resolution, key mandatory, Option A key names, SwiftUI same init, Objective-C Swift-only init, screen reporting in all three languages, `setCapToken` before Loyalty View, all Banner/Embedded/Loyalty signatures (`embedId:` label for Loyalty), checklist.
- Shared files: Gap in `_shared/push.md` about FCM project must match the registered one is consistent with the new configure-firebase page; troubleshooting's "app signature not sent on iOS" is consistent with set-up-source-account-ios.

---

## Summary

The iOS guides were built from older copies of the pages that matter most (front matter cites 2026-03-04 and 2026-08 dates), and the pages updated on 2026-11-12 and later change the install story: the SDK repo is now public (`hydra-ios-sdk-spm`, no token), the minimum SDK is 1.10.6 (not `1.7.5-preprod.12`), the minimum deployment target is iOS 15.6 (not 13.0), and Xcode 16.1+ is required (not 14). Our own `⚠️ Correction` callouts now say the opposite of the docs and must be removed, and the change ripples into _shared/prerequisites.md, troubleshooting §3, prerequisites.yaml (`ios_repo_access`), requirements.yaml, faq.yaml, step_summaries/ios.yaml, step_modules.yaml numbering, one test and two eval files. The 2026-11-16 push page replaces the "Server Key" step with a service-account note, making our Server Key Gap stale. The 2026-11-23 gamification page adds a Game/CMS event payload section we lack. core-features, which we never used, holds the important "update customerID after sign-in" instruction. Everything else in push, rich push, inbox, core API and gamification code matches.

Counts: A = 12 (A1 to A5 High, A6 to A10 Medium, A11 to A12 Low); B = 7 (1 High, 2 Medium, 4 Low); C = 4; D = 5; E = 9; F = 7; G = 8 bullets of verified facts.
