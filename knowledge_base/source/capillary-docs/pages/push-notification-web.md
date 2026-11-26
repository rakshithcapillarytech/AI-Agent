---
updatedAt: 2026-11-17T07:26:50.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Push Notifications

This page provides you with information on push notifications and how to configure them.

Capillary Web SDK sends browser-based push notifications using [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging/) (FCM).

# Prerequisites

* A Firebase project — see [Configure Firebase](https://docs.capillarytech.com/docs/configure-firebase-web)
* A VAPID key generated under **Project Settings → Cloud Messaging → Web Push certificates** in the Firebase Console

The SDK never calls Firebase's `initializeApp()`/`getMessaging()` itself. You create the Firebase app and Messaging instance yourself and pass the instance in via `notifications.messaging` when calling `HydraSDK.initialize()`.

# Configuring push notifications

Add the `notifications` block to your `initialize()` call, alongside your other configuration (direct-config bootstrap shown; the same block applies unchanged in Remote Config bootstrap):

```typescript
import { HydraSDK } from "cap-hydra-web-sdk";
import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";

// An app name is given explicitly so this never collides with any other Firebase
// app your code initializes elsewhere:
const firebaseApp = initializeApp(
  { apiKey: "MY_FIREBASE_API_KEY", /* ...rest of Firebase config */ },
  "hydra-fcm",
);

HydraSDK.initialize({
  accountId: "MY_ACCOUNT_ID",
  baseURL: "MY_BASE_URL",
  orgId: "MY_ORG_ID",
  notifications: {
    messaging: getMessaging(firebaseApp),
    vapidKey: "MY_VAPID_KEY",
    serviceWorkerPath: "/firebase-messaging-sw.js",
  },
});
```

See [Initialise SDK](https://docs.capillarytech.com/docs/web-sdk-initialisation) for the full service file, including the Remote Config bootstrap variant.

## `serviceWorkerPath`

Set `serviceWorkerPath` based on your app's URL:

| App served at                 | `serviceWorkerPath` value            |
| ----------------------------- | ------------------------------------ |
| `https://example.com/`        | `"/firebase-messaging-sw.js"`        |
| `https://example.com/my-app/` | `"/my-app/firebase-messaging-sw.js"` |

<Callout icon="📘" theme="info">
  ### Note

  The service worker **must** be served from a path the browser can reach at the root scope of your app.
</Callout>

# Creating the service worker file

The service worker handles background push notifications, action buttons, CTAs, and delivery receipts (DLR tracking).

1. Create a file named `firebase-messaging-sw.js` in your project's `public/` directory (or the equivalent static-asset directory served at the site root).
2. Paste the full content from [Service Worker File](#service-worker-file) below.
3. Replace the placeholder Firebase config inside the file with your actual credentials (same values as your SDK service file). Leave the `YOUR_*` placeholders in place until you have your credentials.
4. Do **not** rename the file. It must be `firebase-messaging-sw.js`.
5. If your project has no `public/` directory, use the correct static-asset root instead (e.g. `static/`, `assets/`, or your bundler's configured public path).
6. Do **not** modify the service worker logic — only the Firebase config block is meant to change.

# Service Worker File

Copy this entire file into `public/firebase-messaging-sw.js` and replace the `YOUR_*` placeholders in the Firebase config block with your real credentials.

```javascript
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

## Service Worker Notes

* **Default icons:** The worker falls back to `/logo192.png` for icon and badge. Make sure that file exists in your `public/` directory, or change the fallback paths.
* **Firebase version:** The worker loads Firebase `10.7.1` via `importScripts`. Keep this aligned with the SDK's expected Firebase version unless told otherwise by the Capillary team.

# Browser Support Matrix

**Internet Explorer is not supported.**

| Browser         | Minimum Version | Push Notifications |
| --------------- | --------------- | ------------------ |
| Chrome          | 109+            | Supported          |
| Firefox         | 140+ (ESR)      | Supported          |
| Safari          | 26.3+           | Supported          |
| Edge (Chromium) | 149+            | Supported          |

For push notification troubleshooting (service worker not registering, notifications missing a body, DLR events not recorded), see [Validation, Troubleshooting & Rollback](https://docs.capillarytech.com/docs/web-sdk-troubleshooting).

<br />