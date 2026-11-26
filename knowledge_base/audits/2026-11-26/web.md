# WEB slice audit: public docs vs our KB

Scope: 11 public pages (all read in full) against knowledge_base/web/direct.md, web/firebase.md, the Web/Firebase/push parts of _shared/*, requirements.yaml, prerequisites.yaml, faq.yaml, step_summaries/web.yaml, step_modules.yaml.
Page dates: web-sdk 2026-08-18 (the only Web page NOT changed on 11-17 or 11-23); gamification-web and web-sdk-ai-integration-guide 2026-11-23; the other eight 2026-11-17.
Caveat: I have no copy of the older doc versions, so "what changed" is inferred from what our KB (built from pages dated up to 2026-09-24 per its front matter) lacks or says differently.
Verified by script: the `firebase-messaging-sw.js` code block in push-notification-web and in web-sdk-ai-integration-guide is now byte-identical (13,518 chars). The SDKService template in web-sdk-initialisation and the AI guide differ only in comments.

## A. Contradictions (docs and our KB disagree)

**A1. High. `pageView()` option names are wrong in our guides.**
- Docs: web-sdk-initialisation template and web-sdk-api-reference `PageViewOptions` both give `page_url`, `page_title`, `referrer`, `page_category`, `properties`. The AI guide template agrees.
- Ours: `url?`, `title?`, `category?`, `properties?`, with no `referrer`.
  - web/direct.md: template (~l.109-114), step 7 (l.225), API table (l.469).
  - web/firebase.md: template (~l.168-173), step 7 table (l.255), API table (l.492).
  - step_summaries/web.yaml web/direct "7".
- Impact: a TypeScript user following our template passes keys the SDK doesn't read. The URL/title override is silently ignored or fails type-checking.
- Fix: rename to `page_url`, `page_title`, `referrer`, `page_category`, `properties` in all five places and in the API table description. Docs-vs-docs conflict: none; both pages agree.

**A2. Medium. Suppression semantics are narrower in our KB than in the docs.**
- Docs (web-sdk-api-reference `setGamificationSuppressed`): "While suppressed, an overlay never opens, whatever the trigger". This covers screen/path match, an `ACTION_EVENT` from `track()`, and clicks inside a banner/embed/loyalty embed that would open an overlay.
  - Enabling suppression also closes any open overlay (fires `onCampaignClosed`). A game in progress loses unsaved progress.
  - gamification-web: "Embeds, banners and loyalty embeds keep rendering, but clicks inside them can't open an overlay."
- Ours (web/direct.md Gamification › Suppression, ~l.413; web/firebase.md ~l.437): "`EMBEDDED`, `NATIVE_BANNER`, loyalty embeds and explicit opens are unaffected."
- Fix: delete "explicit opens"; add the click, `track()`, close-on-enable and lost-progress points. Update the evals/deep `*-gamification-suppress` questions.

**A3. Medium (confidence about 60%). Browser minimums are scoped to "push" in our KB; the docs present them as the SDK's browser support.**
- Docs: web-sdk-getting-started has a general "Browser support" section that only points to the matrix. The AI guide's "Browser Support" table (Notes: "Full support") is in a general section. Only the push page's column header reads "Push Notifications: Supported".
- Ours: web/direct.md l.29-37 and web/firebase.md l.30-37 head the table "Minimum version (push)" and state "Event tracking, user identification and gamification work on all modern evergreen browsers". That sentence is our own inference.
- requirements.yaml: the four browser rows carry `modules: [push]`. A client without push sees no minimum versions at all.
- Fix: label the table "Minimum browser versions (stated on the push page)". Mark the "all modern evergreen browsers" sentence as not documented. Drop `modules: [push]` from the browser rows, or add a Gap that the docs don't say whether the minimums are push-only. Ask an SME.

**A4. Medium. Our KB says no SDK version is documented; the docs now state one.**
- Docs: web-sdk-getting-started "**SDK version:** `1.10.6`".
- Ours:
  - web/direct.md front matter `sdk_version: null` ("no version is pinned").
  - web/firebase.md front matter `sdk_version: 1.1.0-beta.20260619085241` (from the 2024 guide). Its Gap says the public docs "name no minimum version" (~l.376).
  - _shared/overview.md Gap "production SDK versions aren't documented".
- 1.1.0-beta is lower than 1.10.6, so `@latest` satisfies the old gamification minimum. The docs don't say whether 1.10.6 is a minimum or the current release.
- Fix: record "docs state SDK version 1.10.6 (getting-started, 2026-11-17)" in both files' Requirements and front matter. Keep install unpinned. Reword the firebase.md Gap to "docs don't say whether 1.10.6 is a minimum or just current". Consider a `{sdk_version}` row in requirements.yaml web.

**A5. Medium. Who sends the game/CMS events, and what the client must do about them.**
- Docs (gamification-web "Game and CMS event payloads"; AI guide "Game and CMS events"): "Experience+ sends the following events". "While creating the events, map the fields": `cuid`→`customerId`, `identifierType`, `source` = SDK, `accountId`, all four required.
- Ours (web/direct.md ~l.411, web/firebase.md ~l.435): "The SDK also sends `game_open`... through the normal event pipeline; they will appear in your analytics backend."
- Neither claim is supported by the docs. The docs imply the client must create these seven events in Capillary and map fields. Our overview.md already says behavioural events must exist before they are sent.
- Fix: rewrite per B3 and soften the SDK attribution to a Gap. Update deep eval `web-direct` l.632 (asks for the "SDK itself sends... normal event pipeline" answer).

**A6. Low-Medium. Our Gap about two different service-worker copies is stale.**
- Ours (web/direct.md ~l.334, web/firebase.md ~l.356): "web-sdk-ai-integration-guide's (later) adds a `request.onblocked` handler and a warning for pushes with no `data` payload; push-notification-web's lacks both."
- Docs now: push-notification-web contains both (`request.onblocked` at its l.164-167; "no data payload" warning at l.285-289). A diff of the two code blocks shows they are identical.
- Fix: delete the Gap in both files. Say the file is identical in both pages as of 2026-11-23.

**A7. Low. `@beta` described as "staging".**
- Ours: "Beta (`@beta`: staging / pre-release testing)".
- Docs (web-sdk-install): "pre-release testing — latest features before the next stable cut". "Staging" is not in the docs.
- Fix: drop "staging".

**A8. Low. Stale sentence inside our own files.**
- web/direct.md l.502 and web/firebase.md l.531 say "The step 2/6 template's `traits` type omits `timezone`; add it if needed". Both of our templates already include `timezone`. The docs' template omits it; the docs' API reference lists it.
- Fix: delete the sentence, or restore the docs' template and keep the note.

## B. Missing from our KB (in the docs, important for integrators, absent from our guides)

**B1. Medium. `setTheme(theme)` and the `Theme` type.**
- Docs (web-sdk-api-reference, gamification-web): values `NONE` (default), `LIGHT`, `DARK`, `AUTO`.
  - It appends `darkMode=true|false` to every campaign and loyalty embed URL loaded after the call. A campaign already on screen keeps its look.
  - `AUTO` follows `prefers-color-scheme` at each render.
  - The SDK persists the choice but has no getter, so the service file keeps a localStorage copy (`hydra_gamification_theme`).
- Ours: absent (grep for `setTheme`, `darkMode` finds only RN and Flutter files).
- Fix: add it to Modules › Gamification and the API table. Add an optional block to the service template. Import `Theme` from `cap-hydra-web-sdk`.

**B2. Medium. `setGamificationCallback(GamificationCallback | null)` and its 8 hooks.**
- Docs: `onInitSuccess`, `onInitFailure`, `onEntryPointsLoaded`, `onCampaignOpened`, `onCampaignClosed`, `onAnalyticsEvent`, `onDeepLinkEvent`, `onGameEventTrigger`.
  - All hooks are optional. Hooks fire only after gamification is enabled and `identify()` has run.
  - A later call replaces the earlier hooks, so keep one object. `null` clears them.
- `onDeepLinkEvent` fires "before any navigation the SDK performs". The docs give a window-event plus React Router pattern for SPA deep links. A web app with campaign deep links needs this.
- Ours: absent.
- Fix: add a "Callbacks" paragraph and the hook table to Gamification in both files. Add `setGamificationCallback` to the API table and the service wrapper.

**B3. Medium. Game and CMS event payload spec and field mapping (gamification-web, updated 2026-11-23).**
- Docs: 7 events (5 game, 2 CMS). `cuid` and `event_name` are required on every event.
  - Payloads are flat JSON, and numbers are sent as numbers.
  - Mapping when creating the events: `cuid`→`customerId`, `identifierType` = mobile/email/externalId as passed to the SDK, `source` = SDK, `accountId` = SDK account ID. All four are required.
  - Per-event attributes, e.g. `game_open`: `campaign_id`, `game_type`, `entry_surface`, `embed_id`, `entry_point_id`, `entry_point_location`, `deep_link_url`, `hyper_link_url`.
- Ours: only the 7 names, with a wrong attribution (A5).
- Fix: add a compact table (event, when it fires, attributes) and the 4-row mapping. Add a Gap: where in Capillary these events are created isn't stated. Link it to the overview rule that events must exist first.

**B4. Medium. `track()` can trigger gamification (`ACTION_EVENT` entry points).**
- Docs (api-reference): an `ACTION_EVENT` entry point opens from a `track()` call. `onGameEventTrigger(eventName, { reason: 'NO_GAME_CONFIGURED' })` fires when `track()` has no matching entry point.
- Ours: absent. Integrators should know that event names passed to `trackEvent()` can open campaigns.
- Fix: one sentence under Gamification, plus the hook in B2.

**B5. Low-Medium. Scope of `disableSDK()`.**
- Docs: it drops new `track()`/`pageView()` events, but "Does not affect `identify()`, `reset()`, or gamification events".
- Ours (step 8, Known Issues, API table): only "new events dropped".
- This matters for consent/GDPR claims.
- Fix: add the sentence to step 8 (direct) and step 7 (firebase), and to the API table.

**B6. Medium-Low. Service-file template lacks the gamification wrappers the docs now include.**
- Docs template (web-sdk-initialisation and AI guide): imports `GamificationCallback`, `Theme`; wrappers `setTheme`, `getSavedTheme`, `setGamificationSuppressed`, `getSavedGamificationSuppressed`, `setGamificationCallback`; private `saveSetting`/`readSetting` with try/catch around localStorage.
- Ours: template has none of these. Our own rule is "components never import HydraSDK directly", so suppress/theme/callback calls have no wrapper to go through. We only say "add service wrappers" for the path-tracking methods.
- Docs rationale: `isGamificationSuppressed()` returns `false` right after reload until async init finishes, and there is no theme getter. A UI that shows either value should seed from the localStorage copy. Ours lacks this too.
- Fix: add an "only if gamification" block to the template in both files.

**B7. Medium-Low. The full service-worker file is not in our KB.**
- Ours: only the top of the file plus "...rest of the published file unchanged", with a link to the docs page. An offline kit or AI assistant cannot reproduce the file, and the docs say do not change its logic.
- Now that both public pages carry the identical file (A6), store it once as a shared asset or fenced block.
- Fix: pick one canonical copy, record its source page and date, and embed it.

**B8. Low. Service-worker lifecycle: no `skipWaiting` / `clients.claim`.**
- Docs: the worker installs without `skipWaiting` and activates without `clients.claim`. The app can post `{ type: "SKIP_WAITING" }` to apply a new version.
- Relevance: our Known Issue "DLR events not recorded: old service worker cached" only suggests Unregister.
- Fix: add one line to that row.

**B9. Low. Where each `MY_*` value comes from (web-sdk-initialisation "Replacing placeholders").**
- Docs: API key / project ID / app ID: Project Settings → General. Sender ID: Project Settings → Cloud Messaging. VAPID key: Cloud Messaging → Web Push certificates. `MY_REMOTE_CONFIG_KEY`: the Remote Config parameter key.
- Ours: scattered, no table.
- Fix: add a small table to firebase-setup.md or the Web files.

**B10. Low. URL path rule "or SPA hash route".**
- Docs: a path-segment rule matches "anywhere in the path or SPA hash route".
- Ours: "anywhere in the path". The docs' "(see below)" has nothing below it (E7).
- Fix: add "or SPA hash route", marked unconfirmed.

## C. Changed since 2026-11-13 (substance, and whether our KB reflects it)

I cannot see the old versions. Items below are what the dated pages say that our KB does not, or says differently.

**C1. gamification-web (2026-11-23).** Substance:
- New "Game and CMS event payloads" section: 7 events, attributes, samples, field mapping. Not reflected (A5, B3).
- "Theme, Suppression & Callbacks — Host App Examples": ThemePicker, CampaignToggle, deep-link hook. Not reflected (B1, B2, B6).
- Containers (sizes), 11 content types, path-rule table, loyalty embed and `setCapToken` text: reflected, identical.

**C2. web-sdk-ai-integration-guide (2026-11-23).**
- Adds the pointer to Game and CMS events.
- Remaining content mirrors web-sdk-initialisation, plus `brandId`/`applicationId`/`notifications` rows (E3).
- Reflected except the items in A and B.

**C3. push-notification-web (2026-11-17).**
- The service-worker file now has `onblocked` and the no-data-payload warning. Our Gap is stale (A6).
- Browser matrix, `serviceWorkerPath` table, `/logo192.png` and Firebase 10.7.1 notes: reflected.

**C4. web-sdk-getting-started (2026-11-17).**
- States SDK version 1.10.6, the release channels, and the 7-step roadmap. Version not reflected (A4).
- The roadmap order differs from ours (D5).

**C5. web-sdk-initialisation (2026-11-17).**
- Direct-config as default, `notifications.messaging`, `hydra-fcm`, rules, field tables: reflected.
- Not reflected: pageView option names (A1), the gamification wrappers (B6).

**C6. web-sdk-api-reference (2026-11-17).**
- 16 methods (adds `setTheme`, `setGamificationCallback`); our guides and CHANGELOG list 14. Suppression and `disableSDK` details (A2, B5).
- `isGamificationSuppressed()` is `false` until init finishes.

**C7. web-sdk-troubleshooting, prerequisites, web-sdk-install, configure-firebase-web (2026-11-17).**
- Checked line by line: reflected. CSP entries and example are identical. The error table, 6 checks, rollback, Remote Config steps and VAPID steps all match.
- Our Gap about the 2024 Realtime Database / Cloud Messaging checks is still valid.

**C8. web-sdk.md (2026-08-18).** Navigation page only; not in the 11-17/11-23 window as the brief expected. No facts.

**C9. Our own front matter.** `sources` in both Web files says "updated 2026-08-18 to 2026-09-24"; pages are now dated to 2026-11-23. Update it when the above is merged.

## D. Pages or sections we don't use at all (and whether we should)

**D1. gamification-web "Host App Examples" (ThemePicker, CampaignToggle, `useGamificationDeepLinks`).** Unused. Yes: adapt as framework-neutral snippets for B1, B2, B6.

**D2. gamification-web "Game and CMS event payloads" and "Field mapping".** Unused (names only). Yes: at least the table and mapping (B3).

**D3. web-sdk-api-reference `setTheme`, `setGamificationCallback`, `ACTION_EVENT`, `onGameEventTrigger`.** Unused. Yes (B1, B2, B4).

**D4. web-sdk-ai-integration-guide "Step 0" questions and "After completing the implementation" checklist.** Used (paraphrased). No change needed. The "Decide before writing code" lists match the 8 questions.

**D5. web-sdk-getting-started "Integration roadmap".**
- Docs order for Remote Config: install, initialise, then Firebase. Ours (firebase.md): Firebase steps 1-4 first, then install.
- Ours is workable, because initialise needs the Firebase values. No change needed; optionally note the difference.

**D6. web-sdk.md.** Navigation only. Nothing to use.

**D7. iOS-Safari web push.** The docs say nothing about iOS/iPadOS requirements (for example installing the site to the Home Screen). If we add it, mark it as outside Capillary's docs. Optional Gap.

## E. Problems in the docs themselves (keep as Gap callouts)

**E1. Medium (confidence about 60%). Browser matrix looks inconsistent.**
- push-notification-web and AI guide: Chrome 109+, Firefox 140+ (ESR), Safari 26.3+, Edge (Chromium) 149+.
- Chrome 109 and Edge 109 are the same Chromium line. An Edge minimum of 149 beside Chrome 109 looks like a typo for 109. Safari 26.3 is also a very recent floor.
- Also: the push page labels the table "Push Notifications: Supported", while the AI guide labels it "Full support".
- Keep as Gap: "Edge 149+ looks inconsistent with Chrome 109+; confirm". requirements.yaml currently shows "Edge 149 or later".

**E2. Medium. Push is "always included" in one place and optional in all others.**
- web-sdk-ai-integration-guide Step 0 Q1: core WebSDK (event tracking, user identification, push notifications) "is always included — this is not optional".
- The same page's Q3 asks whether push is needed. prerequisites and getting-started say Firebase is needed only for push or Remote Config.
- Our guides follow the "optional" reading. Add a one-line Gap.

**E3. Low-Medium. The configuration reference differs between pages.**
- web-sdk-initialisation (2026-11-17) optional-fields table lists only `appVersion` and `retryDelays`, and its Remote Config fields table omits `brandId` and `applicationId`.
- web-sdk-ai-integration-guide (2026-11-23) lists `notifications`, `brandId` and `applicationId`. configure-firebase-web's JSON example has only 6 fields.
- Our tables follow the AI guide. Keep the existing Gap on who supplies `brandId`/`applicationId`; add that the init page no longer lists them.

**E4. Low. Misleading table heading.**
- web-sdk-initialisation: "Remote Config fields - Remote Config bootstrap only (do NOT set manually in `initialize()`)". The following sentence says direct-config passes the same fields directly.
- Our guides already resolve it. No change beyond a comment.

**E5. Low-Medium. `gamificationBaseUrl` is unclear.**
- web-sdk-initialisation: region "Derives the API base URL automatically", yet the base URL is also "Yes*" (required). The example is `https://api-us.customerglu.com`, a third-party vendor domain.
- prerequisites says the `capillarytech.com` connect-src entry covers "gamification" traffic. The customerglu host is not in the CSP list. Our Gap already notes the customerglu mismatch.
- Add the first two points to the Gap.

**E6. Low. Web `baseURL` example differs from our cluster table.**
- Docs: `https://api.example.capillarytech.com` (configure-firebase-web). Our `_shared/prerequisites.md` table lists `https://mapp-incrm.api.capillarytech.com/` etc., taken from mobile sources.
- Whether Web uses the same hosts is not stated. Add a Gap line under "Base URL by cluster" for Web.

**E7. Low. Dangling cross-reference.** gamification-web path rules: "SPA hash route (see below)" has no matching text below.

**E8. Low. "Throws before initialize" vs "calls queue".**
- gamification-web: "calling these methods before `initialize()` throws".
- api-reference and rules: every method except `initialize()` waits for init, and "no `isInitialized()` guards".
- Likely both true (never called vs async still running). Worth a one-line note.

**E9. Low. `initialize()` "throws" is swallowed by the template.**
- web-sdk-troubleshooting: direct-config `initialize()` "throws a synchronous Error". The documented template wraps the call in try/catch, so the visible symptom is `Failed to initialize SDK:` in the console.
- Our Known Issues row says "throws"; add the console wording.

**E10. Low. Troubleshooting references a problem it doesn't list.** push-notification-web ends by pointing to troubleshooting for "notifications missing a body". The troubleshooting table has no such row. Our Known Issue for it (campaign sent `notification` instead of `data`) is our own inference from the worker code ("we trust data only").

**E11. Low. Orphan content in configure-firebase-web.** Step 2 has two screenshots (install Firebase CLI, deploy Firebase Hosting) with no text. Step 3 list numbering is "3." then "4)".

**E12. Low. Event surface names don't match container names.** `entry_surface` values are `popup`, `floating_icon`, `modal`, `banner_embedded`. Container names are `POP_UP`, `ICON_BUTTON`, `BOTTOM_SHEET`, `CHAT_BOX`, `EMBEDDED`, `NATIVE_BANNER`. No mapping is given.

## F. Impact on derived files (requirements.yaml, prerequisites.yaml, faq.yaml, step titles)

**F1. High. step_summaries/web.yaml `web/direct` step "7":** change `{ url, title, category, properties }` to `{ page_url, page_title, referrer, page_category, properties }` (A1). Its evidence strings ("Call on every route change.", "sdkService.trackPageView();") remain valid.

**F2. Medium. requirements.yaml (web):**
- Browser rows: see A3 (remove or explain `modules: [push]`). Note E1 on the Edge value.
- Add a Hydra SDK version row or note for 1.10.6 (A4). Keep `check` strings present in both guides.
- The `check: "cap-hydra-web-sdk@beta"` row is still correct.
- Add to `gaps`: iOS-Safari web push (D7), and whether browser minimums are push-only.
- The Node/bundler/firebase-version Gap is still valid; the docs still give no versions.

**F3. Medium (confidence about 60%). faq.yaml answers shown to Web users that are wrong or irrelevant for Web.**
- `events-missing`: "Events only count after a sign-in or sign-up". It has no platforms tag and its evidence is from the mobile-sourced overview.md.
  - Web docs track anonymous visitors: `getAnonymousId()` works regardless of auth state, and smoke test 2 (page view) runs before test 4 (identify) and expects an outbound POST.
  - Tag it `[android, ios, react-native, flutter]` or add a Web answer.
- `registration-must-match` (Android app ID, SHA256, FCM Project ID) and `which-base-url` (mapp-* cluster hosts) also show for Web. Tag `registration-must-match` to mobile and note the Web base URL gap (E6).
- Add Web items with evidence in the Web files:
  - "Do I need Firebase for Web?" (no, only for push or Remote Config);
  - "serviceWorkerPath for a sub-path app";
  - "Why don't gamification campaigns show" (all three fields, `identify()`, suppression);
  - "CSP blocks the SDK".

**F4. Low-Medium. prerequisites.yaml.**
- The docs' Prerequisites page lists CSP configuration as a "before you begin" item. Add a non-blocking client item `web_csp` for `platforms: [web]` (source: web/*.md CSP step).
- The existing Web items (`web_firebase_config`, `web_vapid_key`, `org_id`, `gamification_base_url`, `gamification_view_ids`, `firebase_project` for web/direct + push) all match the docs. No change needed.

**F5. Low. step_modules.yaml has no `web/*` entries.**
- Nothing to fix if B1/B2/B6 go under Modules › Gamification.
- If they become numbered steps, add `modules: [gamification]` entries with a `title` phrase, or `tests/test_humanguide.py` and the human steps document will show them to everyone.

**F6. Low. Deep evals and kits.**
- `evals/deep/web-*.yaml`: the suppression question (A2) and the engagement-events question at web-direct l.632 (A5) need new expected answers. Add questions for page-view option names, theme/callbacks, and the stale SW Gap.
- `evals/results/**` kits embed the old template and need a rebuild.

**F7. Low. CHANGELOG** says Web has "14 public methods". The docs list 16.

## G. Confirmed matching (checked identical on both sides)

- Package `cap-hydra-web-sdk`; install commands for npm, yarn, pnpm and bun (lock-file detection, npm default); `@latest` default and `@beta`.
- Direct-config required fields `accountId`, `baseURL`, `orgId`; Remote Config required fields `firebaseConfig` and `remoteConfigKey`. The mode is picked by whether `remoteConfigKey` is present.
- Defaults: `retryDelays` `[60000,120000,240000,480000,900000]`, `source` `WEBPUSH`, `channelType` `web`, `sessionTimeoutMinutes` 30, `batchSize` 50, `debugLevel` `NONE` (levels NONE/ERROR/WARN/INFO/DEBUG/VERBOSE).
- `notifications: { messaging: getMessaging(firebaseApp), vapidKey, serviceWorkerPath }`; Firebase app named `"hydra-fcm"`; the SDK never calls `initializeApp()`/`getMessaging()` itself.
- `serviceWorkerPath` examples (`/firebase-messaging-sw.js` and `/my-app/firebase-messaging-sw.js`); file name must stay `firebase-messaging-sw.js`.
- Service worker content: Firebase compat 10.7.1, `/logo192.png` fallback, data-only payload, click resolution order (URL action, then CTAs, then `redirectUrl`/`link`/`url`), DLR IndexedDB `WebSDK_DLR_SW`, events `received`/`clicked`/`dismissed`, and the warning not to read the `push` body.
- All three gamification fields required together; silently skipped if absent. Remote Config JSON field names and the "publish changes" step.
- VAPID path (Project Settings → Cloud Messaging → Web configuration → Web Push certificates → Generate key pair).
- CSP: all five directives, every entry, and the example block.
- `USER_REGISTER` for login and sign-up, `USER_UPDATE` for profile only, identifier types, `reset()` on logout and clearing the token.
- Rules: module-load `initialize()` (not in `useEffect`/`ngOnInit`), no `await`, no `isInitialized()`, no re-identify on refresh, `initialize()` safe to call twice.
- Consent behaviour (`disableSDK`/`enableSDK`, queued events kept in IndexedDB), `setCapToken`/`getCapToken` (`?capToken=`, IndexedDB, cleared on `reset()`, immediate re-render), `getAnonymousId` (`string | null`).
- Containers (ICON_BUTTON 160×160, CHAT_BOX 360×580, POP_UP max 1000×740, BOTTOM_SHEET, EMBEDDED, NATIVE_BANNER) and the host-HTML column.
- All 11 content types, including `PROGRAM` and `REWARD` URL patterns, and all 7 URL path rule formats.
- Loyalty `embedId` rule (`getElementById` at render time; silently skipped if missing) and `hookId` MutationObserver behaviour.
- Manual path tracking (`enablePagePathTracking(false)` + `onScreenChanged`).
- The 6 validation checks, the troubleshooting error rows, the DevTools "Verbose" hint, and the rollback steps.
- The remaining Gaps are still true: no permission-prompt, foreground-message, or test-push documentation; no region value list beyond `'us'`/`'me'`; no Account Linking guidance for Web; no Node/bundler/firebase version; no Realtime Database/Cloud Messaging check in the current docs.
- Prerequisites page: accountId/orgId/baseURL, Firebase project only if push or Remote Config, and gamification credentials.

## Summary

Our Web guides are accurate on setup, init, push, service worker, CSP, containers, content types, path rules and troubleshooting, and the matching list above was checked fact by fact. The pages updated on 2026-11-17 and 2026-11-23 expose one clear error and a set of gaps:
- The one clear error is the `pageView` option names (A1), which break type-checking and silently ignore overrides.
- The biggest gaps are the gamification host-API additions: theme, callbacks, deep links, `ACTION_EVENT` and richer suppression semantics (A2, B1, B2, B4, B6).
- The new game/CMS event spec and field mapping (A5, B3) are also missing.
- We have a stale Gap about differing service-worker copies (A6) and an SDK version (1.10.6) we don't record (A4).
- We scope browser minimums to push (A3) on our own inference.
- Several doc inconsistencies should become Gap callouts, notably the odd Edge 149+ and the Step 0 push wording (E1, E2).
- Derived files need one fix (step_summaries "7"), a rethink of the browser rows and a Web-aware FAQ.

Counts: A = 8, B = 10, C = 9, D = 7, E = 12, F = 7, G = 1 list (about 20 verified groups).
