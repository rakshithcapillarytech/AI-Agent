---
updatedAt: 2026-11-23T06:02:22.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Gamification (Experience+)

Add Capillary's Experience+ gamification campaigns, entry points, and loyalty embeds to your Web app.

Gamification auto-renders campaigns and entry points (icon buttons, modals, banners, embeds) after user signin; configured entirely from the gamification dashboard.

When gamification is enabled, the SDK fetches campaigns and entry points from the gamification platform after every `identify()` call and renders them automatically. No additional host-app code is needed — except for two inline embed containers that require a hook element in your HTML.

# Configuration

`gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` are all required together for gamification features to work — obtain all three from the Capillary team. `gamificationRegion` derives the API base URL automatically.

When all three are present, the SDK automatically initializes gamification after every `identify()` call — no additional host-app code is needed. Campaigns and entry points are fetched and rendered automatically.

Opt-in: if all three fields are absent, the gamification module is silently skipped and the rest of the SDK works as normal.

* **Remote Config bootstrap** — `gamificationWriteKey`, `gamificationRegion`, and `gamificationBaseUrl` come from Remote Config — do not pass them in `HydraSDK.initialize()`. Add them to your Remote Config JSON. See [Configure Firebase — Step 3](https://docs.capillarytech.com/docs/configure-firebase-web#step-3-set-up-remote-config).
* **Direct-config bootstrap** — pass all three fields directly in the `initialize()` call instead — same field names, same behavior.

See [Initialise SDK — Configuration Reference](https://docs.capillarytech.com/docs/web-sdk-initialisation#configuration-reference) for the full field table.

# Containers

Containers control where and how an entry point appears. Six types are supported, all configured from the gamification dashboard:

| Container          | Behavior                                                                                                                 | Host HTML required                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **ICON\_BUTTON**   | Fixed-position button (160×160 px) that slides up from the bottom-left corner of the page. Tapping it opens a CHAT\_BOX. | No — appended to `document.body` automatically                      |
| **CHAT\_BOX**      | Fixed-position panel (360×580 px) that appears above the icon button.                                                    | No — appended to `document.body` automatically                      |
| **POP\_UP**        | Centered full-page modal with a semi-transparent backdrop. Max size 1000×740 px.                                         | No — appended to `document.body` automatically                      |
| **BOTTOM\_SHEET**  | Sheet that slides up from the bottom of the screen with a backdrop. Height is configured in the gamification dashboard.  | No — appended to `document.body` automatically                      |
| **EMBEDDED**       | Full-width inline block injected into a host-provided hook `<div>`. Waits for the element to appear (SPA-safe).          | **Yes** — place `<div id="{hookId}"></div>` at the desired position |
| **NATIVE\_BANNER** | Block-level inline injection — same behavior as EMBEDDED.                                                                | **Yes** — place `<div id="{hookId}"></div>` at the desired position |

<Callout icon="📘" theme="info">
  ### EMBEDDED / NATIVE_BANNER setup

  Place a `<div>` with the `id` matching the `hookId` configured in the gamification dashboard. The SDK uses a `MutationObserver` to wait for these elements, so they are SPA-safe — they do not need to exist at page load.

  ```html
  
  <div id="your_hook_id"></div>
  ```
</Callout>

# Campaign display rules — URL path targeting

Each entry point in the gamification dashboard can be configured with include/exclude URL path rules. The SDK evaluates these rules against the current page URL on every route change — SPA navigation is handled automatically via `MutationObserver`, no code changes required in your application.

Path-segment rules are the default format — a plain, `/`-delimited list of path segments matched anywhere in the URL, plus escape hatches for exact-URL and regex matching:

| Format                         | Example                                | Matches                                                                                                                                            |
| ------------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Every page**                 | `*` or `/*`                            | Matches unconditionally                                                                                                                            |
| **Root only**                  | `/` (or any all-slash rule, e.g. `//`) | The exact root path only — not "match everything"                                                                                                  |
| **Path segment(s)**            | `product`, `dashboard/vouchers`        | Those segments as a contiguous run anywhere in the path or SPA hash route (see below). No substring matching — `product` never matches `products`. |
| **Path segment(s) + wildcard** | `product/*`, `dashboard/vouchers/*`    | Same as above, requiring at least one further child segment                                                                                        |
| **Exact URL**                  | `https://example.com/cart`             | Only that exact URL (query/hash stripped) — **must include an explicit `http://`/`https://` scheme**                                               |
| **URL wildcard**               | `https://example.com/cart/*`           | That path and all sub-paths, requiring a child segment (`/cart/*` will not match `/cartoons`)                                                      |
| **Regex literal**              | `/\/cart$/i`                           | Any URL whose path matches the pattern                                                                                                             |

# Content types

Content types control what gets rendered inside a container. Eleven types are supported — all configured from the gamification dashboard, no host-app code required:

| Content type              | What it renders                                     | Use case                                                         |
| ------------------------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| **CAMPAIGN**              | Iframe loading a campaign URL matched by conditions | Gamified campaign screens, mini-games                            |
| **WALLET**                | Iframe loading the default wallet URL               | Points / rewards wallet view                                     |
| **NUDGE**                 | Iframe loading a direct URL                         | Contextual prompts and announcements                             |
| **PROGRAM**               | Iframe loading `{base}/program/?campaignId={id}`    | Loyalty program enrollment and status                            |
| **REWARD**                | Iframe loading `{base}/reward/?rewardUserId={id}`   | Redemption and reward claim flows                                |
| **STATIC**                | Image (`<img>`) with a click action                 | Banners and promotional images that trigger another content type |
| **DYNAMIC**               | Native progress circle card                         | Live campaign progress indicator (activity count, expiry, step)  |
| **DYNAMIC\_MULTISTEP\_1** | Native progress bar card                            | Single-bar step progress with title and body                     |
| **DYNAMIC\_MULTISTEP\_2** | Native multi-step progress meter                    | Step circles with connectors, header image, and CTA button       |
| **DYNAMIC\_MULTISTEP\_3** | Native collapsible accordion                        | Sticky header with expandable step content and CTA               |
| **ACCEPT\_GUARD**         | Native acceptance modal                             | Streak / program enrollment card before a campaign opens         |

# Game and CMS event payloads

Experience+ sends the following events for game and CMS interactions. This section covers seven events (five game events and two CMS events): what each event is, when it fires, which attributes it carries, and a sample payload. It also describes how event fields map to the event-creation fields.

* `cuid` is **required** on every event. All other attributes are optional.
* `event_name` identifies the event and is always sent.
* Payloads are flat JSON with no nested objects. Numbers are sent as numbers, not strings.
* While creating the events, map the fields as described in [Field mapping](#field-mapping) (`cuid` → `customerId`, `identifierType`, `source`, `accountId`).

| #  | Flow | Event name       | When it fires                                                                                       |
| :- | :--- | :--------------- | :-------------------------------------------------------------------------------------------------- |
| 1  | Game | `game_open`      | A game entry surface opens or launches the game (pop-up, floating icon, modal, or embedded banner). |
| 2  | Game | `game_viewed`    | The game UI is rendered and actually visible to the user.                                           |
| 3  | Game | `game_played`    | The user makes the first real interaction with the game (spin, scratch, tap, or select).            |
| 4  | Game | `game_completed` | The game ends: won, lost, completed, or abandoned.                                                  |
| 5  | Game | `reward_seen`    | The user views the reward (reveal screen or wallet).                                                |
| 6  | CMS  | `content_open`   | A CMS surface is opened or displayed (widget, banner, or full page).                                |
| 7  | CMS  | `content_viewed` | The CMS content is rendered and visible.                                                            |

## game\_open

**Flow:** Game

**Fires when:** A game entry surface opens or launches the game (pop-up, floating icon, modal, or embedded banner).

| Attribute              | Type   | Required | Example                | Description                                                                                                                                                       |
| :--------------------- | :----- | :------- | :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`                 | string | Yes      | `stringxxx`            | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event.                                 |
| `event_name`           | string | Yes      | `game_open`            | Event identifier.                                                                                                                                                 |
| `campaign_id`          | string | No       | `camp_44`              | Game instance ID. Join key across game and reward events.                                                                                                         |
| `game_type`            | string | No       | `spinthewheel`         | Which game was opened. *Values include: spinthewheel, scratchcard, slotmachine, quiz, memorygame, giftbox, streak, multistep, referral (list is not exhaustive).* |
| `entry_surface`        | string | No       | `popup`                | Which surface opened the game. *Values: popup, floating\_icon, modal, banner\_embedded.*                                                                          |
| `embed_id`             | string | No       | `home_hero`            | For banner\_embedded only: which placement or slot the banner sat in.                                                                                             |
| `entry_point_id`       | string | No       | `ep_12`                | Entry-point identifier.                                                                                                                                           |
| `entry_point_location` | string | No       | `home_screen`          | Where in the app the entry surface appeared.                                                                                                                      |
| `deep_link_url`        | string | No       | `/home`                | Which screen the user needs to open.                                                                                                                              |
| `hyper_link_url`       | string | No       | `https://your-url.com` | External URL to be opened.                                                                                                                                        |

**Sample payload**

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

## game\_viewed

**Flow:** Game

**Fires when:** The game UI is rendered and actually visible to the user.

| Attribute      | Type   | Required | Example        | Description                                                                                                                       |
| :------------- | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`         | string | Yes      | `stringxxx`    | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`   | string | Yes      | `game_viewed`  | Event identifier.                                                                                                                 |
| `campaign_id`  | string | No       | `camp_44`      | Join key across game and reward events.                                                                                           |
| `game_type`    | string | No       | `spinthewheel` | Segment views by game type. Same values as game\_open.                                                                            |
| `load_time_ms` | number | No       | `850`          | Render or load time in milliseconds.                                                                                              |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_viewed",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "load_time_ms": 850
}
```

## game\_played

**Flow:** Game

**Fires when:** The user makes the first real interaction with the game (spin, scratch, tap, or select).

| Attribute     | Type   | Required | Example        | Description                                                                                                                       |
| :------------ | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`        | string | Yes      | `stringxxx`    | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`  | string | Yes      | `game_played`  | Event identifier.                                                                                                                 |
| `campaign_id` | string | No       | `camp_44`      | Join key across game and reward events.                                                                                           |
| `game_type`   | string | No       | `spinthewheel` | Segment plays by game type. Same values as game\_open.                                                                            |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_played",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel"
}
```

## game\_completed

**Flow:** Game

**Fires when:** The game ends: won, lost, completed, or abandoned.

| Attribute       | Type   | Required | Example          | Description                                                                                                                       |
| :-------------- | :----- | :------- | :--------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`          | string | Yes      | `stringxxx`      | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`    | string | Yes      | `game_completed` | Event identifier.                                                                                                                 |
| `campaign_id`   | string | No       | `camp_44`        | Join key across game and reward events.                                                                                           |
| `game_type`     | string | No       | `spinthewheel`   | Segment completions by game type. Same values as game\_open.                                                                      |
| `total_time_ms` | number | No       | `8200`           | Total play duration from start to finish, in milliseconds.                                                                        |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_completed",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "total_time_ms": 8200
}
```

## reward\_seen

**Flow:** Game

**Fires when:** The user views the reward (reveal screen or wallet).

| Attribute     | Type   | Required | Example       | Description                                                                                                                          |
| :------------ | :----- | :------- | :------------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`        | string | Yes      | `stringxxx`   | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event.    |
| `event_name`  | string | Yes      | `reward_seen` | Event identifier.                                                                                                                    |
| `reward_id`   | string | No       | `rew_88`      | Reward ID. Join key for the reward.                                                                                                  |
| `campaign_id` | string | No       | `camp_44`     | Source game that issued the reward.                                                                                                  |
| `reward_type` | string | No       | `points`      | Segment by reward type. *Values include: points, coupons, cashback, discount, freebie, buyXgetY, noReward (list is not exhaustive).* |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "reward_seen",
  "reward_id": "rew_88",
  "campaign_id": "camp_44",
  "reward_type": "points"
}
```

## content\_open

**Flow:** CMS

**Fires when:** A CMS surface is opened or displayed (widget, banner, or full page).

| Attribute         | Type   | Required | Example        | Description                                                                                                                       |
| :---------------- | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`            | string | Yes      | `stringxxx`    | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`      | string | Yes      | `content_open` | Event identifier.                                                                                                                 |
| `content_surface` | string | No       | `full_page`    | Which CMS surface opened. *Values: widget, banner, full\_page.*                                                                   |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "content_open",
  "content_surface": "full_page"
}
```

## content\_viewed

**Flow:** CMS

**Fires when:** The CMS content is rendered and visible.

| Attribute         | Type   | Required | Example          | Description                                                                                                                       |
| :---------------- | :----- | :------- | :--------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`            | string | Yes      | `stringxxx`      | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`      | string | Yes      | `content_viewed` | Event identifier.                                                                                                                 |
| `page_id`         | string | No       | `page_9`         | Page ID. Join key for the CMS page.                                                                                               |
| `content_surface` | string | No       | `full_page`      | Segment views by surface. *Values: widget, banner, full\_page.*                                                                   |
| `load_time_ms`    | number | No       | `700`            | Load time in milliseconds; helps catch slow or empty loads.                                                                       |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "content_viewed",
  "page_id": "page_9",
  "content_surface": "full_page",
  "load_time_ms": 700
}
```

## Field mapping

When creating the events, map the event fields to the event-creation fields below. All four are required.

| Event-creation field | Maps from                       | Required | Notes                                                                                         |
| :------------------- | :------------------------------ | :------- | :-------------------------------------------------------------------------------------------- |
| `customerId`         | `cuid` (from the event payload) | Yes      | `cuid` on every event must be mapped to `customerId` when creating the events.                |
| `identifierType`     | Identifier passed to the SDK    | Yes      | Set based on what is passed to the SDK as the login identifier: mobile, email, or externalId. |
| `source`             | SDK                             | Yes      | Map `source` to SDK.                                                                          |
| `accountId`          | SDK account ID                  | Yes      | Map to the SDK account ID.                                                                    |

# Loyalty embeds

Loyalty embeds are a separate rendering layer that runs independently of the entry-point/campaign system. When gamification is enabled, the Campaigns API may return a `loyaltyUrls` array alongside campaigns. The SDK renders each loyalty URL as an iframe into a host-provided placeholder element.

## Host HTML setup

Place a `<div>` with an `id` matching the `embedId` value provided by the Capillary team wherever you want the embed to appear:

```html
<div id="loyalty_widget"></div>
```

The SDK calls `document.getElementById(embedId)` at render time and appends an `<iframe>` to the matching element. If the element is not found, that embed is silently skipped.

## Capillary token (required for authenticated loyalty views)

The loyalty iframes require a short-lived Capillary token to display user-specific content. Set it after user login:

```javascript
// After the user logs in and you have a fresh token
sdkService.setCapToken("short-lived-cap-token");

// Read back the current token if needed
const token = sdkService.getCapToken(); // string | null
```

The token is:

* Appended automatically as `?capToken=<value>` to every loyalty iframe URL
* Persisted in IndexedDB (survives page reload — no need to set it again unless it expires)
* Cleared on `reset()` / logout

Call `setCapToken` whenever your app refreshes the token — it triggers an immediate re-render of all loyalty embeds.

Add `setCapToken` and `getCapToken` to your SDK service file:

```typescript
// In your sdkService.ts
setCapToken(token: string) {
  HydraSDK.setCapToken(token);
}

getCapToken(): string | null {
  return HydraSDK.getCapToken();
}
```

## Theme, Suppression & Callbacks — Host App Examples

These examples use the gamification wrappers from the SDK service file on [Initialise SDK](https://docs.capillarytech.com/docs/web-sdk-initialisation). `sdkService` must be initialized first: calling these methods before `initialize()` throws.

**Why the service file keeps its own copy in localStorage:** the SDK saves the theme and suppression state and restores them after a reload, but only once its async initialization finishes. Until then, `isGamificationSuppressed()` returns `false`, and there is no getter for the theme. If your UI shows either value (a theme picker, a "pause campaigns" toggle), seed it from `getSavedTheme()` / `getSavedGamificationSuppressed()` so it's correct on first render. If your UI never displays these values, the localStorage copy is optional.

### Theme — follow your app's theme setting

```javascript
import { useState } from "react";
import type { Theme } from "cap-hydra-web-sdk";
import { sdkService } from "./services/sdkService";

export function ThemePicker() {
  // Seed from the saved copy so the picker is right immediately after a reload
  const [theme, setTheme] = useState<Theme>(() => sdkService.getSavedTheme());

  const onChange = (value: Theme) => {
    setTheme(value);
    sdkService.setTheme(value); // applies to campaigns opened from now on
  };

  return (
    <select value={theme} onChange={(e) => onChange(e.target.value as Theme)}>
      <option value="NONE">Default</option>
      <option value="AUTO">System</option>
      <option value="LIGHT">Light</option>
      <option value="DARK">Dark</option>
    </select>
  );
}
```

If your app already has its own theme setting, call `sdkService.setTheme()` from that toggle instead, mapping light → `LIGHT`, dark → `DARK`, system → `AUTO`. A campaign already on screen keeps its current look. If your app has no dark mode, skip `setTheme()` entirely; the default `NONE` renders campaigns unchanged.

### Suppression — pause overlay campaigns

```javascript
import { useState } from "react";
import { sdkService } from "./services/sdkService";

export function CampaignToggle() {
  // Not isGamificationSuppressed(): it reads false until SDK init finishes after a reload
  const [suppressed, setSuppressed] = useState(() =>
    sdkService.getSavedGamificationSuppressed(),
  );

  const onChange = (value: boolean) => {
    setSuppressed(value);
    sdkService.setGamificationSuppressed(value);
  };

  return (
    <label>
      <input
        type="checkbox"
        checked={suppressed}
        onChange={(e) => onChange(e.target.checked)}
      />
      Pause campaigns
    </label>
  );
}
```

* Suppression blocks pop-ups, bottom sheets, chat boxes and icon buttons. Embeds, banners and loyalty embeds keep rendering, but clicks inside them can't open an overlay.

### Callbacks — react to gamification events

Register the hooks once in the service file, right after `HydraSDK.initialize()`. A later call replaces the earlier hooks rather than adding to them, so keep all hooks in one object. Deep links are forwarded as a window event so your router can handle them without the service file depending on it:

```javascript
// In sdkService.ts
export const DEEP_LINK_EVENT = "hydra-deep-link";

export const sdkService = new SDKService();
sdkService.initialize();

sdkService.setGamificationCallback({
  onInitSuccess: () => console.log("Gamification ready"),
  onInitFailure: (error) =>
    console.error("Gamification init failed", error.code, error.message),
  onEntryPointsLoaded: (entryPoints) =>
    console.log("Entry points loaded", entryPoints.length),
  onCampaignOpened: (campaignId) => console.log("Campaign opened", campaignId),
  onCampaignClosed: (campaignId) => console.log("Campaign closed", campaignId),
  onAnalyticsEvent: (data) => console.log("Gamification analytics", data),
  onDeepLinkEvent: (data) => {
    window.dispatchEvent(
      new CustomEvent(DEEP_LINK_EVENT, { detail: data.deepLink }),
    );
  },
  onGameEventTrigger: (eventName, data) =>
    console.log("No campaign configured for event", eventName, data.reason),
});
```

Then route the deep link in your app (React Router example):

```javascript
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { DEEP_LINK_EVENT } from "./services/sdkService";

export function useGamificationDeepLinks() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleDeepLink = (event: Event) => {
      const deepLink = (event as CustomEvent<unknown>).detail;
      if (typeof deepLink !== "string" || !deepLink) return;

      if (deepLink.startsWith("/")) {
        navigate(deepLink); // in-app path
      } else if (/^https?:\/\//i.test(deepLink)) {
        window.location.assign(deepLink); // web URL
      } else {
        navigate("/"); // e.g. a mobile-app scheme with no web equivalent
      }
    };

    window.addEventListener(DEEP_LINK_EVENT, handleDeepLink);
    return () => window.removeEventListener(DEEP_LINK_EVENT, handleDeepLink);
  }, [navigate]);
}
```

* Replace the `console` calls with your own logging or analytics. Every hook is optional, so register only the ones you need.
* Hooks fire only once gamification is enabled and a user has signed in with `identify()`.
* Call `sdkService.setGamificationCallback(null)` to stop receiving events.

<br />