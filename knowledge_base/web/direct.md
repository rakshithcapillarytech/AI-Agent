---
platform: web
config_mode: direct
sdk_package: cap-hydra-web-sdk
sdk_version: null   # the direct-mode guide pins no version: `cap-hydra-web-sdk` (no tag), or `@beta` for UAT (p.62)
modules_covered: [core, push, visitor, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, multi_account]
sources: ["Integration document _ Experience+ pp.60–71 (WEB Hydra SDK – Integration Guide, Firebase excluded)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# Web (without Firebase)

Capillary values go straight into `HydraSDK.initialize()`; no Remote Config. Firebase is used only for optional web push.

## Coverage
| Module | Status |
|---|---|
| Core: init, identify, profile update, sign-out, events, page views, consent, CSP | Documented |
| Gamification: automatic campaigns, Banner / Embedded / Loyalty views | Documented |
| Push | Optional, brief |
| Visitor | Partial: `getAnonymousId()`, `getUser()` |
| In-App, Inbox, Multi-account | Not documented for Web |

## Requirements
- `cap-hydra-web-sdk` from npm; `@beta` for UAT (step 1).

> ⚠️ Gap: no SDK version, browser list or Node.js / bundler / framework requirements are given for this mode (the Firebase-mode guide has a gamification minimum version, p.8, and a browser table, p.16; see `web/firebase.md`). Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md`. Register the app with the Capillary team, who provide: Account ID → `accountId`, Base URL → `baseURL`, Org ID → `orgId`, Gamification Base URL → `gamificationBaseUrl`, Gamification Key (writeKey) → `gamificationWriteKey`, Gamification Region → `gamificationRegion`.

Only if used:
- **Banner / Embedded View:** `hookId`, configured per entry point in the gamification dashboard.
- **Loyalty View:** `embedId` from the Capillary team, and a Capillary B2B short-lived token, set after login (how to obtain it isn't documented; see `_shared/prerequisites.md`).
- **Web push:** the client's Firebase web config, a VAPID key generated in the Firebase Console, and `firebase-messaging-sw.js` at the site root.

> ⚠️ Gap: not documented: what the client sends to register a web app, the allowed region values (the Firebase-mode guide uses lowercase `"us"`, `"me"`, `"in"`, p.9), and whether the `identify()` identifier must match the CRM Account Linking Identifier. Ask a Capillary engineer.

## Steps

### 1. Install the SDK
```shell
npm install cap-hydra-web-sdk
```

For UAT, use the beta package:

```shell
npm install cap-hydra-web-sdk@beta
```

### 2. Initialise once, at module load
Call `HydraSDK.initialize()` **exactly once at module load time**, not inside lifecycle hooks such as `useEffect`, `ngOnInit` or similar.

```js
import { HydraSDK } from 'cap-hydra-web-sdk';

HydraSDK.initialize({
  accountId: '{{account_id}}',
  baseURL: '{{base_url}}',
  orgId: '{{org_id}}',
  gamificationBaseUrl: '{{gamification_base_url}}',
  gamificationWriteKey: '{{gamification_key}}',
  gamificationRegion: '{{gamification_region}}',
});
```

- `gamification*` fields: only for gamification. Optional fields: API Reference.
- Don't pass `firebaseConfig` or `remoteConfigKey`; omitting them selects this direct configuration. Push: Modules → Push.

> ⚠️ Correction: ✅ Use a comma after the `gamificationBaseUrl` line, as above. ❌ Don't use the source sample without it (p.62); it is a JavaScript syntax error. *Pending SME confirmation.*

### 3. Identify the user at sign-in
Call `HydraSDK.identify()` at sign-in with `actionType: 'USER_REGISTER'` (the source uses it "for both cases": sign-in and sign-up). Shape (TypeScript notation, not runnable as-is):

```ts
HydraSDK.identify({
  identifier: { type: 'email' | 'mobile' | 'externalId', cuid: <corresponding value> },
  actionType: 'USER_REGISTER',
  traits: {
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
});
```

`cuid` is the user's value for the identifier type; `traits` are optional. Minimal call (`cuid` holds the user's email):

```js
HydraSDK.identify({
  identifier: { type: 'email', cuid },
  actionType: 'USER_REGISTER',
});
```

### 4. Update the profile (optional)
Same call as step 3 with `actionType: 'USER_UPDATE'`. Use `USER_UPDATE` only for profile updates, never at sign-in.

### 5. Reset on sign-out
Clears the identity, persisted user context and any cap token; tracking returns to anonymous.

```js
HydraSDK.reset();
```

### 6. Track custom events
General form: `HydraSDK.track(EVENT_NAME, {...ATTRIBUTES})`.

```js
HydraSDK.track('add_to_cart', {
  productId: 'SKU-123',
  quantity: 2,
});
```

> ⚠️ Correction: ✅ Use `HydraSDK.track(...)` and `HydraSDK.pageView(...)`. ❌ Don't use `WebSDK.track(...)` / `WebSDK.pageView(...)` (event and page-view examples, pp.64–65); `WebSDK` is never imported. *Pending SME confirmation.*

### 7. Track page views (optional)
With no arguments, the SDK captures the current URL and page title:

```js
HydraSDK.pageView();
```

Options (TypeScript signature, not a call):

```ts
HydraSDK.pageView(options?: {
  url?: string;
  title?: string;
  category?: string;
  properties?: Record<string, unknown>;
});
```

### 8. Wire up cookie consent (optional)
```js
// When user grants consent
HydraSDK.enableSDK();

// When user revokes consent
HydraSDK.disableSDK();
```

### 9. Allowlist the SDK's domains in the CSP (if the site has one)
**Add these to the existing directives; don't replace them.**

| Directive | Entries |
|---|---|
| `connect-src` | `https://*.capillarytech.com`; `https://*.googleapis.com`, `https://*.firebaseio.com`, `https://*.firebaseapp.com` (only if using Remote Config or push notifications); `https://*.posthog.com` |
| `script-src` | `'self'`; `https://*.gstatic.com` (push notifications only); `https://*.posthog.com` |
| `frame-src` | `https://*.capillarytech.com` |
| `img-src` | `https://*.capillarytech.com` |
| `worker-src` | `'self'`; `blob:`; `data:` |

Example:

```text
connect-src 'self' https://*.capillarytech.com https://*.googleapis.com https://*.firebaseio.com https://*.firebaseapp.com https://*.posthog.com;
script-src 'self' https://*.gstatic.com https://*.posthog.com;
frame-src 'self' https://*.capillarytech.com;
img-src 'self' https://*.capillarytech.com;
worker-src 'self' blob: data:;
```

Without Remote Config or push notifications, only the `capillarytech.com` and `posthog.com` entries are needed.

## Modules

### Push
Optional. Pass a Firebase **Messaging instance** in the `notifications` block of `initialize()` (`HydraSDK` imported as in step 2):

```js
import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";

const firebaseApp = initializeApp(
  { apiKey: "MY_FIREBASE_API_KEY", /* ...rest of Firebase config */ },
  "hydra-fcm",
);

HydraSDK.initialize({
  accountId: '{{account_id}}',
  baseURL: '{{base_url}}',
  orgId: '{{org_id}}',
  notifications: {
    vapidKey: '<VAPID_KEY>',
    serviceWorkerPath: '/firebase-messaging-sw.js',
    messaging: getMessaging(firebaseApp),
  },
});
```

- `firebase-messaging-sw.js` must be deployed at the **site root**.
- The VAPID key must be generated in the Firebase Console.
- `initialize()` is still called only once (step 2). Push needs the Firebase / `gstatic.com` CSP entries (step 9).

> ⚠️ Gap: p.62 says to put `firebaseConfig` in `notifications`; p.67 (followed above) passes a Messaging instance. Also undocumented: the `firebase` npm package, where `firebase-messaging-sw.js` comes from, combining push with gamification fields, and test pushes. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Visitor
Tracking is anonymous before `identify()` and after `reset()`. The `source` field defaults to `WEBPUSH`.

```js
// Returns anonymous ID (safe to call at any time)
const anonymousId = HydraSDK.getAnonymousId();

// Returns full anonymous user object (throws if user is already identified)
const user = HydraSDK.getUser();
```

### Gamification
Disabled by default. It activates only when both `gamificationWriteKey` and `gamificationRegion` are passed to `initialize()`; if either is missing, it is silently skipped and the rest of the SDK is unaffected.

> ⚠️ Gap: the configuration reference (p.69) marks all three `gamification*` fields "Required: Yes" (`gamificationBaseUrl` as an "Override"), but p.65 says gamification is optional and activates with the write key and region. Ask a Capillary engineer.

- Content renders automatically after `HydraSDK.identify()`; no separate start call.
- Eligibility uses the current page URL and include/exclude path rules (exact URL, wildcard or regex-literal) that the Capillary team configures per entry point in the dashboard.
- SPA navigation is handled: the SDK watches URL changes via `MutationObserver` and re-evaluates display rules on every route change.

**Automatic campaigns (no code)**, appended to `document.body`:

| Campaign type | Behaviour |
|---|---|
| Floating Button | Fixed button (bottom-left) that slides up; tapping it opens a chat panel |
| Popup | Centred full-page modal with a semi-transparent backdrop |
| Bottom Sheet | Sheet that slides up from the bottom of the screen, with a backdrop |

**Inline components:** add a `<div>` with the matching `id`. The SDK renders into it as soon as it appears in the DOM (safe for SPA routes that mount later).

```html
<!-- Banner View: hookId configured per entry point in the gamification dashboard -->
<div id="{{banner_id}}"></div>

<!-- Embedded View: hookId configured per entry point in the gamification dashboard -->
<div id="{{embed_id}}"></div>

<!-- Loyalty View: embedId provided by the Capillary team; needs a cap token (below) -->
<div id="{{loyalty_id}}"></div>
```

**Loyalty View token:** set the Capillary B2B short-lived token after login, before the view renders. `reset()` clears it. The SDK appends it as `?capToken=<value>` to every loyalty iframe URL.

```js
HydraSDK.setCapToken('<CAP_TOKEN>');
```

To retrieve the current token:

```js
const token = HydraSDK.getCapToken();
```

## Verification
- `HydraSDK.getAnonymousId()` returns the anonymous visitor ID (safe at any time).
- `HydraSDK.getUser()` returns the anonymous user object before `identify()` and throws after (expected).
- Logging: set `debugLevel` (default `NONE`).
- Gamification: after `identify()`, campaigns appear on pages matching the path rules, and inline placeholders get content.
- `HydraSDK.getCapToken()` returns the token you set.

> ⚠️ Gap: no expected log lines, init-success callback, `debugLevel` values (the Firebase-mode guide lists `NONE` / `ERROR` / `WARN` / `INFO` / `DEBUG`, p.22) or dashboard / test-push check is documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| `initialize()` inside `useEffect` / `ngOnInit`, or called twice | Must be called exactly once at module load | Call it at the top level of a module loaded at app start |
| Direct config ignored | `firebaseConfig` or `remoteConfigKey` passed | Remove them; push uses `notifications` |
| Gamification never appears | Write key or region missing (no error); user not identified; URL doesn't match path rules | Check each |
| `getUser()` throws | User already identified | Use only before `identify()`; `getAnonymousId()` is always safe |
| Wrong `actionType` | `'USER_UPDATE'` at sign-in | `'USER_REGISTER'` at sign-in / sign-up |
| Loyalty View empty | No token before render, or cleared by `reset()` | `setCapToken` after each login, before render |
| SDK requests, iframes or workers blocked | Domains not in the CSP | Add the step 9 entries |
| Web push fails | Service worker not at site root, or VAPID key not from the Firebase Console | Modules → Push |

> ⚠️ Gap: this guide doesn't cover re-identifying on refresh, events while disabled, consent or cap-token persistence, or browser limits; `web/firebase.md` covers them for Firebase mode (pp.10, 16, 20). Ask a Capillary engineer whether they apply here.

## API Reference
| Method | When to call |
|---|---|
| `HydraSDK.initialize(config)` | Once at module load time |
| `HydraSDK.identify(params)` | Sign-in, sign-up (`USER_REGISTER`) or profile update (`USER_UPDATE`). `params`: `{ identifier: { type, cuid }, actionType, traits? }` |
| `HydraSDK.reset()` | On sign-out |
| `HydraSDK.track(event, props?)` | Custom behavioural events |
| `HydraSDK.pageView(options?)` | Page views |
| `HydraSDK.setCapToken(token)` / `getCapToken()` | Set after login (Loyalty View) / read the current token |
| `HydraSDK.enableSDK()` / `disableSDK()` | User grants / revokes consent (GDPR) |
| `HydraSDK.getAnonymousId()` | Anonymous visitor ID |
| `HydraSDK.getUser()` | Anonymous user object (pre-identify only) |

**`initialize()` fields** (Required / Default / Description, as in the source):

| Field | Req. | Default | Description |
|---|---|---|---|
| `accountId` | Yes | — | Your unique account identifier |
| `baseURL` | Yes | — | API base endpoint |
| `orgId` | Yes | — | Your organisation identifier |
| `gamificationWriteKey` | Yes\* | — | Gamification write key |
| `gamificationRegion` | Yes\* | — | Region value |
| `gamificationBaseUrl` | Yes\* | — | Override for gamification API base URL |
| `brandId` | No | — | Brand identifier |
| `applicationId` | No | — | Application identifier |
| `source` | No | `WEBPUSH` | Source channel |
| `channelType` | No | `web` | Channel type |
| `sessionTimeoutMinutes` | No | `30` | Session timeout in minutes |
| `batchSize` | No | `50` | Event batch size |
| `debugLevel` | No | `NONE` | Debug log level |
| `notifications` | Push | — | `{ vapidKey, serviceWorkerPath, messaging }` (not in the source's table) |
| `firebaseConfig`, `remoteConfigKey` | Never | — | Omit them to use direct configuration |

\* As the source's table states; see the gap under Modules → Gamification.

> ⚠️ Gap: not documented: who supplies `brandId` / `applicationId`; `birthday` / `timezone` formats and `gender` values; whether `getAnonymousId()` / `getUser()` return a value or a Promise, and the user object's properties. Ask a Capillary engineer.
