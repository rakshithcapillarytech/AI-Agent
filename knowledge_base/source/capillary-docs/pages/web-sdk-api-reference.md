---
updatedAt: 2026-11-17T06:02:49.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# API Reference for Event Tracking, Notifications, and User Lifecycle

Reference for every public method on the Capillary Web SDK.

These methods are all static and accessed via `HydraSDK.*`. All methods except `initialize()` internally wait for SDK initialization to complete before executing.

# API Quick Reference

| Method                                       | Description                                                                                                            |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `HydraSDK.initialize(config)`                | Initialize the SDK singleton. Call once at module load time.                                                           |
| `HydraSDK.track(eventName, properties?)`     | Track a custom behavioral event.                                                                                       |
| `HydraSDK.pageView(options?)`                | Track a page view. Auto-captures URL and title if no arguments.                                                        |
| `HydraSDK.identify(params)`                  | Identify a user. Use `USER_REGISTER` for login/signup; `USER_UPDATE` for profile changes only.                         |
| `HydraSDK.getAnonymousId()`                  | Returns the backend-assigned anonymous visitor ID, or `null`. Available regardless of auth state.                      |
| `HydraSDK.reset()`                           | Sign out user and return to anonymous tracking. Call on logout.                                                        |
| `HydraSDK.enableSDK()`                       | Re-enable tracking after disable.                                                                                      |
| `HydraSDK.disableSDK()`                      | Disable tracking. New events dropped; queued events preserved in IndexedDB.                                            |
| `HydraSDK.setCapToken(token)`                | Set Capillary token for loyalty embeds; appended to iframe URLs; persisted in IndexedDB; triggers immediate re-render. |
| `HydraSDK.getCapToken()`                     | Returns the current Capillary token, or `null` if not set.                                                             |
| `HydraSDK.setGamificationSuppressed(value)`  | Suppress (`true`) or resume (`false`) overlay campaigns.                                                               |
| `HydraSDK.isGamificationSuppressed()`        | Returns the current suppression state. Defaults to `false`.                                                            |
| `HydraSDK.enablePagePathTracking(enabled)`   | Toggle automatic (default) vs. manual screen/path detection for gamification display rules.                            |
| `HydraSDK.onScreenChanged(screenName)`       | Report the current screen when path tracking is manual — call on every navigation.                                     |
| `HydraSDK.setTheme(theme)`                   | Set the gamification theme: `NONE` (default), `LIGHT`, `DARK`, or `AUTO`.                                              |
| `HydraSDK.setGamificationCallback(callback)` | Register hooks for gamification lifecycle events (init, campaign opened/closed, deep links, etc.). `null` to clear.    |

# Initialization

### `initialize(config)`

| Parameter | Type             | Required | Description                                                                                                                                  |
| --------- | ---------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `config`  | `HydraSDKConfig` | Yes      | SDK configuration object — see [Configuration Reference](https://docs.capillarytech.com/docs/web-sdk-initialisation#configuration-reference) |

Returns: `HydraSDK` instance. Safe to call more than once — a later call returns the existing instance rather than re-initializing.

# Event Tracking

### `track()` — custom events

```javascript
sdkService.trackEvent("test_event", { source: "smoke_test" });
```

| Parameter    | Type                      | Required | Description             |
| ------------ | ------------------------- | -------- | ----------------------- |
| `eventName`  | `string`                  | Yes      | Name of the event       |
| `properties` | `Record<string, unknown>` | No       | Custom event properties |

Returns: `void` (fire-and-forget)

### `pageView()` — page views

```javascript
sdkService.trackPageView();
```

Call on every route change. No arguments = auto-captures the current URL and title.

| Parameter | Type              | Required | Description        |
| --------- | ----------------- | -------- | ------------------ |
| `options` | `PageViewOptions` | No       | Page view metadata |

`PageViewOptions` fields:

| Field           | Type                      | Description                                              |
| --------------- | ------------------------- | -------------------------------------------------------- |
| `page_url`      | `string`                  | Override the current page URL                            |
| `page_title`    | `string`                  | Override the current page title                          |
| `referrer`      | `string`                  | Override the page referrer                               |
| `page_category` | `string`                  | Page category (e.g. `'blog'`, `'product'`, `'checkout'`) |
| `properties`    | `Record<string, unknown>` | Custom properties                                        |

Returns: `void` (fire-and-forget)

# User Identity

### `identify()`

```javascript
sdkService.identifyUser("email", "testuser@example.com", "USER_REGISTER", {
  firstName: "Test",
  lastName: "User",
});
```

| Parameter | Type             | Required | Description         |
| --------- | ---------------- | -------- | ------------------- |
| `params`  | `IdentifyParams` | Yes      | Identity parameters |

`IdentifyParams` fields:

| Field        | Type                               | Required | Description                                                                  |
| ------------ | ---------------------------------- | -------- | ---------------------------------------------------------------------------- |
| `identifier` | `Identifier`                       | Yes      | User identifier (`type` + `cuid`)                                            |
| `actionType` | `'USER_REGISTER' \| 'USER_UPDATE'` | Yes      | `USER_REGISTER` for login and signup; `USER_UPDATE` for profile updates only |
| `traits`     | `IdentifyTraits`                   | No       | User profile attributes                                                      |

`Identifier` fields:

| Field  | Type                                  | Description                |
| ------ | ------------------------------------- | -------------------------- |
| `type` | `'email' \| 'mobile' \| 'externalId'` | How the user is identified |
| `cuid` | `string`                              | The identifier value       |

### `traits` fields

| Field        | Type                      | Description                                      |
| ------------ | ------------------------- | ------------------------------------------------ |
| `firstName`  | `string`                  | First name                                       |
| `lastName`   | `string`                  | Last name                                        |
| `gender`     | `string`                  | Gender                                           |
| `birthday`   | `string`                  | Birthday                                         |
| `city`       | `string`                  | City                                             |
| `country`    | `string`                  | Country                                          |
| `timezone`   | `string`                  | Timezone                                         |
| `email`      | `string`                  | Email                                            |
| `mobile`     | `string`                  | Mobile                                           |
| `externalId` | `string`                  | External ID                                      |
| `custom`     | `Record<string, unknown>` | Additional custom attributes, merged into events |

Returns: `void` (fire-and-forget)

### `identify()` parameter notes

| Parameter        | Value           | When to use                         |
| ---------------- | --------------- | ----------------------------------- |
| `actionType`     | `USER_REGISTER` | Login **and** signup                |
| `actionType`     | `USER_UPDATE`   | Profile updates only                |
| `identifierType` | `"email"`       | User identified by email            |
| `identifierType` | `"mobile"`      | User identified by phone number     |
| `identifierType` | `"externalId"`  | User identified by your internal ID |

## `getAnonymousId()`

Returns: `string | null` — the visitor ID, or `null` if not yet resolved. Works regardless of identification state.

## `reset()` — logout

```javascript
sdkService.reset();
```

Returns: `void` (fire-and-forget). Signs the user out and returns the SDK to anonymous tracking.

# Cookie Consent

### `enableSDK()` / `disableSDK()`

```javascript
sdkService.disableTracking(); // Events dropped
sdkService.enableTracking(); // Queued events resume
```

`enableSDK()` returns: `void`. Re-enables tracking after a disable — queued events resume processing.

`disableSDK()` returns: `void`. Disables tracking — new `track()`/`pageView()` events are dropped; already-queued events are preserved and resume once re-enabled. Does not affect `identify()`, `reset()`, or gamification events.

Persist the consent decision in your own storage and restore it by calling `enableTracking()` / `disableTracking()` on app load.

# Loyalty

### `setCapToken()` / `getCapToken()`

See [Configure Gamification — Loyalty embeds](https://docs.capillarytech.com/docs/gamification-web#loyalty-embeds) for full usage.

| Parameter | Type     | Required | Description                                      |
| --------- | -------- | -------- | ------------------------------------------------ |
| `token`   | `string` | Yes      | Short-lived Capillary token for the current user |

`setCapToken(token)` returns: `void`. The token is:

* Appended automatically as `?capToken=<value>` to every loyalty iframe URL
* Persisted in IndexedDB (survives page reload — no need to set it again unless it expires)
* Cleared on `reset()` / logout

`getCapToken()` returns: `string | null`

# Gamification

### `setGamificationSuppressed(value)`

| Parameter | Type      | Required | Description                           |
| --------- | --------- | -------- | ------------------------------------- |
| `value`   | `boolean` | Yes      | `true` to suppress, `false` to resume |

Returns: `void`. Affects overlay-style containers only (`POP_UP`, `BOTTOM_SHEET`, `CHAT_BOX`, `ICON_BUTTON`). While suppressed, an overlay never opens, whatever the trigger:

* a screen/path match
* an `ACTION_EVENT` trigger from `track()`
* a click inside a banner, embed, or loyalty embed that would open an overlay
* **Enabling suppression closes any overlay already open** (firing `onCampaignClosed`). A game in progress inside a closed overlay loses unsaved progress.
* `EMBEDDED`, `NATIVE_BANNER`, and Loyalty embeds keep rendering (and stay open) regardless of this setting. Only the overlays they would open are blocked.

### `isGamificationSuppressed()`

Returns: `boolean` — the current suppression state. Defaults to `false`. Right after a page reload this returns `false` until SDK initialization finishes, even if suppression was saved as on. To seed UI on first render, use the host-side copy described in [Theme, Suppression & Callbacks — Host App Examples](https://docs.capillarytech.com/docs/gamification-web#theme-suppression--callbacks--host-app-examples).

### `enablePagePathTracking(enabled)`

| Parameter | Type      | Required | Description                                                       |
| --------- | --------- | -------- | ----------------------------------------------------------------- |
| `enabled` | `boolean` | Yes      | `true` for automatic path detection (default), `false` for manual |

Returns: `void`. Switch to manual mode if your app's routing doesn't produce a real URL change (e.g. a native-shell webview, or custom router state) — call `onScreenChanged()` yourself on every navigation instead.

### `onScreenChanged(screenName)`

| Parameter    | Type     | Required | Description                   |
| ------------ | -------- | -------- | ----------------------------- |
| `screenName` | `string` | Yes      | The current screen/route name |

Returns: `void`. Only takes effect when path tracking is in manual mode; has no effect while automatic mode is active.

### `setTheme(theme)`

| Parameter | Type                                    | Required | Description            |
| --------- | --------------------------------------- | -------- | ---------------------- |
| `theme`   | `'NONE' \| 'AUTO' \| 'DARK' \| 'LIGHT'` | Yes      | The gamification theme |

Returns: `void`. Appends a `darkMode=true`/`darkMode=false` query param to every campaign and loyalty embed URL loaded after the call, so the hosted content can theme itself.

| Value   | Behavior                                                                                                                                                           |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `NONE`  | Default. No theme applied — `darkMode` is omitted from URLs and everything renders as before.                                                                      |
| `LIGHT` | Forces light mode (`darkMode=false`).                                                                                                                              |
| `DARK`  | Forces dark mode (`darkMode=true`).                                                                                                                                |
| `AUTO`  | Follows the browser's `prefers-color-scheme`, checked each time something renders. A system change applies to the next campaign opened, not one already on screen. |

### `setGamificationCallback(callback)`

| Parameter  | Type                           | Required | Description                               |
| ---------- | ------------------------------ | -------- | ----------------------------------------- |
| `callback` | `GamificationCallback \| null` | Yes      | The hooks to register, or `null` to clear |

Returns: `void`. Registers host-facing hooks for gamification events. All hooks are optional. Safe to call immediately after `initialize()`; hooks start firing once gamification is enabled and a user has signed in.

```javascript
HydraSDK.setGamificationCallback({
  onInitSuccess: () => console.log("gamification ready"),
  onCampaignOpened: (campaignId) => console.log("opened", campaignId),
  onDeepLinkEvent: (data) => router.push(data.deepLink as string),
});
```

| Hook                  | Signature                                                    | Fires when                                                                                                            |
| --------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `onInitSuccess`       | `() => void`                                                 | Gamification initializes successfully                                                                                 |
| `onInitFailure`       | `(error: GamificationError) => void`                         | Gamification initialization fails                                                                                     |
| `onEntryPointsLoaded` | `(entryPoints: EntryPoint[]) => void`                        | Entry points load on initialization and again on every background resync                                              |
| `onCampaignOpened`    | `(campaignId: string) => void`                               | A campaign actually becomes visible (for embeds and banners, only once the hook element is found on the page)         |
| `onCampaignClosed`    | `(campaignId: string) => void`                               | A campaign that fired `onCampaignOpened` closes — always paired 1:1 with it                                           |
| `onAnalyticsEvent`    | `(data: unknown) => void`                                    | Campaign content sends an analytics message (raw payload)                                                             |
| `onDeepLinkEvent`     | `(data: Record<string, unknown>) => void`                    | Campaign content requests a deep link — fires before any navigation the SDK performs                                  |
| `onGameEventTrigger`  | `(eventName: string, data: Record<string, unknown>) => void` | `track()` fires an event with no `ACTION_EVENT` entry point configured — `data` is `{ reason: 'NO_GAME_CONFIGURED' }` |

`GamificationCallback` and `Theme` are exported from `cap-hydra-web-sdk`.

<br />