---
platform: web
config_mode: direct
sdk_package: cap-hydra-web-sdk
sdk_version: null   # the direct-mode guide pins no version: it installs `cap-hydra-web-sdk` (no tag) or `cap-hydra-web-sdk@beta` for UAT (p.62)
modules_covered: [core, push, visitor, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, multi_account]
sources: ["Integration document _ Experience+ pp.60–71 (WEB Hydra SDK – Integration Guide, Firebase excluded)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# Web (without Firebase)

In this mode the Capillary values are passed straight into `HydraSDK.initialize()`. There's no Firebase Remote Config. Firebase is used only if the client opts into web push (Modules → Push).

## Coverage
| Module | Status in this mode |
|---|---|
| Core (init, identify, profile update, sign-out, custom events, page views, cookie consent) | Documented |
| Gamification (automatic campaigns, Banner, Embedded, Loyalty views) | Documented |
| Push (web push) | Optional, briefly documented. Needs a Firebase Messaging instance, a VAPID key and `firebase-messaging-sw.js` at the site root |
| Visitor (anonymous) | Partial: `getAnonymousId()` and `getUser()` lookups |
| Content Security Policy (CSP) | Documented (step 9) |
| In-App messaging | Not documented for Web |
| Inbox / Notification Center | Not documented for Web |
| Multi-account | Not documented for Web |

## Requirements
- Package: `cap-hydra-web-sdk` from npm (step 1). For UAT the source uses the `@beta` tag.

> ⚠️ Gap: the direct-mode guide gives no version number or minimum version, no browser-support list and no Node.js / bundler / framework requirements. For the same package, the Firebase-mode gamification guide states a minimum version for gamification (p.8), and the Firebase-mode runbook has a browser-support table (p.16); both are in `web/firebase.md`. Confirm whether they apply to this mode. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange. For this platform and mode:

- **Register the app with the Capillary team** (p.61).
  > ⚠️ Gap: the guide doesn't say what the client must provide to register a web app. Ask a Capillary engineer.
- **Capillary gives client** (p.61). Each value goes into `HydraSDK.initialize()` (step 2):

  | Value | `initialize()` field | Description in the source |
  |---|---|---|
  | Account ID | `accountId` | Your unique account identifier |
  | Base URL | `baseURL` | API base endpoint |
  | Org ID | `orgId` | Your organisation identifier |
  | Gamification Base URL | `gamificationBaseUrl` | Base URL for gamification services |
  | Gamification Key | `gamificationWriteKey` | writeKey for gamification |
  | Gamification Region | `gamificationRegion` | region value |

  > ⚠️ Gap: the guide doesn't list the allowed region values or their case. `_shared/prerequisites.md` lists `IN`, `US`, `ME`; the Firebase-mode web guide's example uses lowercase `"us"`, `"me"`, `"in"` (p.9). Ask a Capillary engineer.
- **Gamification inline views (optional):** the Banner and Embedded View `hookId`s are configured per entry point in the gamification dashboard. The Loyalty View `embedId` comes from the Capillary team (pp.66–67).
- **Loyalty View:** the client's backend provides a Capillary B2B short-lived token after login (p.68).
- **Web push (optional):** the client's own Firebase web config, a VAPID key generated in the Firebase Console, and `firebase-messaging-sw.js` deployed at the site root (p.67).

> ⚠️ Gap: the web guide doesn't say whether the identifier sent to `identify()` must match the CRM Account Linking Identifier described in `_shared/prerequisites.md` (documented there for the `MAPP_SDK` channel). Ask a Capillary engineer.

## Steps

### 1. Install the SDK
```shell
npm install cap-hydra-web-sdk
```

For UAT, the source says to use the beta package:

```shell
npm install cap-hydra-web-sdk@beta
```

### 2. Initialise the SDK once, at module load
Call `HydraSDK.initialize()` **exactly once at module load time**. Don't call it inside lifecycle hooks such as `useEffect`, `ngOnInit` or similar.

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

The three `gamification*` fields are for gamification (Modules → Gamification). Optional fields (`brandId`, `applicationId`, `source`, `channelType`, `sessionTimeoutMinutes`, `batchSize`, `debugLevel`) are listed under API Reference.

> ⚠️ Source doc correction: the source sample (p.62) has no comma after `gamificationBaseUrl : '<GAMIFICATION_BASE_URL>'`, which is a JavaScript syntax error, vs the corrected sample above with the comma added. *Pending SME confirmation.*

> **Important:** don't pass anything to `firebaseConfig` or `remoteConfigKey`. Omitting them tells the SDK to use the directly supplied configuration. For push, see Modules → Push.

### 3. Identify the user at sign-in
Call `HydraSDK.identify()` when the user signs in, with `actionType: 'USER_REGISTER'`. The source says to use `USER_REGISTER` "for both cases" without naming them. Its methods summary (p.70) lists `identify()` for sign-in, sign-up and profile update, and profile update uses `USER_UPDATE` (step 4), so the two cases are sign-in and sign-up.

The shape from the source (p.63). It is written in TypeScript type notation, so it isn't runnable as-is:

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

- `identifier.type`: one of `'email'`, `'mobile'`, `'externalId'`.
- `identifier.cuid`: the user's value for that type.
- `traits`: optional.

A minimal call that follows the shape above (traits omitted; `userEmail` is the app's own variable):

```js
HydraSDK.identify({
  identifier: { type: 'email', cuid: userEmail },
  actionType: 'USER_REGISTER',
});
```

> ⚠️ Gap: the source doesn't give the expected formats for `birthday` or `timezone`, or the allowed values for `gender`. Ask a Capillary engineer.

### 4. Update the user's profile (optional)
To update user details after sign-in, call `HydraSDK.identify()` with the same shape as step 3, but with `actionType: 'USER_UPDATE'`. `traits` are optional (pp.63–64).

### 5. Reset on sign-out
Call `HydraSDK.reset()` when the user signs out. It clears the identity, the persisted user context and any cap token, and returns tracking to anonymous (p.64):

```js
HydraSDK.reset();
```

> ⚠️ Gap: the direct guide doesn't say whether to call `identify()` again on page refresh. The Firebase-mode runbook says **not** to, because the SDK persists user context in IndexedDB (`web/firebase.md`, step 8). This guide's mention of "persisted user context" suggests the same behaviour. Ask a Capillary engineer to confirm.

### 6. Track custom events
General form: `HydraSDK.track(EVENT_NAME, {...ATTRIBUTES})`. Example (p.64):

```js
HydraSDK.track('add_to_cart', {
  productId: 'SKU-123',
  quantity: 2,
});
```

> ⚠️ Source doc correction: the event and page-view examples (pp.64–65) call `WebSDK.track(...)` and `WebSDK.pageView(...)` vs `HydraSDK`, the name the guide imports (p.62) and uses in its methods summary (p.70). `WebSDK` is never imported. Use `HydraSDK.track` / `HydraSDK.pageView`. *Pending SME confirmation.*

### 7. Track page views (optional)
`HydraSDK.pageView(options?)`. Called without arguments, the SDK captures the current URL and page title automatically (p.65):

```js
HydraSDK.pageView();
```

The options the source gives (p.65; this is a TypeScript signature, not a call):

```ts
HydraSDK.pageView(options?: {
  url?: string;
  title?: string;
  category?: string;
  properties?: Record<string, unknown>;
});
```

### 8. Wire up cookie consent (optional)
Connect these to the app's consent flow (p.68):

```js
// When user grants consent
HydraSDK.enableSDK();

// When user revokes consent
HydraSDK.disableSDK();
```

> ⚠️ Gap: the direct guide doesn't say what happens to events while the SDK is disabled, or whether the consent state survives a reload. The Firebase-mode runbook (`web/firebase.md`, step 9) says new events are dropped, queued events are kept and sent when re-enabled, and the app should persist and restore the consent decision itself. Ask a Capillary engineer to confirm this applies here.

### 9. Allowlist the SDK's domains in your Content Security Policy (if the site has one)
If the app uses a CSP, allowlist these domains so the SDK works. **Add them to the existing directives rather than replacing them** (pp.70–71).

**`connect-src`**
- `https://*.capillarytech.com`
- `https://*.googleapis.com` (only if using Remote Config or push notifications)
- `https://*.firebaseio.com` (only if using Remote Config or push notifications)
- `https://*.firebaseapp.com` (only if using Remote Config or push notifications)
- `https://*.posthog.com`

**`script-src`**
- `'self'`
- `https://*.gstatic.com` (push notifications only)
- `https://*.posthog.com`

**`frame-src`**
- `https://*.capillarytech.com`

**`img-src`**
- `https://*.capillarytech.com`

**`worker-src`**
- `'self'`
- `blob:`
- `data:`

Example CSP configuration (p.71):

```text
connect-src 'self' https://*.capillarytech.com https://*.googleapis.com https://*.firebaseio.com https://*.firebaseapp.com https://*.posthog.com;
script-src 'self' https://*.gstatic.com https://*.posthog.com;
frame-src 'self' https://*.capillarytech.com;
img-src 'self' https://*.capillarytech.com;
worker-src 'self' blob: data:;
```

If the app already has CSP directives, add these domains to the existing values rather than replacing them. If the app doesn't use Remote Config or push notifications, it only needs the `capillarytech.com` and `posthog.com` entries.

> ⚠️ Gap: the guide doesn't say whether `worker-src 'self' blob: data:` is still needed without push (it has no `capillarytech.com` or `posthog.com` entry). Ask a Capillary engineer.

## Modules

### Push
Optional (p.67). If the client uses web push, create a Firebase app and pass its **Messaging instance** inside the `notifications` block of `initialize()`:

```js
import { HydraSDK } from 'cap-hydra-web-sdk';
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

`initialize()` is called exactly once (step 2). If the client also uses gamification, the `gamification*` fields go in this same call; the source doesn't show the two combined.

**Requirements** (p.67):
- `firebase-messaging-sw.js` must be deployed at the **site root**.
- The VAPID key must be generated in the Firebase Console.

CSP (step 9): push needs the `googleapis.com`, `firebaseio.com` and `firebaseapp.com` `connect-src` entries and the `gstatic.com` `script-src` entry.

> ⚠️ Source doc correction: the initialisation note (p.62) says to supply `firebaseConfig` inside the `notifications` block, vs the push section (p.67), whose text and example pass a Firebase **Messaging instance** (`messaging: getMessaging(firebaseApp)`) and no `firebaseConfig`. The example above follows p.67. *Pending SME confirmation.*

> ⚠️ Gap: the guide doesn't say how to install the `firebase` npm package (or which version) that `firebase/app` and `firebase/messaging` come from. It also doesn't say where `firebase-messaging-sw.js` comes from or what it contains, how to handle apps served from a sub-path, when the SDK asks for notification permission, or how to send a test push. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for Web. Ask a Capillary engineer.

### Visitor
Before a user is identified (and after `reset()`), tracking is anonymous. To look up the anonymous visitor (p.68):

```js
// Returns anonymous ID (safe to call at any time)
const anonymousId = HydraSDK.getAnonymousId();

// Returns full anonymous user object (throws if user is already identified)
const user = HydraSDK.getUser();
```

The `source` init field ("Source channel") defaults to `WEBPUSH`.

> ⚠️ Gap: the return types of `getAnonymousId()` and `getUser()` (a value or a Promise) and the properties of the anonymous user object aren't documented. Ask a Capillary engineer.

### Gamification
**Activation** (p.65): gamification is **disabled by default**. It activates only when both `gamificationWriteKey` and `gamificationRegion` are passed in the `initialize()` config (step 2). If either is missing, the module is silently skipped and the rest of the SDK is unaffected.

> ⚠️ Source doc correction: the configuration reference (p.69) marks `gamificationWriteKey`, `gamificationRegion` and `gamificationBaseUrl` as **Required: Yes**, and describes `gamificationBaseUrl` as an "Override". That conflicts with p.65, where gamification is optional and needs only the write key and region: the fields are required only to enable gamification, and `gamificationBaseUrl` is not needed to activate it. *Pending SME confirmation.*

**How it works** (p.65):
- Once enabled, gamification content renders automatically after `HydraSDK.identify()` is called. No separate "start gamification" call is needed.
- Campaign eligibility is evaluated against the current page URL. Include/exclude path rules are configured per entry point in the gamification dashboard (exact URL, wildcard or regex-literal formats).
- SPA navigation is handled automatically. The SDK watches for URL changes via `MutationObserver` and re-evaluates display rules on every route change. The host app needs no route-change code.
- The Capillary team configures the path rules per entry point in the dashboard; the host app doesn't.

**Automatic campaigns (no code required)** (p.66). The SDK appends these to `document.body` automatically; no placeholder elements or extra code are needed:

| Campaign type | Behaviour |
|---|---|
| Floating Button | Fixed button (bottom-left) that slides up; tapping it opens a chat panel |
| Popup | Centred full-page modal with a semi-transparent backdrop |
| Bottom Sheet | Sheet that slides up from the bottom of the screen, with a backdrop |

**Inline components (need a placeholder `<div>`)** (pp.66–67). Add a `<div>` with the matching `id` in the HTML. The SDK watches the DOM and renders into the element as soon as it appears. The element doesn't need to exist at page load, so this is safe for SPA routes that mount later.

```html
<!-- Banner View: hookId configured per entry point in the gamification dashboard -->
<div id="{{banner_id}}"></div>

<!-- Embedded View: hookId configured per entry point in the gamification dashboard -->
<div id="{{embed_id}}"></div>

<!-- Loyalty View: embedId provided by the Capillary team; needs a cap token (below) -->
<div id="{{loyalty_id}}"></div>
```

**Loyalty embeds: the Capillary token** (p.68). Loyalty View needs a valid Capillary token. Set the Capillary B2B short-lived token after login, before the view is expected to render:

```js
HydraSDK.setCapToken('<CAP_TOKEN>');
```

To retrieve the current token:

```js
const token = HydraSDK.getCapToken();
```

The token is appended automatically as `?capToken=<value>` to every loyalty iframe URL. `HydraSDK.reset()` clears it (p.64), so set it again after the next login.

> ⚠️ Gap: the direct guide doesn't say whether the token persists across page reloads, or whether to set it again when it's refreshed. The Firebase-mode gamification guide (`web/firebase.md`, Modules → Gamification, G4) says it's persisted in IndexedDB and should be set again whenever it's refreshed. Ask a Capillary engineer to confirm this applies here.

## Verification
What the source supports:
- **SDK running:** after initialisation, `HydraSDK.getAnonymousId()` returns the anonymous visitor ID; the source says it's safe to call at any time (p.68).
- **Anonymous vs identified:** `HydraSDK.getUser()` returns the anonymous user object before `identify()` and throws afterwards, which is expected (p.68).
- **Logging:** set the `debugLevel` init field (default `NONE`, p.69).
  > ⚠️ Gap: the direct guide doesn't list the `debugLevel` values. The Firebase-mode runbook lists `NONE` / `ERROR` / `WARN` / `INFO` / `DEBUG` (`web/firebase.md`, API Reference). Ask a Capillary engineer to confirm.
- **Gamification:** after `identify()`, Floating Button, Popup and Bottom Sheet campaigns appear on pages whose path rules match, and inline placeholders receive content (pp.65–67).
- **Loyalty token:** `HydraSDK.getCapToken()` returns the token you set (p.68).

> ⚠️ Gap: the source has no formal verification procedure. It documents no expected log lines, no init-success callback, and no network, dashboard or test-push check. Ask a Capillary engineer.

## Known Issues

**`HydraSDK.initialize()` called inside `useEffect`, `ngOnInit` or similar, or called more than once**
- Cause: the source requires exactly one call, at module load time.
- Fix: call it once at the top level of a module that loads at app start (step 2).

*From the source doc (p.62).*

**`firebaseConfig` or `remoteConfigKey` passed to `initialize()`**
- Cause: the source says to omit them; omitting them is what tells the SDK to use the directly supplied configuration.
- Fix: remove them. For push, use the `notifications` block (Modules → Push).

*From the source doc (p.62).*

**Gamification never appears**
- Possible causes:
  - `gamificationWriteKey` or `gamificationRegion` is missing from `initialize()`. The module is then silently skipped, with no error, while the rest of the SDK keeps working (p.65).
  - The user hasn't been identified yet: content renders after `identify()` (p.65).
  - The page URL doesn't match the entry point's path rules in the dashboard (p.65).
- Fix: check each cause above.

*From the source doc (p.65).*

**`getUser()` throws an error**
- Cause: the user is already identified. `getUser()` returns the anonymous user object before `identify()` only.
- Fix: use it only before `identify()`. `getAnonymousId()` is safe to call at any time.

*From the source doc (p.68, p.70).*

**Wrong `actionType` on `identify()`**
- Cause: using `'USER_UPDATE'` at sign-in.
- Fix: use `'USER_REGISTER'` at sign-in (and sign-up); use `'USER_UPDATE'` only for profile updates.

*From the source doc (pp.63–64).*

**Loyalty View shows no content**
- Cause: no valid Capillary token was set before the view rendered, or `HydraSDK.reset()` cleared it at sign-out.
- Fix: call `HydraSDK.setCapToken(token)` after each login, before the view renders.

*From the source doc (p.64, pp.67–68).*

**SDK requests, iframes or workers blocked on a site with a CSP**
- Cause: the SDK's domains aren't allowlisted.
- Fix: add the entries from step 9 to the existing directives; don't replace them.

*From the source doc (pp.70–71).*

**Web push not working**
- Cause: `firebase-messaging-sw.js` isn't deployed at the site root, or the VAPID key wasn't generated in the Firebase Console.
- Fix: see Modules → Push.

*From the source doc (p.67).*

> ⚠️ Gap: browser limits (e.g. Safari / IE 11 and Service Worker or Push API support) aren't covered by the direct guide. The Firebase-mode runbook has a browser table (`web/firebase.md`, Requirements). Ask a Capillary engineer to confirm it applies here.

## API Reference

**`HydraSDK` methods** (pp.69–70):

| API | When to call |
|---|---|
| `HydraSDK.initialize(config)` | Once at module load time |
| `HydraSDK.identify(params)` | On sign-in, sign-up or profile update. `params`: `{ identifier: { type: 'email' \| 'mobile' \| 'externalId', cuid }, actionType: 'USER_REGISTER' \| 'USER_UPDATE', traits? }` |
| `HydraSDK.reset()` | On sign-out. Clears identity, persisted user context and the cap token |
| `HydraSDK.track(event, props?)` | To track custom behavioural events |
| `HydraSDK.pageView(options?)` | To track page views. `options`: `url?`, `title?`, `category?`, `properties?` |
| `HydraSDK.setCapToken(token)` | After login, if using Loyalty View |
| `HydraSDK.getCapToken()` | To retrieve the current cap token |
| `HydraSDK.enableSDK()` | When the user grants consent (GDPR) |
| `HydraSDK.disableSDK()` | When the user revokes consent (GDPR) |
| `HydraSDK.getAnonymousId()` | To get the anonymous visitor ID (safe at any time) |
| `HydraSDK.getUser()` | To get the anonymous user object (before identify only; throws afterwards) |

**`initialize()` fields** (p.69):

| Field | Required? | Default | Description |
|---|---|---|---|
| `accountId` | Yes | — | Your unique account identifier |
| `baseURL` | Yes | — | API base endpoint |
| `orgId` | Yes | — | Your organisation identifier |
| `gamificationWriteKey` | Yes\* | — | Gamification write key |
| `gamificationRegion` | Yes\* | — | Region value |
| `gamificationBaseUrl` | Yes\* | — | Override for the gamification API base URL |
| `brandId` | No | — | Brand identifier |
| `applicationId` | No | — | Application identifier |
| `source` | No | `WEBPUSH` | Source channel |
| `channelType` | No | `web` | Channel type |
| `sessionTimeoutMinutes` | No | `30` | Session timeout in minutes |
| `batchSize` | No | `50` | Event batch size |
| `debugLevel` | No | `NONE` | Debug log level |
| `notifications` | — | — | Push only (p.67): `{ vapidKey, serviceWorkerPath, messaging }`. Not listed in the source's config table |
| `firebaseConfig`, `remoteConfigKey` | **Do not pass** | — | Omitting them selects direct configuration (p.62) |

\* As written in the source. Gamification needs only `gamificationWriteKey` and `gamificationRegion`, and only if the client uses gamification. See the correction under Modules → Gamification.

> ⚠️ Gap: the source doesn't say who supplies `brandId` and `applicationId`, or which values to use. Ask a Capillary engineer.
