---
updatedAt: 2026-11-23T06:02:22.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# AI-Assisted Integration Guide

A copy-paste prompt that lets an AI coding assistant (Cursor, GitHub Copilot, Claude Code, etc.) wire the Capillary Web SDK into your project automatically.

If you'd rather have an AI coding assistant (Cursor, Copilot, Claude, etc.) do the setup for you instead of following the manual steps above, copy everything between `--- START ---` and `--- END ---` and paste it directly into your AI chat, then press Enter. The tool will scan your project and integrate the SDK automatically. Replace the placeholder values (marked with `MY_*`) with your actual credentials — by default (direct-config bootstrap) these are just your Capillary `accountId`/`baseURL`/`orgId`, no Firebase project needed.

#### **--- START --- (copy from here)**

I want to integrate the Capillary Hydra WebSDK (`cap-hydra-web-sdk`) into my web application for event tracking, user identification, and gamification. Please follow every step below exactly.

#### **Firebase Project Setup (First-time Setup)**

Only needed if you're using Remote Config bootstrap, and/or push notifications. If you're using direct-config bootstrap (see Step 0, question 8) and don't need push notifications, you can skip this entire section — no Firebase project is required. Jump to the Direct-Config Bootstrap part of the Configuration Reference below.

If you don't have a Firebase project set up yet, follow these steps:

1. **Create Firebase Project**

1) Go to the Firebase Console (<https://console.firebase.google.com/>)
2) Click "Add project" or "Create a project"
3) Enter your project name (e.g., "my-app-analytics")
4) Choose whether to enable Google Analytics (recommended)
5) Click "Create project"

2. **Add Web App to Firebase Project**

1) In your Firebase project dashboard, click the Web icon (`</>`) to add a web app
2) Enter your app nickname (e.g., "My Web App")
3) Check "Also set up Firebase Hosting" if you plan to use Firebase Hosting (optional)
4) Click "Register app"
5) Copy the Firebase configuration object - you'll need this for Step 2 below

The config object looks like this:

```text
const firebaseConfig = {
  apiKey: "AIzaSyC...",
  authDomain: "my-project.firebaseapp.com",
  databaseURL: "https://my-project-default-rtdb.firebaseio.com",
  projectId: "my-project",
  storageBucket: "my-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX", // optional, only if Analytics is enabled
};
```

3. **Set up Remote Config**

1) In your Firebase project, go to "Remote Config" in the left sidebar
2) Click "Create configuration"
3) Click "Add parameter"
4) Set Parameter key to your desired config key name (e.g., `hydra_sdk_config`)
5) Set Default value to a JSON object with your configuration values from the Capillary team (see the Configuration Reference section below for the full JSON example and field details)
6) Click "Save" then "Publish changes"
7) Remember your parameter key name - you'll use this as `remoteConfigKey` in Step 2

4. **Generate VAPID Key for Push Notifications**

1) In your Firebase project, go to "Project settings" (gear icon in sidebar)
2) Click the "Cloud Messaging" tab
3) Scroll down to "Web configuration"
4) Under "Web Push certificates", click "Generate key pair"
5) Copy the generated VAPID key - you'll need this for Step 2

5. **Enable Required Firebase Services**

Make sure these services are enabled in your Firebase project:

1. Remote Config: Go to Remote Config → should show your configuration

6) **Set Up the Service Worker**

The `firebase-messaging-sw.js` service worker handles background push notifications and delivery receipts. The template is included below — find it in the Service Worker File section.

1. Copy the service worker template from the Service Worker File section below
2. Replace the `YOUR_*` Firebase config placeholders with your actual credentials (same values as your SDK service file)
3. Place it in your project's `public/` directory
4. Set `serviceWorkerPath` in your SDK config (Step 2) based on where your app is served:

| Scenario                                       | `serviceWorkerPath` value            |
| ---------------------------------------------- | ------------------------------------ |
| App at root (`https://example.com/`)           | `"/firebase-messaging-sw.js"`        |
| App at subpath (`https://example.com/my-app/`) | `"/my-app/firebase-messaging-sw.js"` |

#### **Browser Support**

Internet Explorer is not supported.

| Browser | Minimum Version | Notes        |
| ------- | --------------- | ------------ |
| Chrome  | 109+            | Full support |
| Firefox | 140+ (ESR)      | Full support |
| Safari  | 26.3+           | Full support |
| Edge    | 149+ (Chromium) | Full support |

#### **Content Security Policy (CSP)**

If your application enforces a Content Security Policy (CSP), allowlist the following domains so the SDK functions correctly. Add these to your existing directives rather than replacing them — the exact set needed depends on which features you use.

`connect-src`

* `https://*.capillarytech.com` — core API, gamification, and loyalty (always required)
* `https://*.googleapis.com`, `https://*.firebaseio.com`, `https://*.firebaseapp.com` — only if using Remote Config bootstrap and/or push notifications
* `https://*.posthog.com` — SDK diagnostics (always required)

`script-src`

* `'self'`
* `https://*.gstatic.com` — push notifications only (loads the Firebase Messaging scripts inside the service worker)
* `https://*.posthog.com`

`frame-src`

* `https://*.capillarytech.com` — loyalty embeds and gamification iframe content types (CAMPAIGN, WALLET, NUDGE, PROGRAM, REWARD)

`img-src`

* `https://*.capillarytech.com` — loyalty embeds and the gamification STATIC content type

`worker-src`

* `'self'`, `blob:`, `data:` — required for posthog

Example:

```text
connect-src 'self' https://*.capillarytech.com https://*.googleapis.com https://*.firebaseio.com https://*.firebaseapp.com https://*.posthog.com;
script-src 'self' https://*.gstatic.com https://*.posthog.com;
frame-src 'self' https://*.capillarytech.com;
img-src 'self' https://*.capillarytech.com;
worker-src 'self' blob: data:;
```

If you're not using Remote Config bootstrap, push notifications, or gamification/loyalty, only the `capillarytech.com` and `posthog.com` entries are needed.

#### **Step 0 — Ask These Questions Before You Start**

Before writing any code or installing any package, ask the user the following questions in a single message. Wait for all answers before proceeding.

Ask the user:

1. Scope — The core Hydra WebSDK (event tracking, user identification, push notifications) is always included — this is not optional. The only scope decision is whether to also enable gamification and loyalty embeds — see questions 4 and 5 below.
2. Release channel — Should I install the production release (`@latest`, stable) or the beta release (`@beta`, latest pre-release features)? (Default: production — confirm if unsure.)
3. Push notifications — Will this app send push notifications to users? (Yes → the service worker and VAPID key setup are required. No → skip Step 3 and omit `notifications` from the SDK config.)
4. Gamification — Will this app use gamification widgets (overlays, banners, entry points)? (Yes → `gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` must all be set together — in Remote Config, or passed directly to `initialize()` if using direct-config bootstrap (see question 8). No → omit all three fields, skip the Gamification section entirely.)
5. Loyalty embeds — Will this app render loyalty iframe embeds (e.g. points balance, rewards catalogue)? Loyalty embeds are part of gamification, so skip this question if question 4's answer is No. (Yes → include `setCapToken` / `getCapToken` methods and embed div guidance. No → omit those methods.)
6. Cookie consent / GDPR — Does this app need cookie consent management (opt-in/opt-out tracking)? (Yes → include `enableTracking` / `disableTracking` methods. No → omit them.)
7. Firebase credentials — Do you already have your Firebase project credentials (API key, project ID, etc.)? Only relevant if question 3 (push notifications) is Yes, or question 8 (below) is Remote Config bootstrap — skip this question entirely if both of those are the opposite (no push notifications, and direct-config bootstrap), since no Firebase project is involved at all in that case. (Yes → I will fill them in now. No → I will leave `MY_*` placeholders and note what to replace.)
8. Configuration bootstrap — Will you supply SDK configuration (`accountId`, `baseURL`, `orgId`, etc.) via Firebase Remote Config, or pass it directly to `HydraSDK.initialize()`? Direct-config bootstrap → no Firebase project required unless push notifications are also needed; `accountId`, `baseURL`, and `orgId` are passed directly in the `initialize()` call instead — this is the simpler default. Remote Config bootstrap → requires a Firebase project + `remoteConfigKey`; values fetched from Firebase at runtime — choose this if you want to change SDK config without a redeploy. Default: direct-config bootstrap — confirm if unsure.

Use the answers to skip irrelevant sections and avoid generating code the user doesn't need. If any answer is unclear, default to the safer option noted in parentheses and mention the assumption.

#### **Step 1 — Install the SDK**

Using the release channel confirmed in Step 0, detect the package manager from lock files and install accordingly:

| Lock file present   | Production                      | Beta                                 |
| ------------------- | ------------------------------- | ------------------------------------ |
| `package-lock.json` | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |
| `yarn.lock`         | `yarn add cap-hydra-web-sdk`    | `yarn add cap-hydra-web-sdk@beta`    |
| `pnpm-lock.yaml`    | `pnpm add cap-hydra-web-sdk`    | `pnpm add cap-hydra-web-sdk@beta`    |
| `bun.lockb`         | `bun add cap-hydra-web-sdk`     | `bun add cap-hydra-web-sdk@beta`     |
| None detected       | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |

If no lock file is detected, use npm as the default package manager.

#### **Step 2 — Create an SDK service file**

Create a file at `src/services/sdkService.ts` (or `.js` if not using TypeScript). This file initializes the SDK once at module load time and exposes wrapper methods.

Important: Follow my application's existing naming conventions and directory structure. If my codebase uses different patterns (e.g., `camelCase` vs `kebab-case` for filenames, different service directory names, different export patterns), adapt the file location and naming accordingly while keeping the same functionality.

Use the template matching the bootstrap mode confirmed in Step 0, question 8 (default: direct-config). Replace every `MY_*` placeholder with my actual credentials.

Direct-config bootstrap (default):

Push notifications, either mode: the SDK never calls Firebase's `initializeApp()`/`getMessaging()` itself — you create the Firebase app and Messaging instance yourself and pass the instance in via `notifications.messaging`. Only add the `firebase/app`/`firebase/messaging` imports and the `notifications` block below if push notifications are needed; omit both entirely otherwise.

```text
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
        accountId: "MY_ACCOUNT_ID",
        baseURL: "MY_BASE_URL",
        orgId: "MY_ORG_ID",
        appVersion: "1.0.0", // my app's version string

        // Only include if using gamification — obtain from the Capillary team:
        // gamificationWriteKey: "MY_GAMIFICATION_WRITE_KEY", // required together with the two below, only if using gamification
        // gamificationRegion: "us", // e.g. 'us', 'me'
        // gamificationBaseUrl: "MY_GAMIFICATION_BASE_URL", // gamification API base URL for your region

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

No Firebase project, `firebaseConfig`, or `remoteConfigKey` is needed in this mode unless push notifications are also required.

If Remote Config bootstrap instead: use the exact same template above, but replace only the `initialize()` method body with this — every other method (`trackPageView`, `trackEvent`, `identifyUser`, etc.) stays identical:

```text
initialize() {
  try {
    // Only needed if push notifications are required
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
```

Key rules:

* `HydraSDK.initialize()` must be called at module load time (top level of the file), not inside React `useEffect`, Angular `ngOnInit`, or any async lifecycle hook.
* `initialize()` is safe to call multiple times — subsequent calls return the existing instance.
* All other SDK methods (`track`, `pageView`, `identify`, `reset`) internally wait for initialization to complete, so no `isInitialized()` guard is needed.
* Do NOT re-identify the user on page refresh. The SDK persists user context in IndexedDB automatically.
* All calls are fire-and-forget — they return immediately.
* Components should never import `HydraSDK` directly — all calls go through this service.

#### **Step 3 — Create the Service Worker File (push notifications only)**

Skip this step entirely if the user answered "No" to push notifications in Step 0.

Create a file named `firebase-messaging-sw.js` in the project's `public/` directory (or the equivalent static-asset directory served at the site root). Use the exact content from the Service Worker File section below. Leave the `YOUR_*` Firebase config placeholders in place — the developer will fill them in.

* Do not rename the file. It must be `firebase-messaging-sw.js`.
* If the project has no `public/` directory, detect the correct static-asset root (e.g., `static/`, `assets/`, or the bundler's configured public path) and place it there.
* Do not modify the service worker logic — only the Firebase config block is meant to change.

#### **Usage Notes**

The SDK service file above exposes all available methods. Here are non-obvious details to keep in mind when integrating:

* Page views: `trackPageView()` with no arguments auto-captures the current URL and page title. Call it on route changes.
* User identity: Use `"USER_REGISTER"` as `actionType` for both login and signup. Use `"USER_UPDATE"` only for profile updates. Supported identifier types: `"email"`, `"mobile"`, `"externalId"`. Call `reset()` on logout.
* Get anonymous ID: `getAnonymousId()` returns the backend-assigned anonymous visitor ID (`string | null`). Safe to call at any time regardless of whether the user is identified — use it when you only need the visitor ID.
* Cookie consent: When tracking is disabled via `disableTracking()`, new events are dropped. Already-queued events are preserved in IndexedDB and sent when re-enabled. Persist the consent decision in your own storage and restore it on app load.
* Gamification / Loyalty embeds: See the Gamification section below for containers, content types, and loyalty embed setup.

#### **Gamification**

When `gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` are all present, the SDK automatically initializes gamification after every `identify()` call — no additional host-app code is needed. Campaigns and entry points are fetched and rendered automatically.

Opt-in: if all three fields are absent, the gamification module is silently skipped and the rest of the SDK works as normal.

* Remote Config bootstrap: `gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` come from Remote Config — do not pass them in `HydraSDK.initialize()`. Add them to your Remote Config JSON (see Configuration Reference below).
* Direct-config bootstrap: pass all three fields directly in the `initialize()` call instead — same field names, same behavior.

Game and CMS events: Experience+ sends seven events (`game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed`). For when each event fires, its attributes, sample payloads, and field mapping, see [Game and CMS events](https://docs.capillarytech.com/docs/gamification-web#game-and-cms-event-payloads).

**Containers**

Six display container types are supported. Most are appended to `document.body` automatically — only EMBEDDED and NATIVE\_BANNER require a host-provided hook element.

| Container      | Behavior                                             | Host HTML required                                            |
| -------------- | ---------------------------------------------------- | ------------------------------------------------------------- |
| ICON\_BUTTON   | Fixed button (bottom-left) that opens a CHAT\_BOX    | No — appended to `document.body` automatically                |
| CHAT\_BOX      | Fixed panel above the icon button                    | No — appended to `document.body` automatically                |
| POP\_UP        | Centered full-page modal                             | No — appended to `document.body` automatically                |
| BOTTOM\_SHEET  | Sheet that slides up from the bottom                 | No — appended to `document.body` automatically                |
| EMBEDDED       | Full-width inline block injected into a hook element | Yes — `<div id="{hookId}"></div>` at the desired DOM position |
| NATIVE\_BANNER | Block-level inline injection into a hook element     | Yes — `<div id="{hookId}"></div>` at the desired DOM position |

For EMBEDDED and NATIVE\_BANNER, place a `<div>` with the `id` matching the `hookId` configured in the gamification dashboard:

```text
<!-- Place wherever the inline embed should appear -->
<div id='your_hook_id'></div>
```

The SDK uses a `MutationObserver` to wait for these elements, so they are SPA-safe — they do not need to exist at page load.

**Content Types**

Eleven content types control what renders inside a container — all configured from the gamification dashboard, no host-app code required:

| Content type          | What it renders                                              |
| --------------------- | ------------------------------------------------------------ |
| CAMPAIGN              | Iframe loading a campaign URL matched by conditions          |
| WALLET                | Iframe loading the default rewards wallet                    |
| NUDGE                 | Iframe loading a direct URL                                  |
| PROGRAM               | Iframe for loyalty program enrollment and status             |
| REWARD                | Iframe for reward redemption                                 |
| STATIC                | Image (`<img>`) with a click action                          |
| DYNAMIC               | Native progress circle card (live campaign progress)         |
| DYNAMIC\_MULTISTEP\_1 | Native progress bar card                                     |
| DYNAMIC\_MULTISTEP\_2 | Native multi-step progress meter with step circles and CTA   |
| DYNAMIC\_MULTISTEP\_3 | Native collapsible accordion with sticky header and CTA      |
| ACCEPT\_GUARD         | Native streak enrollment modal shown before a campaign opens |

**Loyalty Embeds**

Loyalty embed URLs are returned by the Campaigns API alongside campaign data. The SDK renders each as an iframe into a host-provided placeholder element. Place a `<div>` with an `id` matching the `embedId` provided by the Capillary team wherever you want the embed to appear:

```text
<div id='your_embed_id'></div>
```

After the user logs in, set the Capillary short-lived token so loyalty iframes can display user-specific content:

```text
// After login / token refresh
sdkService.setCapToken("short-lived-cap-token");

// Read back the current token if needed
const token = sdkService.getCapToken(); // string | null
```

The token is:

* Appended automatically as `?capToken=<value>` to every loyalty iframe URL
* Persisted in IndexedDB (survives page reload — no need to set it on every load)
* Cleared automatically on `reset()` / logout

Call `setCapToken` again whenever your app refreshes the token — it triggers an immediate re-render of all loyalty embeds.

#### **Configuration Reference**

`HydraSDK.initialize()` supports two bootstrap modes, selected by whether `remoteConfigKey` is present (see Step 0, question 8):

Required fields for direct-config bootstrap (default, no Firebase):

| Field       | Type     | Description                            |
| ----------- | -------- | -------------------------------------- |
| `accountId` | `string` | Organization account identifier        |
| `baseURL`   | `string` | API base URL for all SDK requests      |
| `orgId`     | `string` | Organization ID for API authentication |

In this mode, omit `firebaseConfig`/`remoteConfigKey` entirely. No Firebase project is required unless `notifications` is also configured — see Step 2's direct-config template above.

Required fields for Remote Config bootstrap (alternative):

| Field             | Type             | Description                                                         |
| ----------------- | ---------------- | ------------------------------------------------------------------- |
| `firebaseConfig`  | `FirebaseConfig` | Firebase project configuration (from your Firebase console)         |
| `remoteConfigKey` | `string`         | Remote Config key for SDK config (from your Firebase Remote Config) |

Optional fields (either mode):

| Field           | Type                 | Default                                   | Description                         |
| --------------- | -------------------- | ----------------------------------------- | ----------------------------------- |
| `appVersion`    | `string`             | —                                         | Host app version for event metadata |
| `retryDelays`   | `number[]`           | `[60000, 120000, 240000, 480000, 900000]` | Custom retry delays in ms           |
| `notifications` | `NotificationConfig` | —                                         | Push notification config            |

Remote Config bootstrap only — auto-populated from Remote Config, do NOT set manually in `initialize()`. (In direct-config bootstrap, pass these same fields directly in `initialize()` instead — `accountId`/`baseURL`/`orgId` become required there, per the table above; everything else keeps the same defaults.)

| Field                   | Required | Default   | Description                                                                                                               |
| ----------------------- | -------- | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| `accountId`             | Yes      | —         | Organization account identifier                                                                                           |
| `baseURL`               | Yes      | —         | API base URL for all SDK requests                                                                                         |
| `orgId`                 | Yes      | —         | Organization ID for API authentication                                                                                    |
| `brandId`               | No       | —         | Brand identifier for namespaced database names                                                                            |
| `applicationId`         | No       | —         | Application identifier for namespaced database names                                                                      |
| `source`                | No       | `WEBPUSH` | Source identifier for visitor profiles                                                                                    |
| `channelType`           | No       | `web`     | Communication channel type                                                                                                |
| `sessionTimeoutMinutes` | No       | `30`      | Session inactivity timeout in minutes                                                                                     |
| `batchSize`             | No       | `50`      | Max events per batch request                                                                                              |
| `debugLevel`            | No       | `NONE`    | Logging level (`NONE` / `ERROR` / `WARN` / `INFO` / `DEBUG` / `VERBOSE`)                                                  |
| `gamificationWriteKey`  | Yes\*    | —         | gamification write key. Required to enable gamification. Obtain from the Capillary team.                                  |
| `gamificationRegion`    | Yes\*    | —         | gamification region code (e.g. `'us'`, `'me'`). Required to enable gamification. Derives the API base URL automatically.  |
| `gamificationBaseUrl`   | Yes\*    | —         | The gamification API base URL for your region (e.g. `'https://api-us.customerglu.com'`). Required to enable gamification. |

* `gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` are all required together for gamification features to work. Omit all three only if gamification is not being used.

Example Remote Config JSON (stored as the value of your `remoteConfigKey` in Firebase Console):

```text
{
  "accountId": "100458",
  "baseURL": "https://api.example.capillarytech.com",
  "orgId": "100458",
  "brandId": "1",
  "applicationId": "2",
  "source": "WEBPUSH",
  "channelType": "web",
  "sessionTimeoutMinutes": 30,
  "batchSize": 50,
  "debugLevel": "NONE",
  "gamificationWriteKey": "wk_live_xxxxxxxxxx",
  "gamificationRegion": "us",
  "gamificationBaseUrl": "https://api-us.customerglu.com"
}
```

Note: the required fields (`accountId`, `baseURL`, `orgId`) must exist in your Remote Config JSON. If missing, `HydraSDK.initialize()` will fail. Optional fields use their defaults if omitted.

#### **Public API Quick Reference**

| Method                                       | Description                                                                                  |
| -------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `HydraSDK.initialize(config)`                | Initialize the SDK singleton (call once)                                                     |
| `HydraSDK.track(eventName, properties?)`     | Track a custom behavioral event                                                              |
| `HydraSDK.pageView(options?)`                | Track a page view (auto-captures URL/title if no args)                                       |
| `HydraSDK.identify(params)`                  | Identify a user (login / signup / update)                                                    |
| `HydraSDK.getAnonymousId()`                  | Returns the backend-assigned anonymous visitor ID, or `null`. Safe to call at any time.      |
| `HydraSDK.reset()`                           | Sign out user, return to anonymous tracking                                                  |
| `HydraSDK.enableSDK()`                       | Re-enable tracking after disable                                                             |
| `HydraSDK.disableSDK()`                      | Disable tracking (new events are dropped)                                                    |
| `HydraSDK.setCapToken(token)`                | Set Capillary token for loyalty embeds; triggers immediate re-render; persisted in IndexedDB |
| `HydraSDK.getCapToken()`                     | Returns the current Capillary token, or `null` if not set                                    |
| `HydraSDK.setGamificationSuppressed(value)`  | Suppress (`true`) or resume (`false`) overlay campaigns                                      |
| `HydraSDK.isGamificationSuppressed()`        | Returns the current suppression state. Defaults to `false`                                   |
| `HydraSDK.enablePagePathTracking(enabled)`   | Toggle automatic (default) vs. manual screen/path detection for gamification display rules   |
| `HydraSDK.onScreenChanged(screenName)`       | Report the current screen when path tracking is manual — call on every navigation            |
| `HydraSDK.setTheme(theme)`                   | Set the gamification theme: `NONE` (default), `LIGHT`, `DARK`, or `AUTO`                     |
| `HydraSDK.setGamificationCallback(callback)` | Register hooks for gamification lifecycle events; pass `null` to clear                       |

Now please implement the following in my application:

Required Implementation:

* Step 1: Install the SDK package
* Step 2: Create the SDK service file following my existing codebase conventions (file naming, directory structure, import/export patterns) — use the template matching the bootstrap mode confirmed in Step 0, question 8, and include only the methods relevant to the features confirmed in Step 0
* Step 3 (push notifications only): Create `firebase-messaging-sw.js` in the static-asset directory using the content from the Service Worker File section below — leave all `YOUR_*` placeholders in place. Skip entirely if push notifications are not needed.

Usage Notes (do NOT auto-implement): the Usage Notes section is reference only. I will integrate these methods myself where I see fit in my application flow.

After completing the implementation, include the following in your response:

1. If Remote Config bootstrap, or push notifications were selected: a Firebase Project Setup checklist — list all the steps from the "Firebase Project Setup" section above so I know exactly what to set up if I haven't already (creating a Firebase project, adding a web app, setting up Remote Config, generating a VAPID key, and enabling required services). Do NOT create or auto-generate any of these — just provide the checklist as a guide. Skip this entirely if direct-config bootstrap was selected without push notifications — no Firebase project is needed.
2. A reminder to replace all `MY_*` placeholders in the SDK service file with actual credentials — and, if push notifications are enabled, all `YOUR_*` placeholders in `firebase-messaging-sw.js` too (both files use the same Firebase credentials in that case).

#### **Service Worker File**

Copy this entire file into `public/firebase-messaging-sw.js` and replace the `YOUR_*` placeholders in the Firebase config block with your real credentials.

```text
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
// ⚠️ REPLACE WITH YOUR FIREBASE CONFIGURATION ⚠️
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

**Service Worker Notes**

* Default icons: The worker falls back to `/logo192.png` for icon and badge. Make sure that file exists in your `public/` directory, or change the fallback paths.
* Firebase version: The worker loads Firebase `10.7.1` via `importScripts`. Keep this aligned with the SDK's expected Firebase version unless told otherwise by the Capillary team.

#### **--- END --- (stop copying here)**