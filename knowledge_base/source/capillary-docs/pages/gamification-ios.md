---
updatedAt: 2026-11-23T06:02:22.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Gamification (Experience+)

Add Capillary's Experience+ gamification campaigns and views to your iOS app.

HydraCore bundles **HydraGamification**, which lets you deliver Experience+ campaigns (floating buttons, popups, and bottom sheets) and embed optional gamification surfaces (banners, embedded views, and loyalty views) in your iOS app, without building any campaign UI yourself. This guide covers Swift (UIKit), SwiftUI, and Objective-C.

<Callout icon="📘" theme="info">
  ### SDK version

  Minimum SDK version: `1.10.6`
</Callout>

## How it works

Once gamification is configured, Capillary renders these surfaces automatically:

* **Floating button, popup, and bottom sheet campaigns**: appear automatically on any screen you report, based on campaign targeting rules configured in the Gamification dashboard. No additional UI code is required.
* **Banner, embedded, and loyalty views**: optional views you place in your own layout by providing a container and a campaign/entry-point ID.

## Configuration

Gamification needs three values: a write key, a region, and an optional base URL override. How you supply them depends on whether your app already uses Firebase Remote Config for SDK setup.

### Option A: Your app uses Firebase Remote Config

Add these three keys to your Firebase Remote Config, alongside your existing Hydra keys:

| Key                           | Required    | Description                                                                                              |
| ----------------------------- | ----------- | -------------------------------------------------------------------------------------------------------- |
| `hydra_gamification_key`      | Mandatory   | Gamification write key for your account.                                                                 |
| `hydra_gamification_region`   | Conditional | Region for the gamification service. Required unless `hydra_gamification_base_url` is provided.          |
| `hydra_gamification_base_url` | Conditional | Override base URL for the gamification service. Required unless `hydra_gamification_region` is provided. |

Fetch these values from Remote Config at runtime, then pass them into `HydraConfiguration` the same way as Option B below.

### Option B: Your app doesn't use Firebase Remote Config

Get these three values directly from the Capillary team when your app is registered, along with your account ID, base URL, SSL public key, and org ID:

* Gamification Key
* Gamification Region
* Gamification URL (Optional)

Pass them straight into `HydraConfiguration` as literal values instead of fetching them from Remote Config.

### Either way: pass the values to `HydraConfiguration`

```swift
do {
    let configuration = try HydraConfiguration(
        accountID: accountID,
        server: .genericServer(apiBaseURL, sslKey, retryDelays),
        orgID: orgID,
        gamificationWriteKey: writeKey,
        gamificationRegion: region,
        gamificationBaseURL: baseURL // Optional if gamificationRegion is provided
    )

    hydra = try Hydra.generate(with: configuration)
} catch let error {
    Logger.error(error.localizedDescription)
}
```

Hydra resolves the gamification endpoint in this order:

1. If `hydra_gamification_base_url` is set, it's used directly.
2. Otherwise, Hydra resolves the base URL from `hydra_gamification_region`.

`hydra_gamification_key` is always mandatory. Provide at least one of `hydra_gamification_region` or `hydra_gamification_base_url` under either option. HydraGamification stays disabled if neither is available.

**SwiftUI:** Use the exact same `HydraConfiguration` and `Hydra.generate(...)` code shown above under either option. There's no separate SwiftUI initializer. Call it once, for example from your `App` struct's `init()`.

**Objective-C:** `HydraConfiguration` and `Hydra.generate(...)` are Swift-only APIs. There's no Objective-C version of them. If your app is Objective-C, add a small Swift file to your project that runs this initialization once (most mixed Objective-C/Swift apps already have one for existing Hydra setup), and let your Objective-C code run after that file has executed. The rest of the gamification APIs on this page (screen reporting,`setCapToken`, and the banner/embed/loyalty views) do have direct Objective-C methods via `HydraGamificationUI`. It's only SDK initialization itself that requires this Swift bootstrap.

## Reporting screens

Report a screen when it appears and disappears so Capillary can target campaigns correctly. Call these from your view controller's existing lifecycle methods:

```swift
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)

    hydra.gamificationScreenAppeared("SampleScreenName")
}

override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)

    hydra.gamificationScreenDisappeared("SampleScreenName")
}
```

**SwiftUI**, use the view modifier instead, applied directly to the view:

```swift
SampleView()
    .gamificationScreen("SampleScreenName")
```

<Callout icon="📘" theme="info">
  ### Note

  The `gamificationScreen` modifier automatically reports screen appearance and disappearance. No manual lifecycle callbacks are required.
</Callout>

**Objective-C:**

```objectivec
- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];

    [HydraGamificationUI reportScreen:@"SampleScreenName"];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];

    [HydraGamificationUI reportScreenDisappeared:@"SampleScreenName"];
}
```

<Callout icon="📘" theme="info">
  ### Note

  Screen reporting is mandatory for screen-targeted campaigns. Campaign visibility and eligibility depend on the currently reported screen.
</Callout>

## Setting the B2B token

The loyalty view requires a short-lived Capillary B2B token. Set it before the view mounts, or its content won't display.

```swift
hydra.setCapToken(token)
```

**Objective-C:**

```objectivec
[HydraGamificationUI setCapToken:token];
```

## Embeddable views

For each view: pass a unique ID, register a height callback, and update your container's height dynamically when the callback fires.

### Banner view

```swift
hydra.gamificationBannerView(bannerId: BANNER_ID) { height in
    // Update your container's height constraint
}
```

**SwiftUI:**

```swift
GamificationBannerView(bannerId: BANNER_ID)
```

**Objective-C:**

```objectivec
UIView *banner = [HydraGamificationUI bannerViewWithBannerId:BANNER_ID
                                                     onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

### Embedded view

```swift
hydra.gamificationEmbedView(embedId: EMBED_ID) { height in
    // Update your container's height constraint
}
```

**SwiftUI:**

```swift
GamificationEmbedView(embedId: EMBED_ID)
```

**Objective-C:**

```objectivec
UIView *embed = [HydraGamificationUI embedViewWithEmbedId:EMBED_ID
                                                  onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

### Loyalty view

```swift
hydra.gamificationLoyaltyView(embedId: LOYALTY_ID) { height in
    // Update your container's height constraint
}
```

**SwiftUI:**

```swift
GamificationLoyaltyView(embedId: LOYALTY_ID)
```

**Objective-C:**

```objectivec
UIView *loyalty = [HydraGamificationUI loyaltyViewWithEmbedId:LOYALTY_ID
                                                      onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

<Callout icon="📘" theme="info">
  ### Note

  Call `hydra.setCapToken(token)` before mounting the loyalty view. Without a valid token, the view renders empty.
</Callout>

## Integration checklist

**Required:**

* Update to the minimum required Hydra iOS SDK version.
* Add `hydra_gamification_key`.
* Add `hydra_gamification_region` or `hydra_gamification_base_url` (at least one is required).
* Report screen names on appear and disappear.
* Set the Capillary token with `setCapToken` before rendering a loyalty view (required for the loyalty view specifically).

**Optional:**

* Add a banner view.
* Add an embedded view.
* Add a loyalty view.

**Result:** After completing the required steps, floating button, bottom sheet, and popup campaigns become automatically available in your app. If you also add the optional UI components, banner, embedded, and loyalty experiences can be displayed directly within your app screens.

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