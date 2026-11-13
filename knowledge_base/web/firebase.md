---
platform: web
config_mode: firebase
sdk_package: cap-hydra-web-sdk
sdk_version: 1.1.0-beta.20260619085241   # 2024 gamification guide's minimum, via `@beta` (p.8); the public docs pin no version: production `@latest` (default) or `@beta` (web-sdk-install)
modules_covered: [core, push, visitor, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, multi_account]
sources: ["Integration document _ Experience+ pp.7–12 (Gamification WebSDK Integration Guide)", "Integration document _ Experience+ pp.13–24 (Hydra WEB SDK Integration Runbook)", "Capillary developer docs (docs.capillarytech.com): web-sdk, web-sdk-getting-started, web-sdk-install, web-sdk-initialisation, configure-firebase-web, push-notification-web, gamification-web, web-sdk-api-reference, web-sdk-ai-integration-guide, web-sdk-troubleshooting (updated 2026-08-18 to 2026-09-24)"]
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
| Gamification: containers, content types, URL path rules, loyalty embeds, suppression, manual path tracking | Documented |
| In-App, Inbox, Multi-account | Not documented for Web |

## Requirements
- `cap-hydra-web-sdk` (step 5), in `dependencies`. TypeScript or JavaScript.
- The client's own Firebase project with a web app and Remote Config (steps 1–4).
- Push only: the Firebase JS SDK (`firebase`) in your project; the Web SDK never installs or bundles Firebase.
- Event tracking, user identification and gamification work on all modern evergreen browsers. Push needs Service Worker and Push API support. **Internet Explorer is not supported.**

| Browser | Minimum version (push) |
|---|---|
| Chrome | 109+ |
| Firefox | 140+ (ESR) |
| Safari | 26.3+ |
| Edge (Chromium) | 149+ |

> ⚠️ Correction: ✅ Use the browser matrix above (push-notification-web, web-sdk-ai-integration-guide). ❌ Don't use the 2024 table (Chrome 49+, Firefox 52+, Safari 10+ / 11.1+ for Service Worker, Edge 79+, IE 11 limited) (Integration document p.16). *Pending SME confirmation.*

> ⚠️ Gap: no Node.js / bundler / framework versions are stated; nor whether `firebase` must be installed for Remote Config without push, or which `firebase` version matches the SDK (the service worker loads Firebase `10.7.1` compat scripts and should stay "aligned with the SDK's expected Firebase version", which isn't given). Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` and `_shared/firebase-setup.md`.

- **Capillary values go in the Remote Config JSON (step 3), not in code:** `accountId`, `baseURL`, `orgId` (always); `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` (all three, for gamification).
- **Only if used:** each `hookId` for `EMBEDDED` / `NATIVE_BANNER` containers (gamification dashboard entry point settings, provided by the Capillary team); each loyalty `embedId` (Capillary team) and a Capillary short-lived token for the logged-in user (how to obtain it isn't documented; see `_shared/prerequisites.md`); URL path rules per entry point (dashboard, set by the Capillary team).
- **Client's own:** Firebase web config and Remote Config key (steps 1–3); VAPID key (push).

**Decide before writing code** (the official AI runbook asks these first; defaults in brackets): release channel [production]; push notifications?; gamification?; loyalty embeds (only if gamification)?; cookie consent / GDPR?; Firebase credentials ready?; bootstrap mode [direct-config is the SDK default; this file is Remote Config]. Generate only what the answers need, and state any default you assumed.

> ⚠️ Correction: ✅ Use the current AI-assisted runbook (web-sdk-ai-integration-guide), summarised in this file. ❌ Don't use the 2024 Cursor runbook (Integration document pp.13–24): it has no `notifications.messaging`, no service-worker file, `getUser()` instead of `getAnonymousId()`, and an outdated browser table. *Pending SME confirmation.*

> ⚠️ Gap: not documented: what the client sends to register a web app, the full list of region values (docs show `'us'`, `'me'`), and whether the `identify()` identifier must match the CRM Account Linking Identifier. Ask a Capillary engineer.

## Steps
Steps 1–4 are first-time Firebase setup (skip what exists); 5–8 add the SDK.

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

| Lock file | Production (`@latest`, default) | Beta (`@beta`: staging / pre-release testing) |
|---|---|---|
| `package-lock.json` / none | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |
| `yarn.lock` | `yarn add cap-hydra-web-sdk` | `yarn add cap-hydra-web-sdk@beta` |
| `pnpm-lock.yaml` | `pnpm add cap-hydra-web-sdk` | `pnpm add cap-hydra-web-sdk@beta` |
| `bun.lockb` | `bun add cap-hydra-web-sdk` | `bun add cap-hydra-web-sdk@beta` |

For push, also install `firebase`.

### 6. Create the SDK service file and initialise at module load
One service file wraps every SDK call; follow the app's own file naming, folder and export conventions (`.js` if not using TypeScript). Include only the methods for features the app uses. Replace the `MY_*` values with your Firebase values (steps 2–3). Add the `firebase/*` imports, the `initializeApp(...)` lines and the `notifications` block **only for push** (Modules → Push); otherwise delete them.

```ts file=src/services/sdkService.ts
import { HydraSDK } from "cap-hydra-web-sdk";
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

**Rules to enforce:**
- Call `HydraSDK.initialize()` at module load time (top level of the file), **never** inside React `useEffect`, Angular `ngOnInit`, `mounted()` or any async lifecycle hook. Import the service file from the app entry point.
- `initialize()` is safe to call more than once; later calls return the existing instance.
- Components **never** import `HydraSDK` directly; every call goes through the service.
- Don't `await` SDK calls (all are fire-and-forget) and don't add `isInitialized()` guards: the SDK queues calls internally until ready.
- **Don't re-identify the user on page refresh**; the SDK persists user context in IndexedDB.
- Capillary and gamification fields come only from Remote Config; don't pass them to `initialize()`.
- When an AI assistant runs this integration it implements only install, this service file and (push) the service worker; it leaves `MY_*` / `YOUR_*` placeholders it has no values for, reminds the developer to replace them, and gives the Firebase setup (steps 1–4, VAPID key) as a checklist without creating anything. Wiring calls into the app flow (step 7) is the developer's choice.

### 7. Call the service from the app
| When | Call | Notes |
|---|---|---|
| Every route change | `sdkService.trackPageView()` | No args: current URL and title; or pass `{ url, title, category, properties }` |
| Custom event | `sdkService.trackEvent(name, properties?)` | e.g. `sdkService.trackEvent("test_event", { source: "smoke_test" })` |
| Login **and** sign-up | `sdkService.identifyUser(type, cuid, "USER_REGISTER", traits?)` | `type`: `"email"`, `"mobile"`, `"externalId"`; `cuid` = the user's value for it |
| Profile update only | `sdkService.identifyUser(type, cuid, "USER_UPDATE", traits?)` | Never at login |
| Logout | `sdkService.reset()` | Back to anonymous; clears the Capillary token |
| Consent granted / revoked | `sdkService.enableTracking()` / `disableTracking()` | While disabled, new events are dropped; queued ones stay in IndexedDB and are sent on re-enable. Persist the decision yourself and restore it on app load |
| After login / token refresh (loyalty) | `sdkService.setCapToken(token)` | Modules → Gamification |

```js
sdkService.identifyUser("email", "testuser@example.com", "USER_REGISTER", {
  firstName: "Test",
  lastName: "User",
});
```

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

> ⚠️ Gap: the docs' example `gamificationBaseUrl` is on `customerglu.com` (`https://api-us.customerglu.com`), which isn't in the `connect-src` allowlist. Ask a Capillary engineer whether gamification needs that domain allowlisted.

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

> ⚠️ Correction: ✅ Use the `firebase-messaging-sw.js` published in push-notification-web. ❌ Don't wait for a template from the Capillary team (Integration document pp.14–15). *Pending SME confirmation.*

> ⚠️ Gap: the two published copies of the service worker differ: web-sdk-ai-integration-guide's (later) adds a `request.onblocked` handler and a warning for pushes with no `data` payload; push-notification-web's lacks both. Ask a Capillary engineer which is current.

> ⚠️ Gap: not documented: the browser permission prompt (who triggers it and when), foreground message handling, and how to send a test push. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Visitor
Tracking is anonymous before `identify()` and after `reset()`; `source` defaults to `WEBPUSH`. `sdkService.getAnonymousId()` returns the backend-assigned anonymous visitor ID (`string | null`), safe at any time regardless of auth state.

> ⚠️ Correction: ✅ Use `HydraSDK.getAnonymousId()` for the visitor ID (web-sdk-api-reference lists every public method; `getUser()` isn't one). ❌ Don't use `HydraSDK.getUser()` (Integration document runbook pp.13–24). *Pending SME confirmation.*

### Gamification
Part of `cap-hydra-web-sdk`; no extra package. Opt-in: put **all three** `gamificationWriteKey`, `gamificationRegion` and `gamificationBaseUrl` in the Remote Config JSON (step 3) and **republish**; never in `initialize()`. With none of them, gamification is silently skipped and the rest of the SDK works normally. After every `identify()` the SDK fetches campaigns and entry points and renders them; everything is configured in the gamification dashboard, so no host code is needed except the inline hook / loyalty `<div>`s.

> ⚠️ Correction: ✅ Use all three `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` together (web-sdk-initialisation, configure-firebase-web, gamification-web). ❌ Don't treat `gamificationBaseUrl` as optional (Integration document p.9). *Pending SME confirmation.*

> ⚠️ Gap: the 2024 gamification guide requires `cap-hydra-web-sdk` `{{sdk_version}}` or later via `@beta` (p.8); the public docs name no minimum version or channel for gamification. Ask a Capillary engineer.

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
Run all six checks before production (wrapper names from step 6):
1. **Init:** at `debugLevel: "NONE"` a successful init logs nothing. For verbose logs set `"debugLevel": "DEBUG"` in the Remote Config JSON and **republish**; if nothing appears, enable the **Verbose** level in the DevTools Console filter. Init errors log `Failed to initialize SDK:` plus the error.
2. **Page view:** `sdkService.trackPageView()` → an outbound POST to your `baseURL` in the Network tab.
3. **Custom event:** `sdkService.trackEvent("test_event", { source: "smoke_test" })` reaches the Capillary API.
4. **Identify:** `sdkService.identifyUser(...)` → the user profile is created or updated in your Capillary environment.
5. **Reset:** `sdkService.reset()` → user context cleared, later tracking anonymous.
6. **Consent:** `disableTracking()` then `enableTracking()` → events dropped while disabled; queued events resume.

Also: push → the service worker console shows `[FCM SW] Initialized`; gamification → overlay campaigns appear on matching pages after `identify()` and inline hooks fill; loyalty → `sdkService.getCapToken()` returns the token.

> ⚠️ Gap: no init-success callback, Remote Config fetch check, push-token check or test-push procedure is documented. Ask a Capillary engineer.

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
| DLR events not recorded | Old service worker cached | DevTools → Application → Service Workers → Unregister, then reload |
| Gamification entry points not appearing | One of the three `gamification*` fields missing from Remote Config, or not republished; user not identified; URL doesn't match path rules; overlays suppressed | Add all three and republish (confirm values with Capillary); call `identify()`; check rules; `setGamificationSuppressed(false)` |
| Gamification never matches in a webview / custom router | No real URL change | Manual path tracking (`enablePagePathTracking(false)` + `onScreenChanged`) |
| Loyalty iframe not rendering | `<div id="{embedId}">` not in the DOM at render time, wrong `id`, or no token | Match the `embedId`; render the `<div>` before or shortly after `identify()`; `setCapToken` after login |
| SDK requests, iframes or workers blocked | Domains missing from the CSP | Add the step 8 entries |

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

**`traits`** (all `string` unless noted): `firstName`, `lastName`, `gender`, `birthday`, `city`, `country`, `timezone`, `email`, `mobile`, `externalId`, `custom` (`Record<string, unknown>`: extra attributes, merged into events). The step 6 template's `traits` type omits `timezone`; add it if needed.

> ⚠️ Gap: not documented: who supplies `brandId` / `applicationId`; `birthday` / `timezone` formats and `gender` values. Ask a Capillary engineer.
