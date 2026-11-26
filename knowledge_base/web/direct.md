---
platform: web
config_mode: direct
sdk_package: cap-hydra-web-sdk
sdk_version: 1.10.6   # stated by web-sdk-getting-started (2026-11-17); the docs don't say if it is a minimum or just current, so install stays unpinned: `@latest` (default) or `@beta` (web-sdk-install)
modules_covered: [core, push, visitor, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, multi_account]
sources: ["Integration document _ Experience+ pp.60–71 (WEB Hydra SDK – Integration Guide, Firebase excluded)", "Capillary developer docs (docs.capillarytech.com): web-sdk (2026-08-18); web-sdk-getting-started, web-sdk-install, web-sdk-initialisation, configure-firebase-web, push-notification-web, web-sdk-api-reference, web-sdk-troubleshooting, prerequisites (2026-11-17); gamification-web, web-sdk-ai-integration-guide (2026-11-23)"]
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
| Gamification: containers, content types, URL path rules, loyalty embeds, suppression, manual path tracking, theme, callbacks / deep links, game and CMS events | Documented |
| In-App, Inbox, Multi-account | Not documented for Web |

## Requirements
- `cap-hydra-web-sdk` from npm (step 1), in `dependencies`. TypeScript or JavaScript.
- Push only: the Firebase JS SDK (`firebase`) in your project; the Web SDK never installs or bundles Firebase.
- Browsers: the minimums below are the push-notification-web "Browser Support Matrix" (Push Notifications column: Supported). web-sdk-getting-started points to that matrix under "Browser support" for the SDK as a whole, and web-sdk-ai-integration-guide lists the same numbers as "Full support", so they may be the SDK's general minimums rather than push-only (unconfirmed; see the Gap below). Push also needs Service Worker and Push API support. **Internet Explorer is not supported.**
- SDK version: web-sdk-getting-started states `1.10.6` ("SDK version", 2026-11-17). Install stays unpinned (`@latest` default, or `@beta`; step 1).

| Browser | Minimum version (push) |
|---|---|
| Chrome | 109+ |
| Firefox | 140+ (ESR) |
| Safari | 26.3+ |
| Edge (Chromium) | 149+ |

> ⚠️ Gap: the Edge number looks inconsistent: Edge (Chromium) 149+ sits beside Chrome 109+ (same engine), which looks like a typo for 109, and Safari 26.3+ is also a very recent floor. The docs also don't say whether these minimums are push-only (only the push page labels them "Push Notifications: Supported"; the AI guide says "Full support"). Ask a Capillary engineer to confirm the Edge number and the scope.

> ⚠️ Gap: no Node.js / bundler / framework versions are stated, nor which `firebase` npm version matches the SDK (the service worker loads Firebase `10.7.1` compat scripts and should stay "aligned with the SDK's expected Firebase version", which isn't given). Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md`. From the Capillary team: Account ID → `accountId`, Base URL → `baseURL`, Org ID → `orgId`; for gamification, all three of Gamification Write Key → `gamificationWriteKey`, Gamification Region → `gamificationRegion`, Gamification Base URL → `gamificationBaseUrl`.

Only if used:
- **EMBEDDED / NATIVE_BANNER containers:** each `hookId`, configured in the gamification dashboard (entry point settings) and provided by the Capillary team.
- **Loyalty embeds:** each `embedId` from the Capillary team, and a Capillary short-lived token for the logged-in user (how to obtain it isn't documented; see `_shared/prerequisites.md`).
- **URL path rules** per entry point: configured in the gamification dashboard, provided by the Capillary team during campaign setup.
- **Web push:** your Firebase project's web config and a VAPID key (Modules → Push).

**Decide before writing code** (the official AI runbook asks these first; defaults in brackets): release channel [production]; push notifications?; gamification?; loyalty embeds (only if gamification)?; cookie consent / GDPR?; Firebase credentials ready (only if push)?; bootstrap mode [direct-config, this file]. Generate only what the answers need, and state any default you assumed.

> ⚠️ Gap: the AI guide's first question calls the core SDK, including push notifications, "always included — this is not optional", yet its third question asks whether push is needed, and prerequisites / getting-started say Firebase is needed only for push or Remote Config. This guide treats push as optional. Ask a Capillary engineer if unsure.

> ⚠️ Gap: not documented: what the client sends to register a web app, the full list of region values (docs show `'us'`, `'me'`), and whether the `identify()` identifier must match the CRM Account Linking Identifier. Ask a Capillary engineer.

> ⚠️ Gap: the Web docs' `baseURL` example is `https://api.example.capillarytech.com`; they don't say whether Web uses the same cluster hosts as the mobile platforms (`_shared/prerequisites.md`). Use the Base URL Capillary confirms for the org.

## Steps

### 1. Install the SDK
Use the lock file in the project root to pick the package manager (none → npm).

| Lock file | Production (`@latest`, default) | Beta (`@beta`: pre-release testing, latest features before the next stable cut) |
|---|---|---|
| `package-lock.json` / none | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |
| `yarn.lock` | `yarn add cap-hydra-web-sdk` | `yarn add cap-hydra-web-sdk@beta` |
| `pnpm-lock.yaml` | `pnpm add cap-hydra-web-sdk` | `pnpm add cap-hydra-web-sdk@beta` |
| `bun.lockb` | `bun add cap-hydra-web-sdk` | `bun add cap-hydra-web-sdk@beta` |

For push, also install `firebase`.

### 2. Create the SDK service file and initialise at module load
One service file wraps every SDK call; follow the app's own file naming, folder and export conventions (`.js` if not using TypeScript). Include only the methods for features the app uses. Add the `firebase/*` imports and the `notifications` block **only for push**; otherwise delete both (Modules → Push). Uncomment the three `gamification*` lines together, only for gamification; then also keep the `Theme` / `GamificationCallback` import and the gamification wrappers at the end of the class (Modules → Gamification), and delete them otherwise.

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

With gamification on, an event name can also open a campaign (`ACTION_EVENT` entry points; Modules → Gamification).

> ⚠️ Correction: ✅ Use `HydraSDK.track(...)` and `HydraSDK.pageView(...)`, called through the service (web-sdk-api-reference). ❌ Don't use `WebSDK.track(...)` / `WebSDK.pageView(...)` (event and page-view examples, Integration document pp.64–65); `WebSDK` is never imported. *Pending SME confirmation.*

### 7. Track page views
Call on every route change. With no arguments it captures the current URL and title; pass `{ page_url, page_title, referrer, page_category, properties }` to override any of them.

```js
sdkService.trackPageView();
```

| Option | Type | Meaning |
|---|---|---|
| `page_url` | `string` | Override the current page URL |
| `page_title` | `string` | Override the current page title |
| `referrer` | `string` | Override the page referrer |
| `page_category` | `string` | Page category, e.g. `'blog'`, `'product'`, `'checkout'` |
| `properties` | `Record<string, unknown>` | Custom properties |

### 8. Wire up cookie consent (optional)
```js
sdkService.disableTracking(); // Events dropped
sdkService.enableTracking(); // Queued events resume
```
While disabled, new `track()` / `pageView()` events are dropped; already-queued events stay in IndexedDB and are sent on re-enable. `disableSDK()` does not affect `identify()`, `reset()` or gamification events. Persist the consent decision in your own storage and restore it on app load by calling `enableTracking()` / `disableTracking()`.

> ⚠️ Gap: because `disableSDK()` leaves `identify()`, `reset()` and gamification events running, the docs don't say how to fully opt a user out. Ask a Capillary engineer if your consent rules need more than this.

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

> ⚠️ Gap: the docs' example `gamificationBaseUrl` is on `customerglu.com` (`https://api-us.customerglu.com`), which isn't in the `connect-src` allowlist. The docs also describe `gamificationRegion` as deriving the API base URL automatically while still marking `gamificationBaseUrl` required, and describe the `capillarytech.com` entry as covering gamification traffic. Ask a Capillary engineer whether gamification needs that domain allowlisted and what `gamificationBaseUrl` should be.

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

> ⚠️ Correction: ✅ Use `notifications: { messaging: getMessaging(firebaseApp), vapidKey, serviceWorkerPath }` (push-notification-web, web-sdk-initialisation). ❌ Don't put `firebaseConfig` in `notifications` (Integration document p.62). *Pending SME confirmation.*

> ⚠️ Gap: not documented: the browser permission prompt (who triggers it and when), foreground message handling, how to send a test push, and any iOS / iPadOS Safari web-push requirements. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Visitor
Tracking is anonymous before `identify()` and after `reset()`; `source` defaults to `WEBPUSH`. `sdkService.getAnonymousId()` returns the backend-assigned anonymous visitor ID (`string | null`), safe at any time regardless of auth state.

> ⚠️ Correction: ✅ Use `HydraSDK.getAnonymousId()` for the visitor ID (web-sdk-api-reference lists every public method; `getUser()` isn't one). ❌ Don't use `HydraSDK.getUser()` (Integration document pp.60–71). *Pending SME confirmation.*

### Gamification
Part of `cap-hydra-web-sdk`; no extra package. Opt-in: set **all three** `gamificationWriteKey`, `gamificationRegion` and `gamificationBaseUrl` in `initialize()` (step 2); with none of them, gamification is silently skipped and the rest of the SDK works normally. After every `identify()` the SDK fetches campaigns and entry points and renders them; everything is configured in the gamification dashboard, so no host code is needed except the inline hook / loyalty `<div>`s; theme, callbacks and deep links below are optional.

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
Run all six checks before production (wrapper names from step 2):
1. **Init:** at `debugLevel: "NONE"` a successful init logs nothing. For verbose logs set `debugLevel: "DEBUG"` in `initialize()` temporarily; if nothing appears, enable the **Verbose** level in the DevTools Console filter.
2. **Page view:** `sdkService.trackPageView()` → an outbound POST to your `baseURL` in the Network tab.
3. **Custom event:** `sdkService.trackEvent("test_event", { source: "smoke_test" })` reaches the Capillary API.
4. **Identify:** `sdkService.identifyUser(...)` → the user profile is created or updated in your Capillary environment.
5. **Reset:** `sdkService.reset()` → user context cleared, later tracking anonymous.
6. **Consent:** `disableTracking()` then `enableTracking()` → events dropped while disabled; queued events resume.

Also: push → the service worker console shows `[FCM SW] Initialized`; gamification → overlay campaigns appear on matching pages after `identify()` and inline hooks fill (with a callback registered, `onInitSuccess` and `onCampaignOpened` log); loyalty → `sdkService.getCapToken()` returns the token.

> ⚠️ Gap: no SDK init-success callback (`onInitSuccess` exists only for gamification), push-token check or test-push procedure is documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| `initialize()` throws a synchronous `Error` (the service-file template catches it, so the visible symptom is `Failed to initialize SDK:` in the console) | `accountId`, `baseURL` or `orgId` missing | Add the field(s) to the `initialize()` call |
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
| DLR events not recorded | Old service worker cached (a new version waits for the next load: no `skipWaiting`) | DevTools → Application → Service Workers → Unregister, then reload; or have the app post `{ type: "SKIP_WAITING" }` to the worker |
| "Firebase App already exists" | The push Firebase app wasn't given its own name, so it collides with another Firebase app on the site (the SDK creates none in this mode) | Name it `"hydra-fcm"` (Modules → Push, P3) |
| Gamification entry points not appearing | One of `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` missing; user not identified; URL doesn't match path rules; overlays suppressed | Add all three (confirm values with Capillary); call `identify()`; check rules; `setGamificationSuppressed(false)` |
| Gamification never matches in a webview / custom router | No real URL change | Manual path tracking (`enablePagePathTracking(false)` + `onScreenChanged`) |
| Loyalty iframe not rendering | `<div id="{embedId}">` not in the DOM at render time, wrong `id`, or no token | Match the `embedId`; render the `<div>` before or shortly after `identify()`; `setCapToken` after login |
| SDK requests, iframes or workers blocked | Domains missing from the CSP | Add the step 9 entries |

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

**`traits`** (all `string` unless noted): `firstName`, `lastName`, `gender`, `birthday`, `city`, `country`, `timezone`, `email`, `mobile`, `externalId`, `custom` (`Record<string, unknown>`: extra attributes, merged into events).

> ⚠️ Gap: not documented: who supplies `brandId` / `applicationId`; `birthday` / `timezone` formats and `gender` values. Ask a Capillary engineer.

> ⚠️ Gap: web-sdk-initialisation's template omits `timezone` from the `traits` type although web-sdk-api-reference lists it; the template in step 2 includes it. The init page's configuration tables (2026-11-17) also don't list `brandId`, `applicationId` or `notifications` as optional fields, while web-sdk-ai-integration-guide (2026-11-23) does.
