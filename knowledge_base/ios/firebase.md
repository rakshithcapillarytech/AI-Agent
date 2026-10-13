---
platform: ios
config_mode: firebase
sdk_package: HydraCore   # HydraGamification is bundled inside HydraCore; repo named in the source: https://github.com/Capillary/hydra-ios-sdk-spm.git
sdk_version: 1.7.5-preprod.10   # "Minimum Required Version" for gamification (p.26)
modules_covered: [gamification]
modules_missing: [core, push, inapp, inbox_api, inbox_ui, visitor, multi_account]   # core = SDK install, Firebase setup, full init, sign-in/out, events: none of it is in the source
sources: ["Integration document _ Experience+ pp.25–37 (Experience+ iOS: Gamification iOS Integration Guide)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# iOS (with Firebase)

> **Read this first.** The only iOS source for Firebase mode is a **gamification add-on guide** (pp.25–37). It assumes the app **already integrates the Hydra iOS SDK**: the source says existing Hydra iOS users need no extra framework, because HydraGamification is bundled inside HydraCore and is switched on through configuration (p.26). The guide covers only how to turn gamification on. This file is filed under Firebase mode because the guide configures gamification through **Firebase Remote Config keys** (p.27).
>
> The **core iOS + Firebase integration is not documented** in the source. That means installing the SDK, Firebase setup, the full SDK initialisation, sign-in/sign-out, custom events, push (APNs / FCM), rich notifications (Notification Service Extension), Inbox and In-App. For any of these, escalate to a Capillary engineer. Don't fill the gap from `ios/direct.md` (that's a different mode) or from general iOS knowledge.

## Coverage
| Module | Status in this mode |
|---|---|
| Gamification: configuration, screen reporting, Capillary token, automatic campaigns, delegate callbacks, UI suppression, Banner / Embedded / Loyalty views | Documented in Swift (UIKit), SwiftUI and Objective-C. Delegate and suppression: Swift only |
| Core: SDK installation, Firebase project / Remote Config setup | **Not documented** |
| Core: SDK initialisation | **Partly documented.** Only the three gamification parameters of `HydraConfiguration` and a bare `Hydra.generate(with:)` call appear. The other arguments are elided as `...` in the source |
| Core: sign-in, sign-out, custom events | **Not documented** |
| Push notifications (APNs / FCM) | **Not documented** |
| Rich notifications (Notification Service Extension) | **Not documented** |
| In-App messaging | **Not documented** |
| Inbox / Notification Center | **Not documented** |
| Visitor flow, multi-account | **Not documented** |

> ⚠️ Gap: the core iOS integration in Firebase mode isn't in the source. That covers SDK installation, Firebase setup, the full `HydraConfiguration` arguments, sign-in/sign-out, custom events, push via APNs / FCM, the Notification Service Extension for rich notifications, Inbox and In-App. Ask a Capillary engineer.

## Requirements
- The app already integrates the Hydra iOS SDK. This is the guide's starting assumption (p.26).
- Hydra iOS SDK **`{{sdk_version}}` or later**. The source asks clients to "update to the latest Hydra iOS SDK version that includes HydraGamification support" and gives `{{sdk_version}}` as the minimum (p.26).
- Languages covered: Swift (UIKit), SwiftUI, Objective-C.

> ⚠️ Gap: the source doesn't state the minimum iOS deployment target, or the Xcode, Swift, Firebase SDK or CocoaPods versions. Ask a Capillary engineer before giving numbers.

> ⚠️ Source doc correction: this guide gives a minimum version of 1.7.5-preprod.10 (p.26) vs a required version of 1.7.5-preprod.12 (Beta for UAT/POC) in the iOS without-Firebase guide of the same document (p.91). It's unclear which version Firebase-mode clients should install. *Pending SME confirmation.*

## Prerequisites
See `_shared/prerequisites.md` for the common exchange, and `_shared/firebase-setup.md` for the Firebase project and Remote Config basics shared by every platform. This guide lists no prerequisites of its own. The registration exchange (bundle ID `{{bundle_id}}` ↔ Account Id, Base URL, SSL key …) belongs to the core integration, which isn't documented here.

For gamification, Capillary gives the client:
- Gamification Key: goes into `hydra_gamification_key` (step 2).
- Gamification Region: goes into `hydra_gamification_region` (step 2).
- Gamification Base URL (optional): goes into `hydra_gamification_base_url` (step 2).
- Banner / Embed / Loyalty entry-point IDs, if the client uses those views (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`).

> ⚠️ Gap: Firebase-side prerequisites aren't documented: the Firebase project, registering the iOS app in Firebase, and Remote Config access. Ask a Capillary engineer.

## Steps

> ⚠️ Gap: these steps start from an app that already has the Hydra iOS SDK integrated in Firebase mode. How to reach that starting point isn't documented. Ask a Capillary engineer.

### 1. Update to a Hydra iOS SDK version with gamification
Update the app to the latest Hydra iOS SDK version that includes HydraGamification support (p.26). No separate gamification framework is needed: HydraGamification is bundled inside HydraCore and is enabled through configuration.

Repository URL:

```text
https://github.com/Capillary/hydra-ios-sdk-spm.git
```

Minimum required version: `{{sdk_version}}`.

> ⚠️ Gap: the source doesn't say how to update (SPM, Xcode or CocoaPods), whether this repository is private, or what access or credentials it needs. Ask a Capillary engineer.

> ⚠️ Source doc correction: this guide names the repository `https://github.com/Capillary/hydra-ios-sdk-spm.git` (p.26) vs `https://github.com/Capillary/hydra-sdk-ios-packages` in the iOS without-Firebase guide of the same document (pp.89–91). It's unclear whether both repositories are valid, or which one applies to Firebase-mode apps. *Pending SME confirmation.*

### 2. Add the gamification configuration
Add these **Firebase Remote Config keys** (p.27). Key names are literal:

| Remote Config key | Value (from Capillary) | Required? |
|---|---|---|
| `hydra_gamification_key` | `{{gamification_key}}` | **Mandatory** |
| `hydra_gamification_region` | `{{gamification_region}}` | Either this or `hydra_gamification_base_url` must be provided |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Optional, as long as the region is provided |

Allowed region values are listed in `_shared/prerequisites.md`.

> ⚠️ Source doc correction: step 2 lists the key as `hydra_gamification_base_url ()` with empty parentheses (p.27) vs "`hydra_gamification_base_url` (Optional)" in the checklist (p.36). The checklist is consistent with the rule that either region or base URL must be provided. *Pending SME confirmation.*

Then configure Hydra with these values during SDK initialisation.

Swift:

```swift
let configuration = try HydraConfiguration(
    ...
    gamificationWriteKey: writeKey,   // value of hydra_gamification_key
    gamificationRegion: region,       // value of hydra_gamification_region
    gamificationBaseURL: baseURL      // value of hydra_gamification_base_url
)

let hydra = try Hydra.generate(with: configuration)
```

The `...` is in the source and stands for the app's existing `HydraConfiguration` arguments. This source doesn't list them.

- **SwiftUI:** configuration is identical to the Swift example.
- **Objective-C:** Hydra initialisation goes through the app's existing Swift bootstrap. No Objective-C initialisation API is given.

**How the gamification URL is resolved** (in priority order):
1. If `hydra_gamification_base_url` is provided, it is used as the gamification base URL.
2. Otherwise, Hydra resolves the base URL from `hydra_gamification_region`.

This lets existing integrations keep region-based configuration while supporting custom endpoints.

**Important** (from the source, p.28):
- `hydra_gamification_key` is mandatory.
- Either `hydra_gamification_region` or `hydra_gamification_base_url` must be provided.
- HydraGamification **stays disabled** if the required configuration is unavailable.

> ⚠️ Gap: the source says both "add the Remote Config keys" and "configure Hydra using these values during SDK initialization" (passing them to `HydraConfiguration`). It doesn't say whether the SDK reads these keys from Remote Config itself, or whether the app must fetch them from Remote Config and pass them in. It also doesn't give the Swift types of `writeKey` / `region` / `baseURL`, how to omit the optional base URL, or the value format in Remote Config. Ask a Capillary engineer.

### 3. Report the current screen
HydraGamification uses screen information to decide when and where to show campaigns. **Screen reporting is mandatory for screen-targeted campaigns.** Campaign visibility and eligibility depend on the currently reported screen.

Swift (UIKit), in each view controller:

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

SwiftUI, applied to the screen's view:

```swift
SampleView()
    .gamificationScreen("SampleScreenName")
```

The `gamificationScreen` modifier reports screen appearance and disappearance automatically. No manual lifecycle callbacks are needed.

Objective-C:

```objc
- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];

    [HydraGamificationUI reportScreen:@"SampleScreenName"];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];

    [HydraGamificationUI reportScreenDisappeared:@"SampleScreenName"];
}
```

`hydra` is the instance returned by `Hydra.generate(with:)` in step 2.

> ⚠️ Gap: the source doesn't say how screen names must match campaign configuration (naming rules or where they're set up), or which import Objective-C files need to use `HydraGamificationUI`. Ask a Capillary engineer.

### 4. Set the Capillary token (required for Loyalty View)
A new public API supports the Loyalty View. Set the Capillary B2B short-lived token **before** a Loyalty View is displayed. Where the token comes from is described in `_shared/prerequisites.md`.

Swift:

```swift
hydra.setCapToken(token)
```

SwiftUI:

```swift
hydra.setCapToken(token)
```

Objective-C:

```objc
[HydraGamificationUI setCapToken:token];
```

**Important** (from the source, p.30): the token must be set before the Loyalty View renders. Without a valid token, loyalty content may not appear.

## Modules

### Push
> ⚠️ Gap: not documented in the source. That includes APNs / FCM setup and rich notifications via a Notification Service Extension. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented in the source. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: neither the Inbox API nor the Inbox UI is documented in the source. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented in the source. Ask a Capillary engineer.

### Gamification

**Automatic experiences.** Once steps 1–4 are done, Hydra handles these campaign types with no extra code. It evaluates campaign eligibility and shows content when it applies.
- Floating Button campaigns
- Popup campaigns
- Bottom Sheet campaigns

**Optional: gamification delegate.** `HydraGamificationDelegate` gives the host app callbacks for:
- gamification lifecycle events
- campaign interactions
- analytics events
- deeplink requests
- event triggers

The source's implementation (Swift, UIKit):

```swift
// MARK: - Gamification Events

extension HydraBaseManager: HydraGamificationDelegate {

    func gamificationDidInitialize() {
        Logger.debug("[Gamification] initialized")
    }

    func gamificationDidFail(_ error: Error) {
        Logger.debug("[Gamification] failed: \(error)")
    }

    func gamificationDidLoadEntryPoints(
        _ entryPoints: [HydraGamificationEntryPoint]
    ) {
        Logger.debug(
            "[Gamification] entry points loaded: \(entryPoints.count)"
        )
    }

    func gamificationDidOpenCampaign(_ campaignId: String) {
        Logger.debug(
            "[Gamification] campaign opened: \(campaignId)"
        )
    }

    func gamificationDidCloseCampaign(_ campaignId: String) {
        Logger.debug(
            "[Gamification] campaign closed: \(campaignId)"
        )
    }

    func gamificationWidgetHeightChanged(
        entryPointId: String,
        height: CGFloat
    ) {
        Logger.debug(
            "[Gamification] widget height changed: \(height)"
        )
    }

    /// Web analytics events emitted from campaign content,
    /// such as BUTTON_CLICKED or PAGE_OPENED.
    func gamificationDidEmitAnalyticsEvent(
        _ name: String,
        payload: [String: Any]
    ) {
        Logger.debug(
            "[Gamification] analytics event from web: \(name), payload=\(payload)"
        )
    }

    /// Called when a campaign requests the host application
    /// to open a deeplink.
    ///
    /// HTTP/HTTPS links are handled by the SDK. The host application
    /// can handle app-specific custom-scheme deeplinks here.
    func gamificationRequestedDeeplink(_ url: String) {
        Logger.debug(
            "[Gamification] deeplink requested: \(url)"
        )

        if let url = URL(string: url) {
            UIApplication.shared.open(
                url,
                options: [:],
                completionHandler: nil
            )
        }
    }

    /// Called when a gamification event is triggered.
    func gamificationEventTrigger(
        eventName: String,
        info: [String: Any]
    ) {
        Logger.debug(
            "[Gamification] event triggered: \(eventName), info: \(info)"
        )
    }
}
```

> ⚠️ Gap: the source doesn't show how to register the delegate with Hydra (which property or method to set). It also doesn't say what `HydraBaseManager` and `Logger` are (SDK types or the sample app's own classes), or which delegate methods are required and which are optional. Ask a Capillary engineer.

> ⚠️ Gap: the source says HTTP/HTTPS links are handled by the SDK and the host handles custom-scheme deeplinks in `gamificationRequestedDeeplink(_:)`. Yet its sample opens every URL it receives with `UIApplication.shared.open`. It isn't stated whether this callback also fires for HTTP/HTTPS links. Ask a Capillary engineer.

**Gamification UI suppression** (Swift, UIKit). This API temporarily suppresses automatically presented gamification UI, such as floating action buttons, campaign popups and other auto-presented overlays:

```swift
/// Suppresses or resumes automatically presented gamification popups/overlays.
hydra.setGamificationSuppressed(true)
```

> ⚠️ Gap: the source only shows `true`. Its doc comment says the call "suppresses or resumes", which suggests `false` resumes, but that isn't stated explicitly. Ask a Capillary engineer. No SwiftUI or Objective-C variant is given.

**Optional: gamification UI components.** To show gamification content inside the app's own screens, use the views below. For each view:
1. Pass a unique ID.
2. Register a height callback.
3. Update the view height dynamically.

The IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`) are the entry-point IDs from Capillary (see `_shared/prerequisites.md`). The source writes them as constants (`BANNER_ID`, `EMBED_ID`, `LOYALTY_ID`) and doesn't state their type. In the UIKit / Objective-C samples, `bannerHeightConstraint` / `heightConstraint` are the host view's own height constraints.

*Banner View*

Swift (UIKit):

```swift
let bannerView = hydra.gamificationBannerView(
    bannerId: {{banner_id}}
) { height in
    self.bannerHeightConstraint.constant = height
}
```

SwiftUI:

```swift
GamificationBannerView(
    bannerId: {{banner_id}}
)
```

Objective-C:

```objc
UIView *banner =
[HydraGamificationUI bannerViewWithBannerId:{{banner_id}}
                                  onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

*Embedded View*

Swift:

```swift
let embedView = hydra.gamificationEmbedView(
    embedId: {{embed_id}}
) { height in
    self.heightConstraint.constant = height
}
```

SwiftUI:

```swift
GamificationEmbedView(
    embedId: {{embed_id}}
)
```

Objective-C:

```objc
UIView *embed =
[HydraGamificationUI embedViewWithEmbedId:{{embed_id}}
                                onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

*Loyalty View.* Set the Capillary token first (step 4). In the source, the Loyalty View's parameter label is `embedId:` / `EmbedId:`, not a loyalty-specific label. Keep it as shown.

Swift:

```swift
let loyaltyView = hydra.gamificationLoyaltyView(
    embedId: {{loyalty_id}}
) { height in
    self.heightConstraint.constant = height
}
```

SwiftUI:

```swift
GamificationLoyaltyView(
    embedId: {{loyalty_id}}
)
```

Objective-C:

```objc
UIView *loyalty =
[HydraGamificationUI loyaltyViewWithEmbedId:{{loyalty_id}}
                                  onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

## Verification
**Expected result** (from the source, pp.36–37): after the required steps, HydraGamification campaigns appear in the app automatically:
- Floating Buttons
- Bottom Sheets
- Popups

If the optional UI components were added, Banner, Embedded and Loyalty content also appears inside the app's screens.

**Delegate callbacks.** If the app implements `HydraGamificationDelegate`, these callbacks show gamification's state:
- `gamificationDidInitialize()`: gamification has initialised.
- `gamificationDidFail(_ error: Error)`: gamification reported a failure, with the error.
- `gamificationDidLoadEntryPoints(_:)`: entry points have loaded. The sample logs `entryPoints.count`.
- `gamificationDidOpenCampaign(_:)` / `gamificationDidCloseCampaign(_:)`: a campaign was opened or closed.

The `[Gamification] …` strings in the source sample are written by the sample's own `Logger.debug` calls. They are **not** SDK log lines.

**Required checklist** (from the source, p.36):
- Updated to the latest Hydra iOS SDK version (at least `{{sdk_version}}`).
- `hydra_gamification_region` added.
- `hydra_gamification_key` added.
- `hydra_gamification_base_url` added (optional).
- Screen names reported.
- Capillary token set with `setCapToken(...)` (required for Loyalty View).

Optional: Banner View, Embedded View, Loyalty View added.

> ⚠️ Gap: the source gives no formal verification procedure. There are no SDK log lines, no dashboard checks, and no documented way to register the delegate (see Modules → Gamification), so the callbacks above can't be relied on until an SME confirms the registration step. Ask a Capillary engineer.

## Known Issues

**Gamification never starts, and no campaigns appear at all**
- Cause: required configuration is missing. `hydra_gamification_key` is mandatory, and either `hydra_gamification_region` or `hydra_gamification_base_url` must be provided. Otherwise HydraGamification stays disabled.
- Fix: provide the key plus a region or base URL (step 2).

*From the source doc (p.28).*

**Screen-targeted campaigns don't appear**
- Cause: the current screen isn't reported. Campaign visibility and eligibility depend on the currently reported screen.
- Fix: report screens as in step 3.

*From the source doc (p.29).*

**Loyalty View shows no content**
- Cause: the Capillary B2B token wasn't set, or wasn't valid, before the Loyalty View rendered.
- Fix: call `setCapToken(...)` before rendering the Loyalty View (step 4).

*From the source doc (p.30).*

**A custom-scheme deeplink from a campaign does nothing**
- Cause: the SDK handles HTTP/HTTPS links. App-specific custom-scheme deeplinks are left to the host app.
- Fix: handle them in `gamificationRequestedDeeplink(_:)` of `HydraGamificationDelegate` (Modules → Gamification).

*From the source doc (p.32).*

## API Reference

**Configuration and initialisation**

| API | Purpose |
|---|---|
| `HydraConfiguration(..., gamificationWriteKey:, gamificationRegion:, gamificationBaseURL:)` | SDK configuration (`throws`). Only these three gamification arguments are documented; the rest are elided as `...` in the source |
| `Hydra.generate(with:)` | Creates the Hydra instance from the configuration (`throws`). Returns the `hydra` instance used below |

**Remote Config keys**

| Key | Meaning |
|---|---|
| `hydra_gamification_key` | Gamification write key (mandatory) |
| `hydra_gamification_region` | Gamification region. Used to resolve the endpoint when no base URL is set |
| `hydra_gamification_base_url` | Custom gamification base URL (optional). Takes priority over the region |

**Screen reporting**

| API | Purpose |
|---|---|
| `hydra.gamificationScreenAppeared(_:)` | Reports that a screen appeared (Swift, UIKit) |
| `hydra.gamificationScreenDisappeared(_:)` | Reports that a screen disappeared (Swift, UIKit) |
| `.gamificationScreen(_:)` | SwiftUI view modifier. Reports appearance and disappearance automatically |
| `[HydraGamificationUI reportScreen:]` | Reports that a screen appeared (Objective-C) |
| `[HydraGamificationUI reportScreenDisappeared:]` | Reports that a screen disappeared (Objective-C) |

**Capillary token and UI suppression**

| API | Purpose |
|---|---|
| `hydra.setCapToken(_:)` / `[HydraGamificationUI setCapToken:]` | Sets the Capillary B2B short-lived token for the Loyalty View |
| `hydra.setGamificationSuppressed(_:)` | Suppresses or resumes automatically presented gamification UI (Swift) |

**Gamification views**

| API | Purpose |
|---|---|
| `hydra.gamificationBannerView(bannerId:) { height in … }` | Banner view with a height callback (Swift, UIKit) |
| `GamificationBannerView(bannerId:)` | Banner view (SwiftUI) |
| `[HydraGamificationUI bannerViewWithBannerId:onHeight:]` | Returns a `UIView *` banner (Objective-C) |
| `hydra.gamificationEmbedView(embedId:) { height in … }` | Embedded view with a height callback (Swift) |
| `GamificationEmbedView(embedId:)` | Embedded view (SwiftUI) |
| `[HydraGamificationUI embedViewWithEmbedId:onHeight:]` | Returns a `UIView *` embedded view (Objective-C) |
| `hydra.gamificationLoyaltyView(embedId:) { height in … }` | Loyalty view with a height callback (Swift) |
| `GamificationLoyaltyView(embedId:)` | Loyalty view (SwiftUI) |
| `[HydraGamificationUI loyaltyViewWithEmbedId:onHeight:]` | Returns a `UIView *` loyalty view (Objective-C) |

**`HydraGamificationDelegate` methods**

| Method | Called when |
|---|---|
| `gamificationDidInitialize()` | Gamification has initialised |
| `gamificationDidFail(_ error: Error)` | Gamification reported a failure |
| `gamificationDidLoadEntryPoints(_ entryPoints: [HydraGamificationEntryPoint])` | Entry points have loaded |
| `gamificationDidOpenCampaign(_ campaignId: String)` | A campaign was opened |
| `gamificationDidCloseCampaign(_ campaignId: String)` | A campaign was closed |
| `gamificationWidgetHeightChanged(entryPointId: String, height: CGFloat)` | A widget's height changed |
| `gamificationDidEmitAnalyticsEvent(_ name: String, payload: [String: Any])` | Campaign web content emitted an analytics event, such as `BUTTON_CLICKED` or `PAGE_OPENED` |
| `gamificationRequestedDeeplink(_ url: String)` | A campaign asks the host app to open a deeplink. The SDK handles HTTP/HTTPS; the host handles custom schemes |
| `gamificationEventTrigger(eventName: String, info: [String: Any])` | A gamification event was triggered |
