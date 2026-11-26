---
updatedAt: 2026-11-23T06:02:22.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Gamification (Experience+)

Add Capillary's Experience+ gamification campaigns and views to your Flutter app.

Gamification lets you show Floating Button and Popup campaigns, and embed banner, embed, and loyalty widgets directly as Flutter widgets. It requires the Gamification Key, Gamification Region, and Gamification Base Url from [Prerequisites](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#prerequisites), configured the same way as the base account details — see [HydraAccountConfig](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydraaccountconfig)/[HydraFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrafirebaseremoteconfigkeys) for setting them explicitly from Dart if you're on a multi-account setup.

# Screen tracking

Call [Hydra.gamificationScreenAppeared(screenName: ...)](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#7-gamification-screen-appeared-disappeared) when a gamification-related screen appears, and [Hydra.gamificationScreenDisappeared(screenName: ...)](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#7-gamification-screen-appeared-disappeared) when it disappears — pass the **same** `screenName` to both calls. Once a screen is reported, Floating Button, Popup, and Bottom Sheet campaigns targeted at that screen show automatically — no further implementation needed for these.

# Native widgets

Three Flutter widgets, backed by native `PlatformView`s:

* `GamificationBannerView({ required String bannerId, void Function(double height)? onHeightChanged })`
* `GamificationEmbedView({ required String embedId, void Function(double height)? onHeightChanged })`
* `GamificationLoyaltyView({ required String loyaltyId, void Function(double height)? onHeightChanged })` — call [Hydra.setCapToken(token: ...)](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#8-set-cap-token) **before mounting** it: the cap token is read once, when the view binds, so setting it afterwards doesn't reach a view that's already on screen.

All three widgets report their content height via `onHeightChanged`. A height of `0` is meaningful — the widget has nothing to show (no matching entry point, or the campaign closed it) — so collapse with it rather than ignoring it:

```dart
import 'package:capillary_hydra/hydra.dart';
import 'package:flutter/material.dart';

class GamificationSection extends StatefulWidget {
  const GamificationSection({super.key});
  @override
  State<GamificationSection> createState() => _GamificationSectionState();
}

class _GamificationSectionState extends State<GamificationSection> {
  double _bannerHeight = 300;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: _bannerHeight,
      child: GamificationBannerView(
        bannerId: 'your_banner_id',
        onHeightChanged: (height) {
          if (height >= 0) setState(() => _bannerHeight = height);
        },
      ),
    );
  }
}
```

# Suppressing campaigns

Call [Hydra.setGamificationSuppressed(suppressed: true)](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#9-gamification-suppression) to temporarily stop gamification campaigns from being shown (e.g. during checkout or onboarding), and `false` to allow them again. Check the current value with `Hydra.isGamificationSuppressed()`.

# Theme

Call [Hydra.setThemeMode(mode: ...)](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#10-theme-mode) with a [HydraThemeMode](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrathememode) to set the light/dark theme used by gamification UI.

# Gamification events

Events on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class):

* `onGamificationDeeplink`: a campaign asked the app to open a deep link. Route it in your navigation.
* `onGamificationEventTrigger`: a game or campaign triggered a named event, with a payload (e.g. reward unlocked).
* `onGamificationAnalyticsEvent`: analytics events from gamification UI, which you can forward to your own analytics tool.

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