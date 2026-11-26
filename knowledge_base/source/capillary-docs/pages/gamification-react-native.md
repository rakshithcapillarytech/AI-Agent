---
updatedAt: 2026-11-23T06:02:22.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Gamification (Experience+)

Show gamification campaigns and views in your React Native app.

Gamification lets you show Floating Button, Popup, and Bottom Sheet campaigns, add banner, embed, and loyalty widgets in your app, and track screen views against gamification entry points.

It requires the Gamification Key, Gamification Region, and Gamification Base Url. For details, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started). You configure them through the initialiser that you set up in [Installing iOS SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-ios-sdk) and [Installing Android SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-android-sdk).

<Callout icon="⚠️" theme="warn">
  ### Android: pass an FCM token

  If `enable_hydra_sdk_firebase_registration` is `false`, because your app owns FCM or because you are [using Hydra without Firebase](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#using-hydra-without-firebase), call [HydraPushNotification.passFCMToken(token)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#pass-fcm-token-android-only) after the SDK initializes. Otherwise, Gamification doesn't work properly. If you don't have a real FCM token, a dummy token is fine.
</Callout>

## Reporting screens

Call [Hydra.gamificationScreenAppeared(screenName)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#gamification-screen-appeared-and-disappeared) when a gamification-related screen appears, and `Hydra.gamificationScreenDisappeared(screenName)` when it disappears. Pass the same `screenName` to both calls.

```javascript
Hydra.gamificationScreenAppeared('HomeScreen');
// ... later, when the screen unmounts:
Hydra.gamificationScreenDisappeared('HomeScreen');
```

After you report a screen, the SDK automatically shows the Floating Button, Popup, and Bottom Sheet campaigns that target that screen. You don't need to add any other code for these campaigns.

## Handling the height of gamification views

Subscribe to [addGamificationViewHeightChangedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-the-height-of-a-gamification-view-changes) on `HydraNativeEventEmitter` to be notified when the height of a banner, embed, or loyalty view changes.

## Suppressing campaigns

To temporarily stop gamification campaigns from showing, for example during checkout or onboarding, call [Hydra.setGamificationSuppressed(true)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#gamification-suppression). Call it with `false` to allow campaigns again. To check the current value, call `Hydra.isGamificationSuppressed()`.

## Setting the theme

Call [Hydra.setThemeMode(mode)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#theme-mode) with a [ThemeMode](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#thememode) value to set the light or dark theme that Hydra's UI uses.

## Gamification events

Register the following listeners on `HydraNativeEventEmitter`:

* [addGamificationDeeplinkListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-gamification-requests-a-deep-link): A campaign asked the app to open a deep link. Route it in your navigation.
* [addGamificationEventTriggerListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-a-gamification-event-is-triggered): A game or campaign triggered a named event with a payload, for example a reward unlocked.
* [addGamificationAnalyticsEventListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-for-gamification-analytics-events): Analytics events from the gamification UI, which you can forward to your own analytics tool.

## Game and CMS event payloads

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

### game\_open

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

### game\_viewed

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

### game\_played

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

### game\_completed

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

### reward\_seen

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

### content\_open

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

### content\_viewed

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

### Field mapping

When creating the events, map the event fields to the event-creation fields below. All four are required.

| Event-creation field | Maps from                       | Required | Notes                                                                                         |
| :------------------- | :------------------------------ | :------- | :-------------------------------------------------------------------------------------------- |
| `customerId`         | `cuid` (from the event payload) | Yes      | `cuid` on every event must be mapped to `customerId` when creating the events.                |
| `identifierType`     | Identifier passed to the SDK    | Yes      | Set based on what is passed to the SDK as the login identifier: mobile, email, or externalId. |
| `source`             | SDK                             | Yes      | Map `source` to SDK.                                                                          |
| `accountId`          | SDK account ID                  | Yes      | Map to the SDK account ID.                                                                    |

## Embeddable views

Three React Native view components embed gamification surfaces directly in your app:

| Component                 | Prop        | Type   |
| ------------------------- | ----------- | ------ |
| `GamificationBannerView`  | `bannerId`  | string |
| `GamificationEmbedView`   | `embedId`   | string |
| `GamificationLoyaltyView` | `loyaltyId` | string |

`GamificationLoyaltyView` requires you to call [Hydra.setCapToken(token)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#set-cap-token) first, before you show the view.

Banner and embed views should size themselves dynamically with `addGamificationViewHeightChangedListener`, not with a fixed height, because the content height can vary. A height of `0` means the view has nothing to show, for example when no matching entry point exists yet. Collapse the container instead of ignoring it. If the entry point becomes available later, for example after `identify`, the SDK emits a new non-zero height.

```tsx
import { useEffect, useState } from 'react';
import { GamificationBannerView, GamificationEmbedView, GamificationLoyaltyView, HydraNativeEventEmitter } from '@capillarytech/react-native-hydra-lib';

const BANNER_ID = 'your_banner_id';
const EMBED_ID = 'your_embed_id';
const LOYALTY_ID = 'your_loyalty_id';

const [bannerHeight, setBannerHeight] = useState(300);
const [embedHeight, setEmbedHeight] = useState(600);
const [loyaltyHeight, setLoyaltyHeight] = useState(600);

useEffect(() => {
  const subscription = HydraNativeEventEmitter.getInstance().addGamificationViewHeightChangedListener(
    (height, entryPointId) => {
      if (height < 0) return; // 0 is meaningful: collapse the view
      if (entryPointId === BANNER_ID) setBannerHeight(height);
      else if (entryPointId === EMBED_ID) setEmbedHeight(height);
      else if (entryPointId === LOYALTY_ID) setLoyaltyHeight(height);
    }
  );
  return () => HydraNativeEventEmitter.getInstance().removeListener(subscription);
}, []);

<GamificationBannerView bannerId={BANNER_ID} style={{ width: '100%', height: bannerHeight }} />
<GamificationEmbedView embedId={EMBED_ID} style={{ width: '100%', height: embedHeight }} />
<GamificationLoyaltyView loyaltyId={LOYALTY_ID} style={{ width: '100%', height: loyaltyHeight }} />
```

<Callout icon="⚠️" theme="warn">
  ### Important

  When you use Gamification together with Hydra push notifications, use [HydraPushNotification.openExternalUrl(url)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#open-external-url) instead of React Native's `Linking.openURL(url)` to open external links. We've observed issues with external links when using Gamification, and strongly recommend using this API.
</Callout>