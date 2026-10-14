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

> ⚠️ Gap: the only iOS Firebase-mode source is a **gamification add-on guide**. It assumes the Hydra iOS SDK is already integrated and only turns gamification on (via Firebase Remote Config keys). The **core iOS + Firebase integration is not documented**: SDK install, Firebase setup, full `HydraConfiguration` arguments, sign-in/sign-out, custom events, push (APNs / FCM), Notification Service Extension, Inbox, In-App. Don't fill these from `ios/direct.md` or general iOS knowledge. Ask a Capillary engineer.

## Coverage
| Module | Status |
|---|---|
| Gamification: config, screen reporting, Capillary token, auto campaigns, Banner / Embedded / Loyalty views | Documented (Swift UIKit, SwiftUI, Objective-C) |
| Gamification delegate, UI suppression | Documented (Swift only) |
| Core: install, Firebase setup, sign-in/out, events | Not documented |
| Core: initialisation | Partial: only the three gamification arguments (rest elided as `...`) |
| Push, rich notifications, In-App, Inbox, Visitor, multi-account | Not documented |

## Requirements
- An app that already integrates the Hydra iOS SDK.
- Hydra iOS SDK `{{sdk_version}}` or later (the latest version that includes HydraGamification).
- Swift (UIKit), SwiftUI or Objective-C.

> ⚠️ Gap: minimum iOS deployment target and Xcode / Swift / Firebase SDK / CocoaPods versions aren't documented. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` and `_shared/firebase-setup.md`. Capillary gives the client the Gamification Key, Gamification Region, Gamification Base URL (optional), and Banner / Embed / Loyalty entry-point IDs if those views are used.

> ⚠️ Gap: iOS Firebase setup (project, app registration, Remote Config) isn't documented. Ask a Capillary engineer.

## Steps

### 1. Update to a Hydra iOS SDK version with gamification
Update to the latest Hydra iOS SDK version that includes HydraGamification. No extra framework is needed: HydraGamification is bundled inside HydraCore and enabled through configuration.

Repository URL:

```text
https://github.com/Capillary/hydra-ios-sdk-spm.git
```

Minimum required version: `{{sdk_version}}`.

> ⚠️ Gap: the docs disagree on repo and version. This guide: `https://github.com/Capillary/hydra-ios-sdk-spm.git`, minimum 1.7.5-preprod.10 (p.26). iOS without-Firebase guide: `https://github.com/Capillary/hydra-sdk-ios-packages`, required 1.7.5-preprod.12 (pp.89–91). How to install and get repo access isn't stated. Ask a Capillary engineer.

### 2. Add the gamification configuration
Add these Firebase Remote Config keys:

| Key | Value | Required |
|---|---|---|
| `hydra_gamification_key` | `{{gamification_key}}` | Mandatory |
| `hydra_gamification_region` | `{{gamification_region}}` | This or the base URL |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Optional |

> ⚠️ Correction: ✅ Use the key name `hydra_gamification_base_url` (optional, as in the checklist, p.36). ❌ Don't use `hydra_gamification_base_url ()` with empty parentheses (key list, p.27). *Pending SME confirmation.*

Then configure Hydra with these values during SDK initialisation (Swift; SwiftUI is identical; Objective-C apps initialise through their existing Swift bootstrap):

```swift
let configuration = try HydraConfiguration(
    ...
    gamificationWriteKey: writeKey,   // hydra_gamification_key
    gamificationRegion: region,       // hydra_gamification_region
    gamificationBaseURL: baseURL      // hydra_gamification_base_url
)

let hydra = try Hydra.generate(with: configuration)
```

`...` stands for the app's existing `HydraConfiguration` arguments (not listed in the source). Region values: see `_shared/prerequisites.md`.

**URL resolution:** if `hydra_gamification_base_url` is provided it is used; otherwise Hydra resolves the base URL from `hydra_gamification_region`.

**Rules:** `hydra_gamification_key` is mandatory; either region or base URL must be provided; otherwise HydraGamification stays disabled.

> ⚠️ Gap: whether the SDK reads these keys from Remote Config itself or the app fetches and passes them in isn't stated; nor are argument types or how to omit the base URL. Ask a Capillary engineer.

### 3. Report the current screen
Mandatory for screen-targeted campaigns: campaign visibility and eligibility depend on the reported screen.

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

SwiftUI (the modifier reports appear/disappear automatically):

```swift
SampleView()
    .gamificationScreen("SampleScreenName")
```

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

### 4. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** a Loyalty View renders; without a valid token, loyalty content may not appear. Token source: `_shared/prerequisites.md`.

Swift / SwiftUI:

```swift
hydra.setCapToken(token)
```

Objective-C:

```objc
[HydraGamificationUI setCapToken:token];
```

## Modules

### Push
> ⚠️ Gap: not documented (APNs / FCM, Notification Service Extension). Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: Inbox API and UI not documented. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented. Ask a Capillary engineer.

### Gamification
**Automatic experiences.** Once configured, Hydra shows Floating Button, Popup and Bottom Sheet campaigns with no extra code.

**Optional: `HydraGamificationDelegate`** gives callbacks for lifecycle events, campaign interactions, analytics events, deeplink requests and event triggers. Swift (UIKit):

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

> ⚠️ Gap: how to register the delegate with Hydra isn't shown, nor whether `HydraBaseManager` and `Logger` are SDK types or sample-app classes. Ask a Capillary engineer.

**UI suppression** (Swift, UIKit) temporarily suppresses auto-presented gamification UI (floating action buttons, campaign popups, other overlays):

```swift
/// Suppresses or resumes automatically presented gamification popups/overlays.
hydra.setGamificationSuppressed(true)
```

> ⚠️ Gap: only `true` is shown; resuming (presumably `false`) isn't stated. Ask a Capillary engineer.

**Optional UI components.** For each view: pass a unique ID, register a height callback, update the view height dynamically. The IDs are entry-point IDs from Capillary; the height constraints are the host view's own.

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

*Loyalty View* (set the token first, step 4; the parameter label is `embedId:` as shown)

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
- **Result:** Floating Buttons, Bottom Sheets and Popups appear automatically; Banner, Embedded and Loyalty content appears where those views were added.
- **Delegate (if registered):** `gamificationDidInitialize()` = ready; `gamificationDidFail(_:)` = failed. `[Gamification] …` strings come from the sample's own `Logger.debug`, not the SDK.
- **Checklist:** SDK at least `{{sdk_version}}`; the three Remote Config keys added (base URL optional); screens reported; `setCapToken(...)` for Loyalty View. Optional: Banner, Embedded, Loyalty views.

> ⚠️ Gap: no SDK log lines or dashboard checks are documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| No gamification at all | Key missing, or neither region nor base URL set | Provide key + region or base URL (step 2) |
| Screen-targeted campaigns don't appear | Current screen not reported | Report screens (step 3) |
| Loyalty View shows no content | Token missing or invalid before render | Call `setCapToken(...)` first (step 4) |
| Custom-scheme campaign deeplink does nothing | SDK handles only HTTP/HTTPS | Handle it in `gamificationRequestedDeeplink(_:)` |

## API Reference
| API | Purpose |
|---|---|
| `HydraConfiguration(..., gamificationWriteKey:, gamificationRegion:, gamificationBaseURL:)` | SDK config (`throws`) |
| `Hydra.generate(with:)` | Creates the `hydra` instance (`throws`) |
| `hydra.gamificationScreenAppeared(_:)` / `gamificationScreenDisappeared(_:)` | Screen reporting (Swift) |
| `.gamificationScreen(_:)` | Screen reporting (SwiftUI modifier) |
| `[HydraGamificationUI reportScreen:]` / `reportScreenDisappeared:` | Screen reporting (Objective-C) |
| `hydra.setCapToken(_:)` / `[HydraGamificationUI setCapToken:]` | Capillary B2B token for Loyalty View |
| `hydra.setGamificationSuppressed(_:)` | Suppress / resume auto-presented gamification UI (Swift) |
| `hydra.gamificationBannerView(bannerId:)` / `GamificationBannerView(bannerId:)` / `bannerViewWithBannerId:onHeight:` | Banner (Swift / SwiftUI / ObjC) |
| `hydra.gamificationEmbedView(embedId:)` / `GamificationEmbedView(embedId:)` / `embedViewWithEmbedId:onHeight:` | Embedded (Swift / SwiftUI / ObjC) |
| `hydra.gamificationLoyaltyView(embedId:)` / `GamificationLoyaltyView(embedId:)` / `loyaltyViewWithEmbedId:onHeight:` | Loyalty (Swift / SwiftUI / ObjC) |

`HydraGamificationDelegate` methods (signatures in Modules → Gamification):

| Method | Called when |
|---|---|
| `gamificationDidInitialize()` / `gamificationDidFail(_:)` | Initialised / failed |
| `gamificationDidLoadEntryPoints(_:)` | Entry points loaded |
| `gamificationDidOpenCampaign(_:)` / `gamificationDidCloseCampaign(_:)` | Campaign opened / closed |
| `gamificationWidgetHeightChanged(entryPointId:height:)` | Widget height changed |
| `gamificationDidEmitAnalyticsEvent(_:payload:)` | Campaign web content emitted an analytics event (e.g. `BUTTON_CLICKED`) |
| `gamificationRequestedDeeplink(_:)` | Campaign asks the host to open a deeplink (host handles custom schemes) |
| `gamificationEventTrigger(eventName:info:)` | Gamification event triggered |
