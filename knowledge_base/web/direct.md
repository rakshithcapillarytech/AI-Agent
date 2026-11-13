---
platform: web
config_mode: direct
sdk_package: cap-hydra-web-sdk
sdk_version: null   # no version is pinned: production `@latest` (default) or `@beta` (web-sdk-install)
modules_covered: [core, push, visitor, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, multi_account]
sources: ["Integration document _ Experience+ pp.60–71 (WEB Hydra SDK – Integration Guide, Firebase excluded)", "Capillary developer docs (docs.capillarytech.com): web-sdk, web-sdk-getting-started, web-sdk-install, web-sdk-initialisation, configure-firebase-web, push-notification-web, gamification-web, web-sdk-api-reference, web-sdk-ai-integration-guide, web-sdk-troubleshooting (updated 2026-08-18 to 2026-09-24)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Web (without Firebase)

**Direct-config bootstrap** (the SDK's default): `accountId`, `baseURL` and `orgId` are passed straight to `HydraSDK.initialize()`. The SDK picks the mode by whether `remoteConfigKey` is present, so never pass `remoteConfigKey` or `firebaseConfig`. No Firebase project is needed unless the app also uses web push (Modules → Push).

## Coverage
| Module | Status |
|---|---|
| Core: install, service file, init, identify, profile update, reset, events, page views, consent, CSP | Documented |
| Push (Firebase Cloud Messaging) | Documented: your own Firebase Messaging instance, VAPID key, service-worker file, action buttons / CTAs, delivery receipts |
| Visitor | `getAnonymousId()` |
| Gamification: containers, content types, URL path rules, loyalty embeds, suppression, manual path tracking | Documented |
| In-App, Inbox, Multi-account | Not documented for Web |

## Requirements
- `cap-hydra-web-sdk` from npm (step 1), in `dependencies`. TypeScript or JavaScript.
- Push only: the Firebase JS SDK (`firebase`) in your project; the Web SDK never installs or bundles Firebase.
- Event tracking, user identification and gamification work on all modern evergreen browsers. Push needs Service Worker and Push API support. **Internet Explorer is not supported.**

| Browser | Minimum version (push) |
|---|---|
| Chrome | 109+ |
| Firefox | 140+ (ESR) |
| Safari | 26.3+ |
| Edge (Chromium) | 149+ |

> ⚠️ Gap: no Node.js / bundler / framework versions are stated, nor which `firebase` npm version matches the SDK (the service worker loads Firebase `10.7.1` compat scripts and should stay "aligned with the SDK's expected Firebase version", which isn't given). Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md`. From the Capillary team: Account ID → `accountId`, Base URL → `baseURL`, Org ID → `orgId`; for gamification, all three of Gamification Write Key → `gamificationWriteKey`, Gamification Region → `gamificationRegion`, Gamification Base URL → `gamificationBaseUrl`.

Only if used:
- **EMBEDDED / NATIVE_BANNER containers:** each `hookId`, configured in the gamification dashboard (entry point settings) and provided by the Capillary team.
- **Loyalty embeds:** each `embedId` from the Capillary team, and a Capillary short-lived token for the logged-in user (how to obtain it isn't documented; see `_shared/prerequisites.md`).
- **URL path rules** per entry point: configured in the gamification dashboard, provided by the Capillary team during campaign setup.
- **Web push:** your Firebase project's web config and a VAPID key (Modules → Push).

**Decide before writing code** (the official AI runbook asks these first; defaults in brackets): release channel [production]; push notifications?; gamification?; loyalty embeds (only if gamification)?; cookie consent / GDPR?; Firebase credentials ready (only if push)?; bootstrap mode [direct-config, this file]. Generate only what the answers need, and state any default you assumed.

> ⚠️ Gap: not documented: what the client sends to register a web app, the full list of region values (docs show `'us'`, `'me'`), and whether the `identify()` identifier must match the CRM Account Linking Identifier. Ask a Capillary engineer.

## Steps

### 1. Install the SDK
Use the lock file in the project root to pick the package manager (none → npm).

| Lock file | Production (`@latest`, default) | Beta (`@beta`: staging / pre-release testing) |
|---|---|---|
| `package-lock.json` / none | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |
| `yarn.lock` | `yarn add cap-hydra-web-sdk` | `yarn add cap-hydra-web-sdk@beta` |
| `pnpm-lock.yaml` | `pnpm add cap-hydra-web-sdk` | `pnpm add cap-hydra-web-sdk@beta` |
| `bun.lockb` | `bun add cap-hydra-web-sdk` | `bun add cap-hydra-web-sdk@beta` |

For push, also install `firebase`.

### 2. Create the SDK service file and initialise at module load
One service file wraps every SDK call; follow the app's own file naming, folder and export conventions (`.js` if not using TypeScript). Include only the methods for features the app uses. Add the `firebase/*` imports and the `notifications` block **only for push**; otherwise delete both (Modules → Push). Uncomment the three `gamification*` lines together, only for gamification.

```ts file=src/services/sdkService.ts
import { HydraSDK } from "cap-hydra-web-sdk";
// Only needed if push notifications are required:
import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";

class SDKService {
  initialize() {
    try {
      // Only needed if push notifications are required
      // const firebaseApp = initializeApp(
      //   { apiKey: "MY_FIREBASE_API_KEY", /* ...rest of Firebase config */ },
      //   "hydra-fcm",
      // );

      HydraSDK.initialize({
        accountId: "{{account_id}}",
        baseURL: "{{base_url}}",
        orgId: "{{org_id}}",
        appVersion: "1.0.0", // my app's version string

        // Only include if using gamification — obtain from the Capillary team:
        // gamificationWriteKey: "{{gamification_key}}", // required together with the two below, only if using gamification
        // gamificationRegion: "{{gamification_region}}", // e.g. 'us', 'me'
        // gamificationBaseUrl: "{{gamification_base_url}}", // gamification API base URL for your region

        // Only include this block if push notifications are needed:
        // notifications: {
        //   messaging: getMessaging(firebaseApp),
        //   vapidKey: "MY_VAPID_KEY",
        //   serviceWorkerPath: "/firebase-messaging-sw.js",
        // },
      });
    } catch (error) {
      console.error("Failed to initialize SDK:", error);
    }
  }

  // --- Page Views ---
  trackPageView(options?: {
    url?: string;
    title?: string;
    category?: string;
    properties?: Record<string, unknown>;
  }) {
    HydraSDK.pageView(options);
  }

  // --- Custom Events ---
  trackEvent(name: string, properties?: Record<string, unknown>) {
    HydraSDK.track(name, properties);
  }

  // --- User Identity ---
  identifyUser(
    identifierType: "email" | "mobile" | "externalId",
    cuid: string,
    actionType: "USER_REGISTER" | "USER_UPDATE",
    traits?: {
      firstName?: string;
      lastName?: string;
      gender?: string;
      birthday?: string;
      city?: string;
      country?: string;
      timezone?: string;
      email?: string;
      mobile?: string;
      externalId?: string;
      custom?: Record<string, unknown>;
    },
  ) {
    HydraSDK.identify({
      identifier: { type: identifierType, cuid },
      actionType,
      traits,
    });
  }

  // --- Get Anonymous Visitor ID (available regardless of auth state) ---
  getAnonymousId(): string | null {
    return HydraSDK.getAnonymousId();
  }

  // --- Logout / Reset ---
  reset() {
    HydraSDK.reset();
  }

  // --- Cookie Consent ---
  enableTracking() {
    HydraSDK.enableSDK();
  }

  disableTracking() {
    HydraSDK.disableSDK();
  }

  // --- Loyalty Embeds ---
  setCapToken(token: string) {
    HydraSDK.setCapToken(token);
  }

  getCapToken(): string | null {
    return HydraSDK.getCapToken();
  }
}

export const sdkService = new SDKService();

// IMPORTANT: Initialize at module load — NOT inside useEffect, ngOnInit, or similar hooks
sdkService.initialize();
```

Optional `initialize()` fields (`brandId`, `sessionTimeoutMinutes`, `debugLevel`, `retryDelays` …): API Reference.

**Rules to enforce:**
- Call `HydraSDK.initialize()` at module load time (top level of the file), **never** inside React `useEffect`, Angular `ngOnInit`, `mounted()` or any async lifecycle hook. Import the service file from the app entry point.
- `initialize()` is safe to call more than once; later calls return the existing instance.
- Components **never** import `HydraSDK` directly; every call goes through the service.
- Don't `await` SDK calls (all are fire-and-forget) and don't add `isInitialized()` guards: the SDK queues calls internally until ready.
- **Don't re-identify the user on page refresh**; the SDK persists user context in IndexedDB.
- When an AI assistant runs this integration it implements only install, this service file and (push) the service worker; it leaves `MY_*` / `YOUR_*` placeholders it has no values for, reminds the developer to replace them, and doesn't create Firebase resources. Wiring calls into the app flow (steps 3–8) is the developer's choice.

> ⚠️ Correction: ✅ Use the template above (web-sdk-initialisation, web-sdk-ai-integration-guide). ❌ Don't use the source sample that has no comma after `gamificationBaseUrl` (Integration document p.62); it is a JavaScript syntax error. *Pending SME confirmation.*

### 3. Identify the user at sign-in and sign-up
Use `"USER_REGISTER"` for **both** login and sign-up. Identifier types: `"email"`, `"mobile"`, `"externalId"`; `cuid` is the user's value for that type; `traits` are optional (API Reference).

```js
sdkService.identifyUser("email", "testuser@example.com", "USER_REGISTER", {
  firstName: "Test",
  lastName: "User",
});
```

With gamification on, every `identify()` call fetches and renders campaigns (Modules → Gamification).

### 4. Update the profile (optional)
Same call with `"USER_UPDATE"`, for profile changes only, never at login.

### 5. Reset on sign-out
```js
sdkService.reset();
```
Clears user context and the Capillary token (`setCapToken`); tracking returns to anonymous.

### 6. Track custom events
```js
sdkService.trackEvent("test_event", { source: "smoke_test" });
```

> ⚠️ Correction: ✅ Use `HydraSDK.track(...)` and `HydraSDK.pageView(...)`, called through the service (web-sdk-api-reference). ❌ Don't use `WebSDK.track(...)` / `WebSDK.pageView(...)` (event and page-view examples, Integration document pp.64–65); `WebSDK` is never imported. *Pending SME confirmation.*

### 7. Track page views
Call on every route change. With no arguments it captures the current URL and title; pass `{ url, title, category, properties }` to override any of them.

```js
sdkService.trackPageView();
```

### 8. Wire up cookie consent (optional)
```js
sdkService.disableTracking(); // Events dropped
sdkService.enableTracking(); // Queued events resume
```
While disabled, new events are dropped; already-queued events stay in IndexedDB and are sent on re-enable. Persist the consent decision in your own storage and restore it on app load by calling `enableTracking()` / `disableTracking()`.

### 9. Allowlist the SDK's domains in the CSP (if the site has one)
**Add these to the existing directives; don't replace them.**

| Directive | Entries |
|---|---|
| `connect-src` | `https://*.capillarytech.com` (core API, gamification, loyalty; always); `https://*.googleapis.com`, `https://*.firebaseio.com`, `https://*.firebaseapp.com` (push only, in this mode); `https://*.posthog.com` (SDK diagnostics; always) |
| `script-src` | `'self'`; `https://*.gstatic.com` (push only: Firebase Messaging scripts in the service worker); `https://*.posthog.com` |
| `frame-src` | `https://*.capillarytech.com` (loyalty embeds; gamification CAMPAIGN, WALLET, NUDGE, PROGRAM, REWARD) |
| `img-src` | `https://*.capillarytech.com` (loyalty embeds; gamification STATIC) |
| `worker-src` | `'self'`, `blob:`, `data:` (required for posthog) |

```text
connect-src 'self' https://*.capillarytech.com https://*.googleapis.com https://*.firebaseio.com https://*.firebaseapp.com https://*.posthog.com;
script-src 'self' https://*.gstatic.com https://*.posthog.com;
frame-src 'self' https://*.capillarytech.com;
img-src 'self' https://*.capillarytech.com;
worker-src 'self' blob: data:;
```

Without push or gamification / loyalty, only the `capillarytech.com` and `posthog.com` entries are needed.

> ⚠️ Gap: the docs' example `gamificationBaseUrl` is on `customerglu.com` (`https://api-us.customerglu.com`), which isn't in the `connect-src` allowlist. Ask a Capillary engineer whether gamification needs that domain allowlisted.

## Modules

### Push
Optional. The SDK never calls Firebase's `initializeApp()` / `getMessaging()` itself: you create a Firebase app and Messaging instance and pass it as `notifications.messaging`. Omitting `notifications` disables push with no compile-time or runtime error.

**P1. Firebase console** (`_shared/firebase-setup.md` has the common steps): create a project (<https://console.firebase.google.com/>, "Add project", name, Google Analytics optional, "Create project"); click the Web icon (`</>`), enter a nickname, "Register app", and copy the whole `firebaseConfig` object; then **Project Settings → Cloud Messaging → Web configuration → Web Push certificates → "Generate key pair"** and copy the VAPID key (→ `notifications.vapidKey`). Remote Config isn't needed in this mode.

**P2. Install** `firebase` (step 1).

**P3. Pass the Messaging instance** in the step 2 service file: uncomment the `initializeApp(...)` lines (fill in the full Firebase config) and the `notifications` block. Name the app `"hydra-fcm"` as shown, so it never collides with another Firebase app the code initialises.

```ts
const firebaseApp = initializeApp(
  { apiKey: "MY_FIREBASE_API_KEY", /* ...rest of Firebase config */ },
  "hydra-fcm",
);

HydraSDK.initialize({
  accountId: "{{account_id}}",
  baseURL: "{{base_url}}",
  orgId: "{{org_id}}",
  notifications: {
    messaging: getMessaging(firebaseApp),
    vapidKey: "MY_VAPID_KEY",
    serviceWorkerPath: "/firebase-messaging-sw.js",
  },
});
```

| App served at | `serviceWorkerPath` |
|---|---|
| `https://example.com/` | `"/firebase-messaging-sw.js"` |
| `https://example.com/my-app/` | `"/my-app/firebase-messaging-sw.js"` |

**P4. Create the service worker.** It handles background (data-only) pushes, action buttons, CTAs and delivery receipts (DLR).
- Create `firebase-messaging-sw.js` in `public/` (or the static-asset directory served at the site root, e.g. `static/`, `assets/` or the bundler's public path). Vite, CRA and Next.js serve `public/` at the site root. It must be reachable at the app's root scope.
- **Don't rename the file. Don't change its logic**; replace only the `YOUR_*` values in the Firebase config block, with the same values as the service file. (An AI assistant leaves the `YOUR_*` placeholders for the developer.)
- Notification `title`, `body`, `icon` etc. are read from the push **`data`** payload, not `notification`: Capillary campaigns must send them as data fields.
- Icon and badge fall back to `/logo192.png`: add it to `public/` or change the fallback paths.
- Receipts (`received`, `clicked`, `dismissed`) go to IndexedDB store `WebSDK_DLR_SW` and the app is notified by `postMessage`; the SDK processes them automatically.
- Clicks resolve in order: an action that is itself a URL (`https://...`) opens directly; else the action is looked up in the payload's `ctas` (`[{ action, actionLink }]`); else the default click URL (`data.redirectUrl` / `data.link` / `data.url`). Buttons and CTAs are configured on the push campaign in the dashboard.

Copy the **full file verbatim** from <https://docs.capillarytech.com/docs/push-notification-web#service-worker-file> (also in web-sdk-ai-integration-guide, "Service Worker File"). Its top, the only part you edit:

```js file=public/firebase-messaging-sw.js
// firebase-messaging-sw.js
importScripts(
  "https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js",
);
importScripts(
  "https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js",
);

// self.firebase is injected into the service worker global scope by importScripts above
self.firebase.initializeApp({
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  databaseURL: "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID",
});

const messaging = self.firebase.messaging();
console.log("[FCM SW] Initialized");
// ... rest of the published file unchanged: DLR helpers, push / onBackgroundMessage /
// notificationclick / notificationclose / install / activate / message handlers
```

> ⚠️ Correction: ✅ Use `notifications: { messaging: getMessaging(firebaseApp), vapidKey, serviceWorkerPath }` (push-notification-web, web-sdk-initialisation). ❌ Don't put `firebaseConfig` in `notifications` (Integration document p.62). *Pending SME confirmation.*

> ⚠️ Gap: the two published copies of the service worker differ: web-sdk-ai-integration-guide's (later) adds a `request.onblocked` handler and a warning for pushes with no `data` payload; push-notification-web's lacks both. Ask a Capillary engineer which is current.

> ⚠️ Gap: not documented: the browser permission prompt (who triggers it and when), foreground message handling, and how to send a test push. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Visitor
Tracking is anonymous before `identify()` and after `reset()`; `source` defaults to `WEBPUSH`. `sdkService.getAnonymousId()` returns the backend-assigned anonymous visitor ID (`string | null`), safe at any time regardless of auth state.

> ⚠️ Correction: ✅ Use `HydraSDK.getAnonymousId()` for the visitor ID (web-sdk-api-reference lists every public method; `getUser()` isn't one). ❌ Don't use `HydraSDK.getUser()` (Integration document pp.60–71). *Pending SME confirmation.*

### Gamification
Part of `cap-hydra-web-sdk`; no extra package. Opt-in: set **all three** `gamificationWriteKey`, `gamificationRegion` and `gamificationBaseUrl` in `initialize()` (step 2); with none of them, gamification is silently skipped and the rest of the SDK works normally. After every `identify()` the SDK fetches campaigns and entry points and renders them; everything is configured in the gamification dashboard, so no host code is needed except the inline hook / loyalty `<div>`s.

> ⚠️ Correction: ✅ Use all three `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` together (web-sdk-initialisation, gamification-web). ❌ Don't treat gamification as active with only the write key and region (Integration document p.65). *Pending SME confirmation.*

**Containers** (all set in the dashboard):

| Container | Behaviour | Host HTML |
|---|---|---|
| `ICON_BUTTON` | Fixed 160×160 px button sliding up from the bottom-left; opens a `CHAT_BOX` | No (appended to `document.body`) |
| `CHAT_BOX` | Fixed 360×580 px panel above the icon button | No |
| `POP_UP` | Centred full-page modal with backdrop; max 1000×740 px | No |
| `BOTTOM_SHEET` | Slides up from the bottom with a backdrop; height set in the dashboard | No |
| `EMBEDDED` | Full-width inline block in a hook `<div>` | **Yes** |
| `NATIVE_BANNER` | Block-level inline injection, same as `EMBEDDED` | **Yes** |

**Inline hooks and loyalty embeds:**

```html
<!-- NATIVE_BANNER: id = the hookId from the gamification dashboard / Capillary team -->
<div id="{{banner_id}}"></div>

<!-- EMBEDDED: id = the hookId from the gamification dashboard / Capillary team -->
<div id="{{embed_id}}"></div>

<!-- Loyalty embed: id = the embedId from the Capillary team; needs setCapToken (below) -->
<div id="{{loyalty_id}}"></div>
```

- `EMBEDDED` / `NATIVE_BANNER` hooks are SPA-safe: a `MutationObserver` waits for them, so they needn't exist at page load.
- Loyalty embeds: URLs come from the Campaigns API; at render time the SDK calls `document.getElementById(embedId)` and appends an `<iframe>`. **If the element isn't found, that embed is silently skipped**, so it must exist before or shortly after `identify()`.

> ⚠️ Gap: the 2024 guide (Integration document pp.60–71) says every inline component, loyalty included, renders once its `<div>` appears (SPA-safe); the current docs say only `EMBEDDED` / `NATIVE_BANNER` hooks are awaited by a `MutationObserver`, while a loyalty `<div>` must exist at render time or is silently skipped. Until confirmed, mount the loyalty `<div>` before or shortly after `identify()`. Ask a Capillary engineer.

**Capillary token (authenticated loyalty views).** After login, and again whenever your app refreshes the token:

```js
// After the user logs in and you have a fresh token
sdkService.setCapToken("short-lived-cap-token");

// Read back the current token if needed
const token = sdkService.getCapToken(); // string | null
```

The token is appended as `?capToken=<value>` to every loyalty iframe URL, persisted in IndexedDB (no need to set it on each load unless it expires), cleared on `reset()`, and each `setCapToken` re-renders all loyalty embeds at once.

**URL path rules.** Each entry point has include/exclude rules (dashboard, set by the Capillary team), evaluated against the current URL on every route change; SPA navigation is detected via `MutationObserver`.

| Format | Example | Matches |
|---|---|---|
| Every page | `*` or `/*` | Everything |
| Root only | `/` (or any all-slash rule, e.g. `//`) | Exact root path only, not "everything" |
| Path segment(s) | `product`, `dashboard/vouchers` | Those segments as a contiguous run anywhere in the path; no substring match (`product` ≠ `products`) |
| Segment(s) + wildcard | `product/*` | Same, requiring at least one further child segment |
| Exact URL | `https://example.com/cart` | Only that URL (query/hash stripped); **must include `http://` / `https://`** |
| URL wildcard | `https://example.com/cart/*` | That path and sub-paths, requiring a child segment (`/cart/*` doesn't match `/cartoons`) |
| Regex literal | `/\/cart$/i` | Any URL whose path matches |

If routing doesn't change the real URL (native-shell webview, custom router state), switch to manual tracking with `HydraSDK.enablePagePathTracking(false)` and call `HydraSDK.onScreenChanged(screenName)` on every navigation (add service wrappers for both).

**Content types** (dashboard only, no code): iframes `CAMPAIGN`, `WALLET`, `NUDGE`, `PROGRAM` (`{base}/program/?campaignId={id}`), `REWARD` (`{base}/reward/?rewardUserId={id}`); `STATIC` image with a click action; native `DYNAMIC` (progress circle), `DYNAMIC_MULTISTEP_1` (progress bar), `DYNAMIC_MULTISTEP_2` (multi-step meter with CTA), `DYNAMIC_MULTISTEP_3` (collapsible accordion with CTA), `ACCEPT_GUARD` (streak / enrolment modal before a campaign opens).

**Engagement events.** The SDK also sends `game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed` through the normal event pipeline; they will appear in your analytics backend.

**Suppression.** `HydraSDK.setGamificationSuppressed(true)` pauses automatic rendering of overlay containers (`POP_UP`, `BOTTOM_SHEET`, `CHAT_BOX`, `ICON_BUTTON`); `false` resumes. `EMBEDDED`, `NATIVE_BANNER`, loyalty embeds and explicit opens are unaffected. `isGamificationSuppressed()` returns the state (default `false`).

## Verification
Run all six checks before production (wrapper names from step 2):
1. **Init:** at `debugLevel: "NONE"` a successful init logs nothing. For verbose logs set `debugLevel: "DEBUG"` in `initialize()` temporarily; if nothing appears, enable the **Verbose** level in the DevTools Console filter.
2. **Page view:** `sdkService.trackPageView()` → an outbound POST to your `baseURL` in the Network tab.
3. **Custom event:** `sdkService.trackEvent("test_event", { source: "smoke_test" })` reaches the Capillary API.
4. **Identify:** `sdkService.identifyUser(...)` → the user profile is created or updated in your Capillary environment.
5. **Reset:** `sdkService.reset()` → user context cleared, later tracking anonymous.
6. **Consent:** `disableTracking()` then `enableTracking()` → events dropped while disabled; queued events resume.

Also: push → the service worker console shows `[FCM SW] Initialized`; gamification → overlay campaigns appear on matching pages after `identify()` and inline hooks fill; loyalty → `sdkService.getCapToken()` returns the token.

> ⚠️ Gap: no init-success callback, push-token check or test-push procedure is documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| `initialize()` throws a synchronous `Error` | `accountId`, `baseURL` or `orgId` missing | Add the field(s) to the `initialize()` call |
| SDK not initialising on app load | `initialize()` inside a lifecycle hook | Call `sdkService.initialize()` at module top level |
| Direct config ignored | `remoteConfigKey` / `firebaseConfig` passed (selects Remote Config bootstrap) | Remove them |
| Events not reaching the API | Wrong `baseURL` | Verify the value with Capillary |
| TypeScript import errors | Package types not resolved | Put `cap-hydra-web-sdk` in `dependencies`; refresh `node_modules` |
| `debugLevel: "DEBUG"` shows nothing extra | DevTools hides `console.debug()` under "Verbose" | Enable Verbose in the Console filter |
| Wrong `actionType` | `"USER_UPDATE"` at login | `"USER_REGISTER"` for login and sign-up |
| Re-identifying on every refresh | Unnecessary; context persists in IndexedDB | `identify()` only on login, sign-up, profile update |
| Events missing after consent revoked | Expected: new events dropped while disabled | Persist and restore consent on load |
| Push not working | Service worker not found, or wrong VAPID key | Match `serviceWorkerPath` to the file's real location; regenerate the VAPID key if needed |
| Service worker 404 / not registering | File not served at the expected path | Put `firebase-messaging-sw.js` in `public/` so it loads at `https://yourapp/firebase-messaging-sw.js`; check `serviceWorkerPath` (sub-path apps: P3 table) |
| `self.firebase is undefined` in the service worker console | `importScripts` failed, or `YOUR_*` placeholders not replaced | Allow network access to `gstatic.com` (CSP, step 9); replace all `YOUR_*` values |
| No notification shown at all | Code that reads the push body (`event.data.json()` / `text()` / `arrayBuffer()`) added to the worker's `push` listener; the body can be read only once, so Firebase's handler throws | Don't modify the worker logic |
| Notification body / title missing | Campaign sent fields in the `notification` payload | Send them as `data` fields |
| Notification icon missing | `/logo192.png` doesn't exist | Add it to `public/` or change the fallback paths |
| DLR events not recorded | Old service worker cached | DevTools → Application → Service Workers → Unregister, then reload |
| "Firebase App already exists" | The push Firebase app wasn't given its own name, so it collides with another Firebase app on the site (the SDK creates none in this mode) | Name it `"hydra-fcm"` (Modules → Push, P3) |
| Gamification entry points not appearing | One of `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` missing; user not identified; URL doesn't match path rules; overlays suppressed | Add all three (confirm values with Capillary); call `identify()`; check rules; `setGamificationSuppressed(false)` |
| Gamification never matches in a webview / custom router | No real URL change | Manual path tracking (`enablePagePathTracking(false)` + `onScreenChanged`) |
| Loyalty iframe not rendering | `<div id="{embedId}">` not in the DOM at render time, wrong `id`, or no token | Match the `embedId`; render the `<div>` before or shortly after `identify()`; `setCapToken` after login |
| SDK requests, iframes or workers blocked | Domains missing from the CSP | Add the step 9 entries |

**Rollback** (if the SDK causes production issues): 1) call `sdkService.disableTracking()` via a feature flag or emergency toggle; 2) remove the SDK service import from the app entry point; 3) uninstall:

```bash
npm uninstall cap-hydra-web-sdk
# or: yarn remove / pnpm remove / bun remove
```

4) if stale data is a concern, clear IndexedDB in affected browsers (DevTools → Application → IndexedDB); 5) send the error details to the Capillary team.

## API Reference
Call these through the service wrapper.

| Method | Purpose |
|---|---|
| `HydraSDK.initialize(config)` | Initialise the singleton, once at module load |
| `HydraSDK.track(eventName, properties?)` | Custom behavioural event |
| `HydraSDK.pageView(options?)` | Page view; `options`: `url?`, `title?`, `category?`, `properties?` (no args: current URL and title) |
| `HydraSDK.identify(params)` | `{ identifier: { type, cuid }, actionType, traits? }`; `USER_REGISTER` login / sign-up, `USER_UPDATE` profile changes |
| `HydraSDK.getAnonymousId()` | Backend-assigned anonymous visitor ID or `null`; any auth state |
| `HydraSDK.reset()` | Logout: back to anonymous; clears the Capillary token |
| `HydraSDK.enableSDK()` / `disableSDK()` | Re-enable tracking / disable it (new events dropped, queued kept in IndexedDB) |
| `HydraSDK.setCapToken(token)` / `getCapToken()` | Set the loyalty token (persisted, re-renders embeds) / read it (`string \| null`) |
| `HydraSDK.setGamificationSuppressed(value)` | `boolean`; suppress / resume overlay campaigns; returns `void` |
| `HydraSDK.isGamificationSuppressed()` | `boolean`, default `false` |
| `HydraSDK.enablePagePathTracking(enabled)` | `true` automatic path detection (default), `false` manual; returns `void` |
| `HydraSDK.onScreenChanged(screenName)` | `string`; report the screen in manual mode (no effect in automatic mode); returns `void` |

**`initialize()` fields (direct-config):**

| Field | Required | Default | Description |
|---|---|---|---|
| `accountId` | Yes | — | Organization account identifier (`string`) |
| `baseURL` | Yes | — | API base URL for all SDK requests (`string`) |
| `orgId` | Yes | — | Organization ID for API authentication (`string`) |
| `gamificationWriteKey` | For gamification | — | Write key, from Capillary |
| `gamificationRegion` | For gamification | — | Region code, e.g. `'us'`, `'me'`; derives the API base URL |
| `gamificationBaseUrl` | For gamification | — | Gamification API base URL for your region, from Capillary |
| `appVersion` | No | — | Host app version for event metadata |
| `retryDelays` | No | `[60000, 120000, 240000, 480000, 900000]` | Retry delays in ms (`number[]`) |
| `notifications` | Push only | — | `NotificationConfig`: `{ messaging, vapidKey, serviceWorkerPath }` |
| `brandId` | No | — | Brand identifier (namespaced database names) |
| `applicationId` | No | — | Application identifier (namespaced database names) |
| `source` | No | `WEBPUSH` | Source identifier for visitor profiles |
| `channelType` | No | `web` | Communication channel type |
| `sessionTimeoutMinutes` | No | `30` | Session inactivity timeout in minutes |
| `batchSize` | No | `50` | Max events per batch request |
| `debugLevel` | No | `NONE` | `NONE` / `ERROR` / `WARN` / `INFO` / `DEBUG` / `VERBOSE` |
| `firebaseConfig`, `remoteConfigKey` | Never here | — | Remote Config bootstrap only |

**`traits`** (all `string` unless noted): `firstName`, `lastName`, `gender`, `birthday`, `city`, `country`, `timezone`, `email`, `mobile`, `externalId`, `custom` (`Record<string, unknown>`: extra attributes, merged into events). The step 2 template's `traits` type omits `timezone`; add it if needed.

> ⚠️ Gap: not documented: who supplies `brandId` / `applicationId`; `birthday` / `timezone` formats and `gender` values. Ask a Capillary engineer.
