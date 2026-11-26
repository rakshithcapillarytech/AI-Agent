---
updatedAt: 2026-11-17T07:38:34.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Initialise SDK

This section provides information on initialisation of the SDK.

# Configuration bootstrap

`HydraSDK.initialize()` supports two bootstrap modes:

* **Direct-config bootstrap** (default, simpler) — no Firebase project required unless push notifications are also needed; `accountId`/`baseURL`/`orgId` are passed directly in the `initialize()` call.
* **Remote Config bootstrap** — requires a Firebase project + `remoteConfigKey`; values are fetched from Firebase at runtime. Use this if you want to change SDK config without a redeploy.

The two modes are selected by whether `remoteConfigKey` is present.

# Create the SDK service file

Rather than importing `HydraSDK` directly all over your app, wrap it in one service file and call that service everywhere else. This keeps every SDK call in one place.

Create a service file at a path that fits your project's conventions (e.g. `src/services/sdkService.ts`).

## Direct-config bootstrap (default)

Push notifications, either mode: the SDK never calls Firebase's `initializeApp()`/`getMessaging()` itself — you create the Firebase app and Messaging instance yourself and pass the instance in via `notifications.messaging`. Only add the `firebase/app`/`firebase/messaging` imports and the `notifications` block below if push notifications are needed; omit both entirely otherwise. See [Configure Push Notifications](https://docs.capillarytech.com/docs/push-notification-web).

```typescript
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
        appVersion: "1.0.0", // host application version

        // Required together, only if using gamification — obtain from the Capillary team:
        // gamificationWriteKey: "MY_GAMIFICATION_WRITE_KEY",
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

  // --- User Consent ---
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

// IMPORTANT: Initialize at module load time — NOT inside useEffect, ngOnInit, or any lifecycle hook
sdkService.initialize();
```

No Firebase project, `firebaseConfig`, or `remoteConfigKey` is needed in this mode unless push notifications are also required.

## Remote Config bootstrap (alternative)

Use the exact same service file, but replace only the `initialize()` method body with this:

```typescript
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
      appVersion: "1.0.0", // host application version
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
```

In this mode, `gamificationWriteKey`/`gamificationRegion`/`gamificationBaseUrl` and the other optional fields shown commented-out above are instead set in your Remote Config JSON — see [Configuration Reference](#configuration-reference) below, and [Configure Firebase — Step 3](https://docs.capillarytech.com/docs/configure-firebase-web#step-3-set-up-remote-config).

## Usage notes

* **Page views:** Call `trackPageView()` on route changes. No arguments = auto-captures current URL and title.
* **User identity:** Use `USER_REGISTER` for both login and signup. Use `USER_UPDATE` only for profile updates. Call `reset()` on logout.
* **`getAnonymousId()`:** Returns the backend-assigned anonymous visitor ID (`string | null`). Available regardless of auth state.
* **User consent:** When `disableTracking()` is called, new events are dropped. Queued events resume on `enableTracking()`. Persist the consent decision in your own storage and restore it on app load.
* **Loyalty embeds:** If gamification is enabled and the Capillary team has configured loyalty embed URLs, place `<div id="{embedId}"></div>` elements in your HTML wherever embeds should appear — the `embedId` value is provided by the Capillary team. After login, call `setCapToken('your-token')` with the short-lived Capillary token; the SDK appends it to every loyalty iframe URL and persists it in IndexedDB. Call `setCapToken` again whenever the token refreshes. Token is cleared automatically on `reset()`.

## Replacing placeholders

Once your service file is in place, replace every placeholder with your actual credentials.

*If direct-config bootstrap:*

| Placeholder     | Where to get it                |
| --------------- | ------------------------------ |
| `MY_ACCOUNT_ID` | Provided by the Capillary team |
| `MY_BASE_URL`   | Provided by the Capillary team |
| `MY_ORG_ID`     | Provided by the Capillary team |

*If Remote Config bootstrap, or push notifications are enabled* — also fill in the SDK service file (`MY_*`) and, if push notifications are enabled, the service worker file (`YOUR_*`) too:

| Placeholder                                 | Where to get it                                                                                         |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `MY_FIREBASE_API_KEY` / `YOUR_API_KEY_HERE` | Firebase Console → Project Settings → General                                                           |
| `MY_PROJECT_ID` / `YOUR_PROJECT_ID`         | Firebase Console → Project Settings → General                                                           |
| `MY_SENDER_ID` / `YOUR_SENDER_ID`           | Firebase Console → Project Settings → Cloud Messaging                                                   |
| `MY_APP_ID` / `YOUR_APP_ID`                 | Firebase Console → Project Settings → General                                                           |
| `MY_MEASUREMENT_ID` / `YOUR_MEASUREMENT_ID` | Firebase Console → Project Settings → General (optional)                                                |
| `MY_REMOTE_CONFIG_KEY`                      | The parameter key you created in Firebase Remote Config (Remote Config bootstrap only)                  |
| `MY_VAPID_KEY`                              | Firebase Console → Project Settings → Cloud Messaging → Web Push certificates (push notifications only) |

> When push notifications are enabled, the service worker and the SDK service file use the **same** Firebase credentials — fill them in identically in both places.

If you selected Remote Config bootstrap, or push notifications, complete [Firebase setup](https://docs.capillarytech.com/docs/configure-firebase-web) next. Otherwise, you're done with setup — skip to [Validation & Smoke Testing](https://docs.capillarytech.com/docs/web-sdk-troubleshooting).

# Rules to enforce

* `HydraSDK.initialize()` **must** be called at module load time (top level of the file). Never inside `useEffect`, `ngOnInit`, `mounted()`, or any async lifecycle hook.
* Components **must never** import `HydraSDK` directly. All calls should go through your service.
* Do **not** re-identify the user on page refresh. The SDK persists user context in IndexedDB.
* Do **not** add `await` to SDK calls. All methods are fire-and-forget.
* Do **not** add `isInitialized()` guards. The SDK queues calls internally until ready.

# Configuration Reference

`HydraSDK.initialize()` supports two bootstrap modes, selected by whether `remoteConfigKey` is present.

## Required fields - direct-config bootstrap (default, no Firebase)

| Field       | Type     | Description                            |
| ----------- | -------- | -------------------------------------- |
| `accountId` | `string` | Organization account identifier        |
| `baseURL`   | `string` | API base URL for all SDK requests      |
| `orgId`     | `string` | Organization ID for API authentication |

Omit `firebaseConfig`/`remoteConfigKey` entirely in this mode. No Firebase project is required unless `notifications` is also configured.

## Required fields - Remote Config bootstrap (alternative)

| Field             | Type             | Description                                              |
| ----------------- | ---------------- | -------------------------------------------------------- |
| `firebaseConfig`  | `FirebaseConfig` | Firebase project configuration from the Firebase Console |
| `remoteConfigKey` | `string`         | The parameter key name set in Firebase Remote Config     |

## Optional fields (either mode)

| Field         | Type       | Default                                   | Description                                |
| ------------- | ---------- | ----------------------------------------- | ------------------------------------------ |
| `appVersion`  | `string`   | —                                         | Host app version string for event metadata |
| `retryDelays` | `number[]` | `[60000, 120000, 240000, 480000, 900000]` | Custom retry delays in milliseconds        |

## Remote Config fields - Remote Config bootstrap only (do NOT set manually in `initialize()`)

In direct-config bootstrap, pass these same fields directly in `initialize()` instead — `accountId`/`baseURL`/`orgId` are required there (see table above), everything else keeps the same defaults.

| Field                   | Required | Default   | Description                                                                                                                   |
| ----------------------- | -------- | --------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `accountId`             | Yes      | —         | Organization account identifier                                                                                               |
| `baseURL`               | Yes      | —         | API base URL for all SDK requests                                                                                             |
| `orgId`                 | Yes      | —         | Organization ID for API authentication                                                                                        |
| `source`                | No       | `WEBPUSH` | Source identifier for visitor profiles                                                                                        |
| `channelType`           | No       | `web`     | Communication channel type                                                                                                    |
| `sessionTimeoutMinutes` | No       | `30`      | Session inactivity timeout in minutes                                                                                         |
| `batchSize`             | No       | `50`      | Max events per batch request                                                                                                  |
| `debugLevel`            | No       | `NONE`    | Logging level: `NONE` / `ERROR` / `WARN` / `INFO` / `DEBUG` / `VERBOSE`                                                       |
| `gamificationWriteKey`  | Yes\*    | —         | Gamification write key. **Required to enable gamification.** Obtain from the Capillary team.                                  |
| `gamificationRegion`    | Yes\*    | —         | Gamification region code (e.g. `'us'`, `'me'`). **Required to enable gamification.** Derives the API base URL automatically.  |
| `gamificationBaseUrl`   | Yes\*    | —         | The gamification API base URL for your region (e.g. `'https://api-us.customerglu.com'`). **Required to enable gamification.** |

<Callout icon="📘" theme="info">
  ### Note

  `gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` are all required together for gamification features to work. Omit all three only if gamification is not being used. See [Configure Gamification](https://docs.capillarytech.com/docs/gamification-web).
</Callout>