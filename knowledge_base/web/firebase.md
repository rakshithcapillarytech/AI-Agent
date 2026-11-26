---
platform: web
config_mode: firebase
sdk_package: cap-hydra-web-sdk
sdk_version: 1.10.6   # stated by web-sdk-getting-started (2026-11-17); the docs don't say if it is a minimum or just current, so install stays unpinned: `@latest` (default) or `@beta` (web-sdk-install). The 2024 gamification guide's minimum was 1.1.0-beta.20260619085241 via `@beta` (p.8)
modules_covered: [core, push, visitor, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, multi_account]
sources: ["Integration document _ Experience+ pp.7–12 (Gamification WebSDK Integration Guide)", "Integration document _ Experience+ pp.13–24 (Hydra WEB SDK Integration Runbook)", "Capillary developer docs (docs.capillarytech.com): web-sdk (2026-08-18); web-sdk-getting-started, web-sdk-install, web-sdk-initialisation, configure-firebase-web, push-notification-web, web-sdk-api-reference, web-sdk-troubleshooting, prerequisites (2026-11-17); gamification-web, web-sdk-ai-integration-guide (2026-11-23)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Web (with Firebase)

**Remote Config bootstrap** (the SDK's alternative to its default direct-config mode): the app passes its `firebaseConfig` and a `remoteConfigKey` to `HydraSDK.initialize()`, and the SDK fetches the Capillary values from a JSON in **Firebase Remote Config** at runtime, so SDK config changes need no redeploy. The SDK picks this mode because `remoteConfigKey` is present. Web push (optional) uses Firebase Cloud Messaging through a separate Firebase app you create.

## Coverage
| Module | Status |
|---|---|
| Core: Firebase setup, Remote Config JSON, install, service file, init, identify, profile update, reset, events, page views, consent, CSP | Documented |
| Push (Firebase Cloud Messaging) | Documented: your own Firebase Messaging instance, VAPID key, service-worker file, action buttons / CTAs, delivery receipts |
| Visitor | `getAnonymousId()` |
| Gamification: containers, content types, URL path rules, loyalty embeds, suppression, manual path tracking, theme, callbacks / deep links, game and CMS events | Documented |
| In-App, Inbox, Multi-account | Not documented for Web |

## Requirements
- `cap-hydra-web-sdk` (step 5), in `dependencies`. TypeScript or JavaScript.
- The client's own Firebase project with a web app and Remote Config (steps 1–4).
- Push only: the Firebase JS SDK (`firebase`) in your project; the Web SDK never installs or bundles Firebase.
- Browsers: the minimums below are the push-notification-web "Browser Support Matrix" (Push Notifications column: Supported). web-sdk-getting-started points to that matrix under "Browser support" for the SDK as a whole, and web-sdk-ai-integration-guide lists the same numbers as "Full support", so they may be the SDK's general minimums rather than push-only (unconfirmed; see the Gap below). Push also needs Service Worker and Push API support. **Internet Explorer is not supported.**
- SDK version: web-sdk-getting-started states `1.10.6` ("SDK version", 2026-11-17). Install stays unpinned (`@latest` default, or `@beta`; step 5).

| Browser | Minimum version (push) |
|---|---|
| Chrome | 109+ |
| Firefox | 140+ (ESR) |
| Safari | 26.3+ |
| Edge (Chromium) | 149+ |

> ⚠️ Gap: the Edge number looks inconsistent: Edge (Chromium) 149+ sits beside Chrome 109+ (same engine), which looks like a typo for 109, and Safari 26.3+ is also a very recent floor. The docs also don't say whether these minimums are push-only (only the push page labels them "Push Notifications: Supported"; the AI guide says "Full support"). Ask a Capillary engineer to confirm the Edge number and the scope.

> ⚠️ Correction: ✅ Use the browser matrix above (push-notification-web, web-sdk-ai-integration-guide). ❌ Don't use the 2024 table (Chrome 49+, Firefox 52+, Safari 10+ / 11.1+ for Service Worker, Edge 79+, IE 11 limited) (Integration document p.16). *Pending SME confirmation.*

> ⚠️ Gap: no Node.js / bundler / framework versions are stated; nor whether `firebase` must be installed for Remote Config without push, or which `firebase` version matches the SDK (the service worker loads Firebase `10.7.1` compat scripts and should stay "aligned with the SDK's expected Firebase version", which isn't given). Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` and `_shared/firebase-setup.md`.

- **Capillary values go in the Remote Config JSON (step 3), not in code:** `accountId`, `baseURL`, `orgId` (always); `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` (all three, for gamification).
- **Only if used:** each `hookId` for `EMBEDDED` / `NATIVE_BANNER` containers (gamification dashboard entry point settings, provided by the Capillary team); each loyalty `embedId` (Capillary team) and a Capillary short-lived token for the logged-in user (how to obtain it isn't documented; see `_shared/prerequisites.md`); URL path rules per entry point (dashboard, set by the Capillary team).
- **Client's own:** Firebase web config and Remote Config key (steps 1–3); VAPID key (push).

**Decide before writing code** (the official AI runbook asks these first; defaults in brackets): release channel [production]; push notifications?; gamification?; loyalty embeds (only if gamification)?; cookie consent / GDPR?; Firebase credentials ready?; bootstrap mode [direct-config is the SDK default; this file is Remote Config]. Generate only what the answers need, and state any default you assumed.

> ⚠️ Gap: the AI guide's first question calls the core SDK, including push notifications, "always included — this is not optional", yet its third question asks whether push is needed, and prerequisites / getting-started say Firebase is needed only for push or Remote Config. This guide treats push as optional. Ask a Capillary engineer if unsure.

> ⚠️ Correction: ✅ Use the current AI-assisted runbook (web-sdk-ai-integration-guide), summarised in this file. ❌ Don't use the 2024 Cursor runbook (Integration document pp.13–24): it has no `notifications.messaging`, no service-worker file, `getUser()` instead of `getAnonymousId()`, and an outdated browser table. *Pending SME confirmation.*

> ⚠️ Gap: not documented: what the client sends to register a web app, the full list of region values (docs show `'us'`, `'me'`), and whether the `identify()` identifier must match the CRM Account Linking Identifier. Ask a Capillary engineer.

> ⚠️ Gap: the Web docs' `baseURL` example is `https://api.example.capillarytech.com`; they don't say whether Web uses the same cluster hosts as the mobile platforms (`_shared/prerequisites.md`). Use the Base URL Capillary confirms for the org.

## Steps
Steps 1–4 are first-time Firebase setup (skip what exists); 5–8 add the SDK. (The public roadmap lists install and initialise before Firebase; this guide does Firebase first because step 6 needs its values.)

### 1. Create a Firebase project
Go to <https://console.firebase.google.com/> → "Add project" → enter a project name (e.g. `my-app-analytics`) → enable Google Analytics if desired (recommended) → "Create project".

### 2. Register a web app and copy its Firebase config
In the project dashboard click the Web icon (`</>`) → enter an app nickname (e.g. `My Web App`) → optionally check "Also set up Firebase Hosting" → "Register app". Copy the config object; you need every value (step 6, and the service worker for push):

```js
const firebaseConfig = {
  apiKey: "AIzaSyC...",
  authDomain: "my-project.firebaseapp.com",
  databaseURL: "https://my-project-default-rtdb.firebaseio.com",
  projectId: "my-project",
  storageBucket: "my-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX", // only if Analytics is enabled
};
```

### 3. Store the Hydra config in Remote Config
1. Left sidebar → **Remote Config** → "Create configuration" → "Add parameter".
2. **Parameter key**: a name of your choice (e.g. `hydra_sdk_config`); this is `remoteConfigKey` in step 6.
3. **Default value**: this JSON. `accountId`, `baseURL`, `orgId` are required; drop the three `gamification*` fields together if not using gamification; other fields are optional and default if omitted (API Reference; `brandId` / `applicationId` values are examples).

```json
{
  "accountId": "{{account_id}}",
  "baseURL": "{{base_url}}",
  "orgId": "{{org_id}}",
  "brandId": "1",
  "applicationId": "2",
  "source": "WEBPUSH",
  "channelType": "web",
  "sessionTimeoutMinutes": 30,
  "batchSize": 50,
  "debugLevel": "NONE",
  "gamificationWriteKey": "{{gamification_key}}",
  "gamificationRegion": "{{gamification_region}}",
  "gamificationBaseUrl": "{{gamification_base_url}}"
}
```

4. "Save" → **"Publish changes"**. Republish after every edit.

If `accountId`, `baseURL` or `orgId` is missing, `HydraSDK.initialize()` **fails silently** in this mode (the fetch error is only logged). Never set these fields in `initialize()`.

### 4. Confirm the parameter is published
Remote Config: confirm your parameter is published.

> ⚠️ Gap: the 2024 runbook also had you check Cloud Messaging and, if the config uses `databaseURL`, create a Realtime Database (region, security rules; test mode for development) (Integration document pp.14–15); configure-firebase-web now lists only Remote Config. Ask a Capillary engineer whether those are still needed.

### 5. Install the SDK
Use the lock file in the project root to pick the package manager (none → npm).

| Lock file | Production (`@latest`, default) | Beta (`@beta`: pre-release testing, latest features before the next stable cut) |
|---|---|---|
| `package-lock.json` / none | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |
| `yarn.lock` | `yarn add cap-hydra-web-sdk` | `yarn add cap-hydra-web-sdk@beta` |
| `pnpm-lock.yaml` | `pnpm add cap-hydra-web-sdk` | `pnpm add cap-hydra-web-sdk@beta` |
| `bun.lockb` | `bun add cap-hydra-web-sdk` | `bun add cap-hydra-web-sdk@beta` |

For push, also install `firebase`.

### 6. Create the SDK service file and initialise at module load
One service file wraps every SDK call; follow the app's own file naming, folder and export conventions (`.js` if not using TypeScript). Include only the methods for features the app uses. Replace the `MY_*` values with your Firebase values (steps 2–3; the table after the rules says where each comes from). Add the `firebase/*` imports, the `initializeApp(...)` lines and the `notifications` block **only for push** (Modules → Push); otherwise delete them. Keep the `Theme` / `GamificationCallback` import and the gamification wrappers at the end of the class only for gamification (Modules → Gamification).

```ts file=src/services/sdkService.ts
import { HydraSDK } from "cap-hydra-web-sdk";
// Only needed if using gamification:
import { GamificationCallback, Theme } from "cap-hydra-web-sdk";
// Only needed if push notifications are required:
import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";

class SDKService {
  initialize() {
    try {
      // Only needed if push notifications are required — this is a SEPARATE app instance from
      // whatever the SDK uses internally for Remote Config, even though it's the same project's
      // credentials; giving it its own name avoids a "Firebase App already exists" collision:
      // const firebaseApp = initializeApp(
      //   { apiKey: "MY_FIREBASE_API_KEY", /* ...rest of Firebase config, same project as below */ },
      //   "hydra-fcm",
      // );

      HydraSDK.initialize({
        firebaseConfig: {
          apiKey: "MY_FIREBASE_API_KEY",
          authDomain: "MY_PROJECT_ID.firebaseapp.com",
          databaseURL: "https://MY_PROJECT_ID-default-rtdb.firebaseio.com",
          projectId: "MY_PROJECT_ID",
          storageBucket: "MY_PROJECT_ID.appspot.com",
          messagingSenderId: "MY_SENDER_ID",
          appId: "MY_APP_ID",
          measurementId: "MY_MEASUREMENT_ID", // optional
        },
        remoteConfigKey: "MY_REMOTE_CONFIG_KEY",
        appVersion: "1.0.0", // my app's version string
        // Only include this block if push notifications are needed:
        // notifications: {
        //   messaging: getMessaging(firebaseApp),
        //   vapidKey: "MY_VAPID_KEY",
        //   serviceWorkerPath: "/firebase-messaging-sw.js", // adjust if app is at a subpath
        // },
      });
    } catch (error) {
      console.error("Failed to initialize SDK:", error);
    }
  }

  // --- Page Views ---
  trackPageView(options?: {
    page_url?: string;
    page_title?: string;
    referrer?: string;
    page_category?: string;
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

  // --- Gamification (only if using gamification) ---
  // The SDK saves the theme and suppression state itself, but restores them only after its
  // async initialization finishes, and has no theme getter. A copy in localStorage lets your
  // UI (theme picker, suppression toggle) show the correct value immediately on page load.
  private readonly THEME_KEY = "hydra_gamification_theme";
  private readonly SUPPRESSED_KEY = "hydra_gamification_suppressed";

  setTheme(theme: Theme) {
    HydraSDK.setTheme(theme);
    this.saveSetting(this.THEME_KEY, theme);
  }

  getSavedTheme(): Theme {
    const saved = this.readSetting(this.THEME_KEY);
    return saved === "AUTO" || saved === "DARK" || saved === "LIGHT"
      ? saved
      : "NONE";
  }

  setGamificationSuppressed(value: boolean) {
    HydraSDK.setGamificationSuppressed(value);
    this.saveSetting(this.SUPPRESSED_KEY, String(value));
  }

  getSavedGamificationSuppressed(): boolean {
    return this.readSetting(this.SUPPRESSED_KEY) === "true";
  }

  setGamificationCallback(callback: GamificationCallback | null) {
    HydraSDK.setGamificationCallback(callback);
  }

  private saveSetting(key: string, value: string) {
    try {
      localStorage.setItem(key, value);
    } catch {
      // localStorage unavailable — the SDK still keeps its own copy
    }
  }

  private readSetting(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }
}

export const sdkService = new SDKService();

// IMPORTANT: Initialize at module load — NOT inside useEffect, ngOnInit, or similar hooks
sdkService.initialize();
```

**Rules to enforce:**
- Call `HydraSDK.initialize()` at module load time (top level of the file), **never** inside React `useEffect`, Angular `ngOnInit`, `mounted()` or any async lifecycle hook. Import the service file from the app entry point.
- `initialize()` is safe to call more than once; later calls return the existing instance.
- Components **never** import `HydraSDK` directly; every call goes through the service.
- Don't `await` SDK calls (all are fire-and-forget) and don't add `isInitialized()` guards: the SDK queues calls internally until ready.
- **Don't re-identify the user on page refresh**; the SDK persists user context in IndexedDB.
- Capillary and gamification fields come only from Remote Config; don't pass them to `initialize()`.
- When an AI assistant runs this integration it implements only install, this service file and (push) the service worker; it leaves `MY_*` / `YOUR_*` placeholders it has no values for, reminds the developer to replace them, and gives the Firebase setup (steps 1–4, VAPID key) as a checklist without creating anything. Wiring calls into the app flow (step 7) is the developer's choice.

**Where each placeholder value comes from** (web-sdk-initialisation, "Replacing placeholders"):

| Placeholder | Where to get it |
|---|---|
| `accountId`, `baseURL`, `orgId` values | Provided by the Capillary team |
| `MY_FIREBASE_API_KEY` / `YOUR_API_KEY_HERE` | Firebase Console → Project Settings → General |
| `MY_PROJECT_ID` / `YOUR_PROJECT_ID` | Firebase Console → Project Settings → General |
| `MY_SENDER_ID` / `YOUR_SENDER_ID` | Firebase Console → Project Settings → Cloud Messaging |
| `MY_APP_ID` / `YOUR_APP_ID` | Firebase Console → Project Settings → General |
| `MY_MEASUREMENT_ID` / `YOUR_MEASUREMENT_ID` | Firebase Console → Project Settings → General (optional) |
| `MY_REMOTE_CONFIG_KEY` | The parameter key you created in Firebase Remote Config (Remote Config bootstrap only) |
| `MY_VAPID_KEY` | Firebase Console → Project Settings → Cloud Messaging → Web Push certificates (push only) |

When push is enabled, the service worker and the SDK service file use the **same** Firebase credentials: fill them in identically in both places.

### 7. Call the service from the app
| When | Call | Notes |
|---|---|---|
| Every route change | `sdkService.trackPageView()` | No args: current URL and title; or pass `{ page_url, page_title, referrer, page_category, properties }` to override (`referrer` overrides the page referrer; `page_category` e.g. `'blog'`, `'product'`, `'checkout'`) |
| Custom event | `sdkService.trackEvent(name, properties?)` | e.g. `sdkService.trackEvent("test_event", { source: "smoke_test" })`; with gamification, an event name can also open a campaign (`ACTION_EVENT`; Modules → Gamification) |
| Login **and** sign-up | `sdkService.identifyUser(type, cuid, "USER_REGISTER", traits?)` | `type`: `"email"`, `"mobile"`, `"externalId"`; `cuid` = the user's value for it |
| Profile update only | `sdkService.identifyUser(type, cuid, "USER_UPDATE", traits?)` | Never at login |
| Logout | `sdkService.reset()` | Back to anonymous; clears the Capillary token |
| Consent granted / revoked | `sdkService.enableTracking()` / `disableTracking()` | While disabled, new `track()` / `pageView()` events are dropped; queued ones stay in IndexedDB and are sent on re-enable. `disableSDK()` does not affect `identify()`, `reset()` or gamification events. Persist the decision yourself and restore it on app load |
| After login / token refresh (loyalty) | `sdkService.setCapToken(token)` | Modules → Gamification |

```js
sdkService.identifyUser("email", "testuser@example.com", "USER_REGISTER", {
  firstName: "Test",
  lastName: "User",
});
```

> ⚠️ Gap: because `disableSDK()` leaves `identify()`, `reset()` and gamification events running, the docs don't say how to fully opt a user out. Ask a Capillary engineer if your consent rules need more than this.

### 8. Allowlist the SDK's domains in the CSP (if the site has one)
**Add these to the existing directives; don't replace them.**

| Directive | Entries |
|---|---|
| `connect-src` | `https://*.capillarytech.com` (core API, gamification, loyalty; always); `https://*.googleapis.com`, `https://*.firebaseio.com`, `https://*.firebaseapp.com` (Remote Config bootstrap and/or push: always in this mode); `https://*.posthog.com` (SDK diagnostics; always) |
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

> ⚠️ Gap: the docs' example `gamificationBaseUrl` is on `customerglu.com` (`https://api-us.customerglu.com`), which isn't in the `connect-src` allowlist. The docs also describe `gamificationRegion` as deriving the API base URL automatically while still marking `gamificationBaseUrl` required, and describe the `capillarytech.com` entry as covering gamification traffic. Ask a Capillary engineer whether gamification needs that domain allowlisted and what `gamificationBaseUrl` should be.

## Modules

### Push
Optional. The SDK never calls Firebase's `initializeApp()` / `getMessaging()` itself: you create a **separately named** Firebase app (same project credentials) and Messaging instance and pass it as `notifications.messaging`. Omitting `notifications` disables push with no compile-time or runtime error.

**P1. VAPID key:** Firebase Console → **Project Settings → Cloud Messaging → Web configuration → Web Push certificates → "Generate key pair"** → copy it (→ `notifications.vapidKey`).

**P2. Install** `firebase` (step 5).

**P3. Pass the Messaging instance** in the step 6 service file: uncomment the `initializeApp(...)` lines with your full Firebase config, named `"hydra-fcm"`, and the `notifications` block:

```ts
notifications: {
  messaging: getMessaging(firebaseApp),
  vapidKey: "MY_VAPID_KEY",
  serviceWorkerPath: "/firebase-messaging-sw.js",
},
```

| App served at | `serviceWorkerPath` |
|---|---|
| `https://example.com/` | `"/firebase-messaging-sw.js"` |
| `https://example.com/my-app/` | `"/my-app/firebase-messaging-sw.js"` |

> ⚠️ Correction: ✅ Use `notifications: { messaging: getMessaging(firebaseApp), vapidKey, serviceWorkerPath }` with your own Firebase app named `"hydra-fcm"` (push-notification-web, web-sdk-initialisation). ❌ Don't use a `notifications` block with only `vapidKey` and `serviceWorkerPath` (Integration document runbook pp.13–24). *Pending SME confirmation.*

**P4. Create the service worker.** It handles background (data-only) pushes, action buttons, CTAs and delivery receipts (DLR).
- Create `firebase-messaging-sw.js` in `public/` (or the static-asset directory served at the site root, e.g. `static/`, `assets/` or the bundler's public path). Vite, CRA and Next.js serve `public/` at the site root. It must be reachable at the app's root scope.
- **Don't rename the file. Don't change its logic**; replace only the `YOUR_*` values in the Firebase config block, with the same values as the service file. (An AI assistant leaves the `YOUR_*` placeholders for the developer.)
- Notification `title`, `body`, `icon` etc. are read from the push **`data`** payload, not `notification`: Capillary campaigns must send them as data fields.
- Icon and badge fall back to `/logo192.png`: add it to `public/` or change the fallback paths.
- Receipts (`received`, `clicked`, `dismissed`) go to IndexedDB store `WebSDK_DLR_SW` and the app is notified by `postMessage`; the SDK processes them automatically.
- Clicks resolve in order: an action that is itself a URL (`https://...`) opens directly; else the action is looked up in the payload's `ctas` (`[{ action, actionLink }]`); else the default click URL (`data.redirectUrl` / `data.link` / `data.url`). Buttons and CTAs are configured on the push campaign in the dashboard.
- Lifecycle: the worker installs without `skipWaiting` and activates without `clients.claim` (no extra OS "updated in background" notices), so a new version takes over on the next load. To apply it at once, the app can post `{ type: "SKIP_WAITING" }` to the worker, which then calls `skipWaiting()`.
- A push that arrives with no `data` payload logs a warning and is shown with defaults (title "New Notification", empty body). The raw `push` listener only logs; leave it as is. The IndexedDB open has an `onblocked` handler, and receipt tracking never blocks showing the notification (3 s timeout).

The **full file**, verbatim from push-notification-web ("Service Worker File", 2026-11-17). web-sdk-ai-integration-guide ("Service Worker File", 2026-11-23) carries a byte-identical copy (here the two warning emoji in the "REPLACE WITH YOUR FIREBASE CONFIGURATION" comment are dropped; nothing else differs). Replace only the `YOUR_*` values in the Firebase config block:

```js file=public/firebase-messaging-sw.js
// firebase-messaging-sw.js

/**
 * Firebase Cloud Messaging Service Worker
 * - Handles background push notifications
 * - Supports:
 *    - Data-only messages
 *    - Action buttons (URL or ID-based)
 *    - CTAs mapping action -> URL
 *
 * SETUP INSTRUCTIONS:
 * 1. Copy this file to your public directory as 'firebase-messaging-sw.js'
 * 2. Replace the placeholder Firebase configuration below with your actual credentials
 */

importScripts(
  "https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js",
);
importScripts(
  "https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js",
);

// --------------------------------------------------
// REPLACE WITH YOUR FIREBASE CONFIGURATION
// --------------------------------------------------
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

// --------------------------------------------------
// Small helper: never let a promise hang the pipeline forever.
// Wrap any non-essential async work (analytics, IndexedDB, etc.) in this so
// it can delay, but never block, the actual notification display.
// --------------------------------------------------
const DLR_TIMEOUT_MS = 3000;

function withTimeout(promise, ms, label) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`[FCM SW] "${label}" timed out after ${ms}ms`));
    }, ms);

    promise.then(
      (value) => {
        clearTimeout(timer);
        resolve(value);
      },
      (err) => {
        clearTimeout(timer);
        reject(err);
      },
    );
  });
}

// --------------------------------------------------
// DLR (Delivery Receipt) IndexedDB Helper
// Stores DLR events for the main app to process
// --------------------------------------------------
const DLR_DB_NAME = "WebSDK_DLR_SW";
const DLR_DB_VERSION = 1;
const DLR_STORE_NAME = "pending_dlr_events";

function openDLRDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DLR_DB_NAME, DLR_DB_VERSION);

    request.onerror = () => {
      console.error("[FCM SW] Failed to open DLR database:", request.error);
      reject(request.error);
    };

    request.onblocked = () => {
      console.warn("[FCM SW] DLR database open blocked by another connection");
      reject(new Error("IndexedDB open blocked by another connection"));
    };

    request.onsuccess = () => {
      resolve(request.result);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(DLR_STORE_NAME)) {
        const store = db.createObjectStore(DLR_STORE_NAME, {
          keyPath: "id",
          autoIncrement: true,
        });
        store.createIndex("timestamp", "timestamp", { unique: false });
        store.createIndex("type", "type", { unique: false });
        console.log("[FCM SW] DLR database store created");
      }
    };
  });
}

async function storeDLREvent(type, data) {
  const db = await openDLRDatabase();

  const dlrEvent = {
    type: type,
    messageId: data.messageId || "",
    scope: data.scope || "",
    campaignId: data.campaignId || "",
    variationId: data.variationId || "",
    senderId: data.senderId || "",
    cuid: data.cuid || "",
    accountId: data.accountId || "",
    timestamp: new Date().toISOString(),
  };

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([DLR_STORE_NAME], "readwrite");
    const store = transaction.objectStore(DLR_STORE_NAME);
    const request = store.add(dlrEvent);

    request.onerror = () => {
      console.error("[FCM SW] Failed to store DLR event:", request.error);
      db.close();
      reject(request.error);
    };

    request.onsuccess = () => {
      console.log("[FCM SW] DLR event stored:", type, dlrEvent.messageId);
      db.close();
      resolve();
    };
  });
}

async function notifyMainAppOfDLREvents(dlrEventType, dlrData) {
  const allClients = await clients.matchAll({
    type: "window",
    includeUncontrolled: true,
  });

  if (allClients.length === 0) {
    console.log(
      "[FCM SW] No open clients to notify of DLR event:",
      dlrEventType,
    );
    return;
  }

  for (const client of allClients) {
    client.postMessage({
      type: "HYDRA_DLR_EVENTS_PENDING",
      timestamp: new Date().toISOString(),
      dlrEventType,
      messageId: dlrData && dlrData.messageId,
      campaignId: dlrData && dlrData.campaignId,
    });
  }
}

function trackDLREvent(type, dlrData) {
  return withTimeout(
    storeDLREvent(type, dlrData).then(() =>
      notifyMainAppOfDLREvents(type, dlrData),
    ),
    DLR_TIMEOUT_MS,
    `DLR:${type}`,
  ).catch((error) => {
    console.error(
      "[FCM SW] DLR tracking failed or timed out (non-fatal):",
      error,
    );
  });
}

// --------------------------------------------------
// Raw push event visibility — messaging.onBackgroundMessage() below wraps this, but a payload
// that fails inside Firebase's own internal handling never reaches onBackgroundMessage at all.
// This listener only logs; it never calls preventDefault/respondWith/stopPropagation, so it
// cannot interfere with Firebase's own 'push' listener processing the same event.
//
// NOTE: never call event.data.json()/text()/arrayBuffer() here. PushMessageData's body can
// only be consumed once; if this listener reads it, Firebase's own internal push listener
// (which also needs to read it) will throw, and no notification will be shown at all.
// --------------------------------------------------
self.addEventListener("push", (event) => {
  console.log("[FCM SW] Raw push event received", {
    hasData: !!event.data,
  });
});

// --------------------------------------------------
// Handle background messages (tab closed / in bg)
// --------------------------------------------------
messaging.onBackgroundMessage((payload) => {
  console.log("[FCM SW] ===== BACKGROUND MESSAGE =====");
  console.log("[FCM SW] Raw payload:", JSON.stringify(payload, null, 2));

  if (!payload.data) {
    console.warn(
      "[FCM SW] Background message has no data payload, using defaults for everything",
    );
  }
  const data = payload.data || {};

  // Notification UI fields (we trust data only)
  const title = data.title || "New Notification";
  const body = data.body || "";
  const icon = data.icon || "/logo192.png";
  const image = data.image;
  const badge = data.badge || "/logo192.png";
  const tag = data.tag || `hydra-${payload.fcmMessageId || Date.now()}`;

  // Where to go on normal click (no action button)
  const clickUrl =
    data.redirectUrl || // preferred
    data.link ||
    data.url ||
    "/";

  console.log("[FCM SW] Base click URL:", clickUrl);

  // Parse CTAs: [{ action, actionLink }]
  let ctaActions = [];
  if (data.ctas) {
    try {
      ctaActions =
        typeof data.ctas === "string" ? JSON.parse(data.ctas) : data.ctas;
      console.log("[FCM SW] Parsed CTAs:", ctaActions);
    } catch (e) {
      console.error("[FCM SW] Failed to parse CTAs:", e);
    }
  }

  // Parse actions for notification buttons
  // examples:
  // 1) [{ action: "https://www.zoho.com/", title: "Zoho" }]
  // 2) [{ action: "action_1", title: "Alpha" }]
  let actions = [];
  if (data.actions) {
    try {
      actions =
        typeof data.actions === "string"
          ? JSON.parse(data.actions)
          : data.actions;
      console.log("[FCM SW] Parsed actions:", actions);
    } catch (e) {
      console.error("[FCM SW] Failed to parse actions:", e);
    }
  }

  const notificationOptions = {
    body,
    icon,
    image,
    badge,
    tag,
    renotify: false,
    vibrate: [200, 100, 200],
    data: {
      clickUrl,
      ctaActions,
      actions,
      scope: data.scope,
      campaignId: data.campaignId,
      variationId: data.variationId,
      senderId: data.senderId,
      cuid: data.cuid,
      accountId: data.accountId,
      originalData: data,
    },
  };

  if (actions.length > 0) {
    notificationOptions.actions = actions.map((a) => ({
      action: a.action,
      title: a.title,
      icon: a.icon, // optional, often undefined
    }));
    console.log(
      "[FCM SW] Actions set on notification:",
      notificationOptions.actions,
    );
  }

  console.log("[FCM SW] Showing notification:", title);

  // Track DLR: notification received
  const dlrData = {
    messageId: tag,
    scope: data.scope,
    campaignId: data.campaignId,
    variationId: data.variationId,
    senderId: data.senderId,
    cuid: data.cuid,
    accountId: data.accountId,
  };

  const notificationPromise = self.registration
    .showNotification(title, notificationOptions)
    .catch((error) => {
      console.error("[FCM SW] showNotification failed:", error);
    });

  const trackingPromise = trackDLREvent("received", dlrData);

  return Promise.allSettled([notificationPromise, trackingPromise]);
});

// --------------------------------------------------
// Handle notification click
// --------------------------------------------------
self.addEventListener("notificationclick", (event) => {
  console.log("[FCM SW] ===== NOTIFICATION CLICK =====");

  const notification = event.notification;
  const action = event.action; // empty string when body clicked
  const data = notification.data || {};

  notification.close();

  console.log("[FCM SW] Action clicked:", action || "(main body)");

  let urlToOpen = data.clickUrl || "/";
  const ctaActions = data.ctaActions || [];

  // 1️⃣ If the action *itself* is a URL ⇒ open directly
  if (action && /^https?:\/\//i.test(action)) {
    console.log("[FCM SW] Action is URL, opening directly:", action);
    urlToOpen = action;
  }
  // 2️⃣ Else, try to resolve via CTAs
  else if (action && ctaActions.length > 0) {
    const matchedCta = ctaActions.find((cta) => cta.action === action);
    if (matchedCta && matchedCta.actionLink) {
      console.log("[FCM SW] Matched CTA actionLink:", matchedCta.actionLink);
      urlToOpen = matchedCta.actionLink;
    } else {
      console.log("[FCM SW] No CTA match, using default clickUrl:", urlToOpen);
    }
  }
  // 3️⃣ Else (no action button or no match) → use default clickUrl
  else {
    console.log("[FCM SW] Using default clickUrl:", urlToOpen);
  }

  // Ensure URL is absolute
  try {
    if (!/^https?:\/\//i.test(urlToOpen)) {
      urlToOpen = new URL(urlToOpen, self.location.origin).href;
    }
  } catch (e) {
    console.error(
      "[FCM SW] Invalid URL, falling back to origin:",
      urlToOpen,
      e,
    );
    urlToOpen = self.location.origin;
  }

  console.log("[FCM SW] Opening URL:", urlToOpen);

  // Track DLR: notification clicked
  const dlrData = {
    messageId: notification.tag || "",
    scope: data.scope,
    campaignId: data.campaignId,
    variationId: data.variationId,
    senderId: data.senderId,
    cuid: data.cuid,
    accountId: data.accountId,
  };

  const openPromise = clients
    .openWindow(urlToOpen)
    .then((client) => {
      if (client) {
        console.log("[FCM SW] Window opened");
      } else {
        console.warn("[FCM SW] Window did not open");
      }
    })
    .catch((error) => {
      console.error("[FCM SW] Error opening window:", error);
    });

  const trackingPromise = trackDLREvent("clicked", dlrData);

  event.waitUntil(Promise.allSettled([openPromise, trackingPromise]));
});

// --------------------------------------------------
// Handle notification close (dismiss)
// --------------------------------------------------
self.addEventListener("notificationclose", (event) => {
  const notification = event.notification;
  const data = notification.data || {};

  console.log("[FCM SW] Notification dismissed");
  console.log("[FCM SW]   - Campaign ID:", data.campaignId || "N/A");
  console.log("[FCM SW]   - Tag:", notification.tag);

  // Track DLR: notification dismissed
  const dlrData = {
    messageId: notification.tag || "",
    scope: data.scope,
    campaignId: data.campaignId,
    variationId: data.variationId,
    senderId: data.senderId,
    cuid: data.cuid,
    accountId: data.accountId,
  };

  event.waitUntil(trackDLREvent("dismissed", dlrData));
});

// --------------------------------------------------
// Service worker lifecycle
// --------------------------------------------------
self.addEventListener("install", (_event) => {
  console.log("[FCM SW] Installing...");
  // No skipWaiting: let it activate normally on next load
});

self.addEventListener("activate", (_event) => {
  console.log("[FCM SW] Activating...");
  // No clients.claim: avoid extra OS "updated in background" noise
});

// --------------------------------------------------
// Messages from main app (optional)
// --------------------------------------------------
self.addEventListener("message", (event) => {
  console.log("[FCM SW] Message from app:", event.data);
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting().catch((error) => {
      console.error("[FCM SW] skipWaiting() failed:", error);
    });
  }
});
```

> ⚠️ Correction: ✅ Use the `firebase-messaging-sw.js` published in push-notification-web. ❌ Don't wait for a template from the Capillary team (Integration document pp.14–15). *Pending SME confirmation.*

> ⚠️ Gap: not documented: the browser permission prompt (who triggers it and when), foreground message handling, how to send a test push, and any iOS / iPadOS Safari web-push requirements. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Visitor
Tracking is anonymous before `identify()` and after `reset()`; `source` defaults to `WEBPUSH`. `sdkService.getAnonymousId()` returns the backend-assigned anonymous visitor ID (`string | null`), safe at any time regardless of auth state.

> ⚠️ Correction: ✅ Use `HydraSDK.getAnonymousId()` for the visitor ID (web-sdk-api-reference lists every public method; `getUser()` isn't one). ❌ Don't use `HydraSDK.getUser()` (Integration document runbook pp.13–24). *Pending SME confirmation.*

### Gamification
Part of `cap-hydra-web-sdk`; no extra package. Opt-in: put **all three** `gamificationWriteKey`, `gamificationRegion` and `gamificationBaseUrl` in the Remote Config JSON (step 3) and **republish**; never in `initialize()`. With none of them, gamification is silently skipped and the rest of the SDK works normally. After every `identify()` the SDK fetches campaigns and entry points and renders them; everything is configured in the gamification dashboard, so no host code is needed except the inline hook / loyalty `<div>`s; theme, callbacks and deep links below are optional.

> ⚠️ Correction: ✅ Use all three `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` together (web-sdk-initialisation, configure-firebase-web, gamification-web). ❌ Don't treat `gamificationBaseUrl` as optional (Integration document p.9). *Pending SME confirmation.*

> ⚠️ Gap: the 2024 gamification guide required `cap-hydra-web-sdk` 1.1.0-beta.20260619085241 or later via `@beta` (p.8). web-sdk-getting-started now states SDK version `1.10.6` but doesn't say whether that is a minimum or just the current release, and gamification-web names no minimum version or channel. `@latest` is higher than the old minimum. Ask a Capillary engineer.

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

> ⚠️ Gap: the 2024 guide (Integration document pp.7–12) says every inline component, loyalty included, renders once its `<div>` appears (SPA-safe); the current docs say only `EMBEDDED` / `NATIVE_BANNER` hooks are awaited by a `MutationObserver`, while a loyalty `<div>` must exist at render time or is silently skipped. Until confirmed, mount the loyalty `<div>` before or shortly after `identify()`. Ask a Capillary engineer.

**Capillary token (authenticated loyalty views).** After login, and again whenever your app refreshes the token:

```js
// After the user logs in and you have a fresh token
sdkService.setCapToken("short-lived-cap-token");

// Read back the current token if needed
const token = sdkService.getCapToken(); // string | null
```

The token is appended as `?capToken=<value>` to every loyalty iframe URL, persisted in IndexedDB (no need to set it on each load unless it expires), cleared on `reset()`, and each `setCapToken` re-renders all loyalty embeds at once.

**URL path rules.** Each entry point has include/exclude rules (dashboard, set by the Capillary team), evaluated against the current URL on every route change; SPA navigation is detected via `MutationObserver` (16 ms debounce, per the 2024 guide).

| Format | Example | Matches |
|---|---|---|
| Every page | `*` or `/*` | Everything |
| Root only | `/` (or any all-slash rule, e.g. `//`) | Exact root path only, not "everything" |
| Path segment(s) | `product`, `dashboard/vouchers` | Those segments as a contiguous run anywhere in the path or SPA hash route (hash handling unconfirmed, see the Gap below); no substring match (`product` ≠ `products`) |
| Segment(s) + wildcard | `product/*` | Same, requiring at least one further child segment |
| Exact URL | `https://example.com/cart` | Only that URL (query/hash stripped); **must include `http://` / `https://`** |
| URL wildcard | `https://example.com/cart/*` | That path and sub-paths, requiring a child segment (`/cart/*` doesn't match `/cartoons`) |
| Regex literal | `/\/cart$/i` | Any URL whose path matches |

If routing doesn't change the real URL (native-shell webview, custom router state), switch to manual tracking with `HydraSDK.enablePagePathTracking(false)` and call `HydraSDK.onScreenChanged(screenName)` on every navigation (add service wrappers for both).

> ⚠️ Gap: gamification-web says path-segment rules match "anywhere in the path or SPA hash route (see below)", but nothing follows to explain how hash routes are matched. Ask a Capillary engineer before relying on hash-route rules.

**Content types** (dashboard only, no code): iframes `CAMPAIGN`, `WALLET`, `NUDGE`, `PROGRAM` (`{base}/program/?campaignId={id}`), `REWARD` (`{base}/reward/?rewardUserId={id}`); `STATIC` image with a click action; native `DYNAMIC` (progress circle), `DYNAMIC_MULTISTEP_1` (progress bar), `DYNAMIC_MULTISTEP_2` (multi-step meter with CTA), `DYNAMIC_MULTISTEP_3` (collapsible accordion with CTA), `ACCEPT_GUARD` (streak / enrolment modal before a campaign opens).

**Events can open campaigns.** An `ACTION_EVENT` entry point (set up in the dashboard) opens from a `track()` call, so an event name passed to `sdkService.trackEvent()` can open a campaign. When `track()` fires an event that has no `ACTION_EVENT` entry point configured, the `onGameEventTrigger` hook is called (Callbacks, below).

**Theme.** `HydraSDK.setTheme(theme)` (service wrapper `sdkService.setTheme`) takes a `Theme` (import the type from `cap-hydra-web-sdk`). It appends `darkMode=true` or `darkMode=false` to every campaign and loyalty embed URL loaded after the call, so the hosted content can theme itself; a campaign already on screen keeps its look.

| Value | Behaviour |
|---|---|
| `NONE` | Default. No theme: `darkMode` is omitted from URLs and everything renders as before |
| `LIGHT` | Forces light mode (`darkMode=false`) |
| `DARK` | Forces dark mode (`darkMode=true`) |
| `AUTO` | Follows the browser's `prefers-color-scheme`, checked each time something renders; a system change applies to the next campaign opened, not one already on screen |

Call `sdkService.setTheme()` from your app's own theme toggle (light → `LIGHT`, dark → `DARK`, system → `AUTO`); if the app has no dark mode, skip it. The SDK saves the choice and restores it after a reload only once its async initialisation finishes, and it has no theme getter, so the service file keeps a localStorage copy (`hydra_gamification_theme`, read with `getSavedTheme()`). Seed a theme picker from that copy; if no UI shows the value, the copy is optional.

**Suppression.** `HydraSDK.setGamificationSuppressed(true)` (wrapper `sdkService.setGamificationSuppressed`) affects overlay containers only (`POP_UP`, `BOTTOM_SHEET`, `CHAT_BOX`, `ICON_BUTTON`); `false` resumes. While suppressed, an overlay never opens, whatever the trigger: a screen / path match, an `ACTION_EVENT` trigger from `track()`, or a click inside a banner, embed or loyalty embed that would open an overlay. `EMBEDDED`, `NATIVE_BANNER` and loyalty embeds keep rendering (and stay open); only the overlays they would open are blocked. **Enabling suppression closes any overlay that is already open** (firing `onCampaignClosed`), and a game in progress inside it loses unsaved progress. `isGamificationSuppressed()` returns the state (default `false`), but right after a page reload it returns `false` until SDK initialisation finishes, even if suppression was saved as on: seed a "pause campaigns" toggle from the service file's localStorage copy (`getSavedGamificationSuppressed()`, key `hydra_gamification_suppressed`) instead.

**Callbacks.** `HydraSDK.setGamificationCallback(callback)` (wrapper `sdkService.setGamificationCallback`) registers host-side hooks for gamification events; pass `null` to stop receiving them. `GamificationCallback` is exported from `cap-hydra-web-sdk`. Every hook is optional, so register only the ones you need. The call is safe right after `initialize()`, but hooks fire only once gamification is enabled and a user has signed in with `identify()`. A later call replaces the earlier hooks instead of adding to them, so keep all hooks in one object, registered once in the service file.

| Hook | Signature | Fires when |
|---|---|---|
| `onInitSuccess` | `() => void` | Gamification initialises successfully |
| `onInitFailure` | `(error: GamificationError) => void` | Gamification initialisation fails (`error.code`, `error.message`) |
| `onEntryPointsLoaded` | `(entryPoints: EntryPoint[]) => void` | Entry points load on initialisation and again on every background resync |
| `onCampaignOpened` | `(campaignId: string) => void` | A campaign actually becomes visible (for embeds and banners, only once the hook element is found on the page) |
| `onCampaignClosed` | `(campaignId: string) => void` | A campaign that fired `onCampaignOpened` closes; always paired 1:1 with it |
| `onAnalyticsEvent` | `(data: unknown) => void` | Campaign content sends an analytics message (raw payload) |
| `onDeepLinkEvent` | `(data: Record<string, unknown>) => void` | Campaign content requests a deep link; fires before any navigation the SDK performs |
| `onGameEventTrigger` | `(eventName: string, data: Record<string, unknown>) => void` | `track()` fires an event with no `ACTION_EVENT` entry point configured; `data` is `{ reason: 'NO_GAME_CONFIGURED' }` |

Deep links: forward `onDeepLinkEvent` as a window event, so your router handles it without the service file depending on the router (pattern from gamification-web, which shows React Router):

```ts
// In the service file (sdkService.ts), right after sdkService.initialize()
export const DEEP_LINK_EVENT = "hydra-deep-link";

sdkService.setGamificationCallback({
  onInitSuccess: () => console.log("Gamification ready"),
  onInitFailure: (error) =>
    console.error("Gamification init failed", error.code, error.message),
  onCampaignOpened: (campaignId) => console.log("Campaign opened", campaignId),
  onCampaignClosed: (campaignId) => console.log("Campaign closed", campaignId),
  onDeepLinkEvent: (data) => {
    window.dispatchEvent(
      new CustomEvent(DEEP_LINK_EVENT, { detail: data.deepLink }),
    );
  },
  onGameEventTrigger: (eventName, data) =>
    console.log("No campaign configured for event", eventName, data.reason),
});

// In the app, once, where your router is available
window.addEventListener(DEEP_LINK_EVENT, (event) => {
  const deepLink = (event as CustomEvent<unknown>).detail;
  if (typeof deepLink !== "string" || !deepLink) return;

  if (deepLink.startsWith("/")) {
    navigate(deepLink); // in-app path: your router's navigate function
  } else if (/^https?:\/\//i.test(deepLink)) {
    window.location.assign(deepLink); // web URL
  } else {
    navigate("/"); // e.g. a mobile-app scheme with no web equivalent
  }
});
```

Replace the `console` calls with your own logging or analytics; register the other hooks (`onEntryPointsLoaded`, `onAnalyticsEvent`) the same way if needed.

> ⚠️ Gap: gamification-web says calling these wrappers (theme, suppression, callbacks) before `initialize()` throws, while web-sdk-api-reference says every method except `initialize()` waits for initialisation. Call `sdkService.initialize()` at module load first and ask a Capillary engineer how the two statements fit together.

**Game and CMS events.** gamification-web says Experience+ sends seven events (five game, two CMS) and documents their payloads. `cuid` and `event_name` are on every event; `cuid` is required and is the loginIdentifier value (mobile number, email or externalId); every other attribute is optional. Payloads are flat JSON (no nested objects) and numbers are sent as numbers.

| Event | Flow | Fires when | Other attributes |
|---|---|---|---|
| `game_open` | Game | A game entry surface opens or launches the game (pop-up, floating icon, modal or embedded banner) | `campaign_id`, `game_type`, `entry_surface`, `embed_id`, `entry_point_id`, `entry_point_location`, `deep_link_url`, `hyper_link_url` |
| `game_viewed` | Game | The game UI is rendered and visible | `campaign_id`, `game_type`, `load_time_ms` (number) |
| `game_played` | Game | The user's first real interaction (spin, scratch, tap or select) | `campaign_id`, `game_type` |
| `game_completed` | Game | The game ends: won, lost, completed or abandoned | `campaign_id`, `game_type`, `total_time_ms` (number) |
| `reward_seen` | Game | The user views the reward (reveal screen or wallet) | `reward_id`, `campaign_id`, `reward_type` |
| `content_open` | CMS | A CMS surface opens or is displayed (widget, banner or full page) | `content_surface` |
| `content_viewed` | CMS | The CMS content is rendered and visible | `page_id`, `content_surface`, `load_time_ms` (number) |

Values listed in the docs: `game_type` `spinthewheel`, `scratchcard`, `slotmachine`, `quiz`, `memorygame`, `giftbox`, `streak`, `multistep`, `referral` (not exhaustive); `entry_surface` `popup`, `floating_icon`, `modal`, `banner_embedded`; `reward_type` `points`, `coupons`, `cashback`, `discount`, `freebie`, `buyXgetY`, `noReward` (not exhaustive); `content_surface` `widget`, `banner`, `full_page`. Sample `game_open` payload:

```json
{
  "cuid": "stringxxx",
  "event_name": "game_open",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "entry_surface": "popup",
  "embed_id": "home_hero",
  "entry_point_id": "ep_12",
  "entry_point_location": "home_screen",
  "deep_link_url": "/home",
  "hyper_link_url": "https://your-url.com"
}
```

**Field mapping.** "While creating the events", map the event fields to the event-creation fields below. All four are required:

| Event-creation field | Maps from |
|---|---|
| `customerId` | `cuid` from the event payload |
| `identifierType` | The login identifier type passed to the SDK: mobile, email or externalId |
| `source` | The SDK (set `source` to SDK) |
| `accountId` | The SDK account ID |

> ⚠️ Gap: the docs don't say where in Capillary these seven events are created ("while creating the events" is all they say), whether they must exist before the first campaign runs (the shared rule is that behavioural events must exist before they are sent; `_shared/overview.md`), or whether the SDK or the Experience+ platform emits them. An earlier version of this guide said the SDK sends them through the normal event pipeline and they appear in your analytics backend; the docs say only "Experience+ sends the following events". Ask a Capillary engineer.

> ⚠️ Gap: the mapping says `source` = SDK, while the SDK's own `source` setting defaults to `WEBPUSH`; the docs don't say whether these are the same value. Also, `entry_surface` values (`popup`, `floating_icon`, `modal`, `banner_embedded`) don't match the container names (`POP_UP`, `ICON_BUTTON`, `BOTTOM_SHEET`, `CHAT_BOX`, `EMBEDDED`, `NATIVE_BANNER`) and no mapping is given. Ask a Capillary engineer.

## Verification
Run all six checks before production (wrapper names from step 6):
1. **Init:** at `debugLevel: "NONE"` a successful init logs nothing. For verbose logs set `"debugLevel": "DEBUG"` in the Remote Config JSON and **republish**; if nothing appears, enable the **Verbose** level in the DevTools Console filter. Init errors log `Failed to initialize SDK:` plus the error.
2. **Page view:** `sdkService.trackPageView()` → an outbound POST to your `baseURL` in the Network tab.
3. **Custom event:** `sdkService.trackEvent("test_event", { source: "smoke_test" })` reaches the Capillary API.
4. **Identify:** `sdkService.identifyUser(...)` → the user profile is created or updated in your Capillary environment.
5. **Reset:** `sdkService.reset()` → user context cleared, later tracking anonymous.
6. **Consent:** `disableTracking()` then `enableTracking()` → events dropped while disabled; queued events resume.

Also: push → the service worker console shows `[FCM SW] Initialized`; gamification → overlay campaigns appear on matching pages after `identify()` and inline hooks fill (with a callback registered, `onInitSuccess` and `onCampaignOpened` log); loyalty → `sdkService.getCapToken()` returns the token.

> ⚠️ Gap: no SDK init-success callback (`onInitSuccess` exists only for gamification), Remote Config fetch check, push-token check or test-push procedure is documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| SDK silently does nothing | `accountId`, `baseURL` or `orgId` missing from Remote Config (fails silently; fetch error only logged) | Add the field(s) to the JSON and republish |
| Events not reaching the API | Wrong `baseURL`, or Remote Config not published | Verify `baseURL`; confirm the parameter is published |
| SDK not initialising on app load | `initialize()` inside a lifecycle hook | Call `sdkService.initialize()` at module top level |
| TypeScript import errors | Package types not resolved | Put `cap-hydra-web-sdk` in `dependencies`; refresh `node_modules` |
| `debugLevel: "DEBUG"` shows nothing extra | Not republished, or DevTools hides `console.debug()` under "Verbose" | Republish; enable Verbose in the Console filter |
| Wrong `actionType` | `"USER_UPDATE"` at login | `"USER_REGISTER"` for login and sign-up |
| Re-identifying on every refresh | Unnecessary; context persists in IndexedDB | `identify()` only on login, sign-up, profile update |
| Events missing after consent revoked | Expected: new events dropped while disabled | Persist and restore consent on load |
| "Firebase App already exists" | Push Firebase app not given its own name | Name it `"hydra-fcm"` (Modules → Push, P3) |
| Push not working | Service worker not found, or wrong VAPID key | Match `serviceWorkerPath` to the file's real location; regenerate the VAPID key if needed |
| Service worker 404 / not registering | File not served at the expected path | Put `firebase-messaging-sw.js` in `public/` so it loads at `https://yourapp/firebase-messaging-sw.js`; check `serviceWorkerPath` (sub-path apps: P3 table) |
| `self.firebase is undefined` in the service worker console | `importScripts` failed, or `YOUR_*` placeholders not replaced | Allow network access to `gstatic.com` (CSP, step 8); replace all `YOUR_*` values |
| No notification shown at all | Code that reads the push body (`event.data.json()` / `text()` / `arrayBuffer()`) added to the worker's `push` listener; the body can be read only once, so Firebase's handler throws | Don't modify the worker logic |
| Notification body / title missing | Campaign sent fields in the `notification` payload | Send them as `data` fields |
| Notification icon missing | `/logo192.png` doesn't exist | Add it to `public/` or change the fallback paths |
| DLR events not recorded | Old service worker cached (a new version waits for the next load: no `skipWaiting`) | DevTools → Application → Service Workers → Unregister, then reload; or have the app post `{ type: "SKIP_WAITING" }` to the worker |
| Gamification entry points not appearing | One of the three `gamification*` fields missing from Remote Config, or not republished; user not identified; URL doesn't match path rules; overlays suppressed | Add all three and republish (confirm values with Capillary); call `identify()`; check rules; `setGamificationSuppressed(false)` |
| Gamification never matches in a webview / custom router | No real URL change | Manual path tracking (`enablePagePathTracking(false)` + `onScreenChanged`) |
| Loyalty iframe not rendering | `<div id="{embedId}">` not in the DOM at render time, wrong `id`, or no token | Match the `embedId`; render the `<div>` before or shortly after `identify()`; `setCapToken` after login |
| SDK requests, iframes or workers blocked | Domains missing from the CSP | Add the step 8 entries |

> ⚠️ Gap: push-notification-web points to the troubleshooting page for "notifications missing a body", but its error table has no such row. The "Notification body / title missing" row above is our reading of the worker, which trusts `data` only.

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
| `HydraSDK.track(eventName, properties?)` | Custom behavioural event; with gamification, can also open an `ACTION_EVENT` campaign |
| `HydraSDK.pageView(options?)` | Page view; `PageViewOptions`: `page_url?`, `page_title?`, `referrer?`, `page_category?` (e.g. `'blog'`, `'product'`, `'checkout'`), `properties?` (no args: current URL and title) |
| `HydraSDK.identify(params)` | `{ identifier: { type, cuid }, actionType, traits? }`; `USER_REGISTER` login / sign-up, `USER_UPDATE` profile changes |
| `HydraSDK.getAnonymousId()` | Backend-assigned anonymous visitor ID or `null`; any auth state |
| `HydraSDK.reset()` | Logout: back to anonymous; clears the Capillary token |
| `HydraSDK.enableSDK()` / `disableSDK()` | Re-enable tracking / disable it (new `track()` / `pageView()` events dropped, queued kept in IndexedDB); `disableSDK()` doesn't affect `identify()`, `reset()` or gamification events |
| `HydraSDK.setCapToken(token)` / `getCapToken()` | Set the loyalty token (persisted, re-renders embeds) / read it (`string \| null`) |
| `HydraSDK.setGamificationSuppressed(value)` | `boolean`; suppress / resume overlay campaigns (no overlay opens while suppressed; enabling closes any open one); returns `void` |
| `HydraSDK.isGamificationSuppressed()` | `boolean`, default `false`; `false` after a reload until SDK init finishes |
| `HydraSDK.enablePagePathTracking(enabled)` | `true` automatic path detection (default), `false` manual; returns `void` |
| `HydraSDK.onScreenChanged(screenName)` | `string`; report the screen in manual mode (no effect in automatic mode); returns `void` |
| `HydraSDK.setTheme(theme)` | `Theme`: `NONE` (default), `LIGHT`, `DARK`, `AUTO`; appends `darkMode` to campaign / loyalty embed URLs loaded afterwards; returns `void` |
| `HydraSDK.setGamificationCallback(callback)` | `GamificationCallback \| null`; register the 8 optional gamification hooks, `null` clears; returns `void` |

**`initialize()` fields (Remote Config bootstrap):**

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `firebaseConfig` | Yes | `FirebaseConfig` | — | Firebase project configuration from the Firebase Console |
| `remoteConfigKey` | Yes | `string` | — | The parameter key name set in Remote Config |
| `appVersion` | No | `string` | — | Host app version for event metadata |
| `retryDelays` | No | `number[]` | `[60000, 120000, 240000, 480000, 900000]` | Retry delays in ms |
| `notifications` | Push only | `NotificationConfig` | — | `{ messaging, vapidKey, serviceWorkerPath }` |

**Remote Config JSON fields** (never set in `initialize()`):

| Field | Required | Default | Description |
|---|---|---|---|
| `accountId` | Yes | — | Organization account identifier |
| `baseURL` | Yes | — | API base URL for all SDK requests |
| `orgId` | Yes | — | Organization ID for API authentication |
| `gamificationWriteKey` | For gamification | — | Write key, from Capillary |
| `gamificationRegion` | For gamification | — | Region code, e.g. `'us'`, `'me'`; derives the API base URL |
| `gamificationBaseUrl` | For gamification | — | Gamification API base URL for your region, from Capillary |
| `brandId` | No | — | Brand identifier (namespaced database names) |
| `applicationId` | No | — | Application identifier (namespaced database names) |
| `source` | No | `WEBPUSH` | Source identifier for visitor profiles |
| `channelType` | No | `web` | Communication channel type |
| `sessionTimeoutMinutes` | No | `30` | Session inactivity timeout in minutes |
| `batchSize` | No | `50` | Max events per batch request |
| `debugLevel` | No | `NONE` | `NONE` / `ERROR` / `WARN` / `INFO` / `DEBUG` / `VERBOSE` |

**`traits`** (all `string` unless noted): `firstName`, `lastName`, `gender`, `birthday`, `city`, `country`, `timezone`, `email`, `mobile`, `externalId`, `custom` (`Record<string, unknown>`: extra attributes, merged into events).

> ⚠️ Gap: not documented: who supplies `brandId` / `applicationId`; `birthday` / `timezone` formats and `gender` values. Ask a Capillary engineer.

> ⚠️ Gap: web-sdk-initialisation's template omits `timezone` from the `traits` type although web-sdk-api-reference lists it; the template in step 6 includes it. The init page's configuration tables (2026-11-17) also don't list `brandId`, `applicationId` or `notifications` as optional fields, while web-sdk-ai-integration-guide (2026-11-23) does.
